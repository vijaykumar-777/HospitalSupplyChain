"""Orders router — CRUD + prediction trigger."""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.order import Order
from backend.models.purchase_order import PurchaseOrder
from backend.models.item import Item
from backend.models.supplier import Supplier
from backend.models.inventory import Inventory
from backend.models.ai_predictions_log import AIPredictionsLog
from backend.schemas import OrderCreate, OrderResponse, OrderStatusUpdate
from backend.services.ai_service import predict_delivery_delay

router = APIRouter(prefix="/api/orders", tags=["Orders"])

def _trigger_prediction(db: Session, order: Order, item: Item):
    supplier = db.query(Supplier).filter(Supplier.supplier_id == order.supplier_id).first()
    inv = db.query(Inventory).filter(Inventory.item_id == order.item_id).first()
    
    context = {
        "order_id": order.order_id,
        "supplier": {"name": supplier.name, "city": supplier.city, "reliability": supplier.reliability_score, "avg_lead_days": supplier.avg_lead_days},
        "item": {"name": item.name, "category": item.category, "criticality": item.criticality},
        "order_quantity": order.quantity,
        "inventory": {"current_stock": inv.current_stock if inv else 0, "reorder_level": inv.reorder_level if inv else 0},
        "season": "current_season" # placeholder
    }
    
    # In real app, the DB session should be thread-local or managed cleanly for background tasks
    # We pass context here to be executed
    try:
        res = predict_delivery_delay(db, context)
        # We could update the order if it's delayed, etc.
    except Exception as e:
        print(f"Prediction error: {e}")

@router.post("", response_model=OrderResponse)
def create_order(payload: OrderCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create order → auto-creates draft PO."""
    order = Order(
        order_id=str(uuid.uuid4()),
        item_id=payload.item_id,
        supplier_id=payload.supplier_id,
        quantity=payload.quantity,
        order_date=datetime.now(),
        expected_delivery_date=payload.expected_delivery_date,
        status="pending",
        is_emergency_order=payload.is_emergency_order,
    )
    db.add(order)

    # Auto-create draft PO
    item = db.query(Item).filter(Item.item_id == payload.item_id).first()
    unit_price_est = 50.0  # placeholder — real price comes from supplier catalog
    po = PurchaseOrder(
        po_id=str(uuid.uuid4()),
        po_number=f"PO-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:5].upper()}",
        order_id=order.order_id,
        raised_by="System",
        approval_status="pending_approval",
        budget_code=f"AUTO-{datetime.now().strftime('%Y')}-Q{(datetime.now().month - 1) // 3 + 1}",
        payment_terms="NET30",
        payment_status="pending",
        total_value_inr=round(payload.quantity * unit_price_est, 2),
    )
    db.add(po)
    db.commit()
    db.refresh(order)
    
    # Trigger prediction in background
    background_tasks.add_task(_trigger_prediction, db, order, item)
    
    return order


@router.get("", response_model=list[OrderResponse])
def list_orders(
    status: Optional[str] = Query(None),
    supplier_id: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    if supplier_id:
        q = q.filter(Order.supplier_id == supplier_id)
    return q.order_by(Order.order_date.desc()).offset(offset).limit(limit).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@router.get("/{order_id}/prediction")
def get_order_prediction(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    
    prediction = db.query(AIPredictionsLog).filter(
        AIPredictionsLog.order_id == order_id,
        AIPredictionsLog.prediction_type == "delivery_delay"
    ).order_by(AIPredictionsLog.created_at.desc()).first()
    
    if not prediction:
        return {"status": "pending", "message": "No prediction available yet for this order"}
    return prediction.output_payload

@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: str, payload: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")
    order.status = payload.status
    db.commit()
    db.refresh(order)
    return order
