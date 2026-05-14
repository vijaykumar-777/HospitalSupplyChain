from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.ai_predictions_log import AIPredictionsLog
from backend.models.order import Order
from backend.models.item import Item
from backend.models.supplier import Supplier
from backend.models.inventory import Inventory
from backend.schemas import AIPredictionLogResponse
from backend.services.ai_service import predict_delivery_delay

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])

def _recheck_orders_task(db: Session):
    orders = db.query(Order).filter(Order.status.in_(["pending", "in_transit"])).all()
    for order in orders:
        item = db.query(Item).filter(Item.item_id == order.item_id).first()
        supplier = db.query(Supplier).filter(Supplier.supplier_id == order.supplier_id).first()
        inv = db.query(Inventory).filter(Inventory.item_id == order.item_id).first()
        if not item or not supplier:
            continue
            
        context = {
            "order_id": order.order_id,
            "supplier": {"name": supplier.name, "city": supplier.city, "reliability": supplier.reliability_score, "avg_lead_days": supplier.avg_lead_days},
            "item": {"name": item.name, "category": item.category, "criticality": item.criticality},
            "order_quantity": order.quantity,
            "inventory": {"current_stock": inv.current_stock if inv else 0, "reorder_level": inv.reorder_level if inv else 0},
            "season": "current_season"
        }
        try:
            predict_delivery_delay(db, context)
        except Exception as e:
            print(f"Recheck error for order {order.order_id}: {e}")

@router.get("/log", response_model=list[AIPredictionLogResponse])
def get_prediction_log(db: Session = Depends(get_db)):
    return db.query(AIPredictionsLog).order_by(AIPredictionsLog.created_at.desc()).limit(100).all()

@router.post("/recheck-all")
def recheck_all_pending(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Triggers AI re-prediction on all pending orders."""
    background_tasks.add_task(_recheck_orders_task, db)
    return {"status": "ok", "message": "Re-prediction triggered for pending orders"}
