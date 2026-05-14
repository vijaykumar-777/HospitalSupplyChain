"""Goods Receipt Notes router."""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.goods_receipt_note import GoodsReceiptNote
from backend.models.order import Order
from backend.models.inventory import Inventory
from backend.schemas import GRNCreate, GRNResponse

router = APIRouter(prefix="/api/grn", tags=["Goods Receipt Notes"])


@router.post("", response_model=GRNResponse)
def create_grn(payload: GRNCreate, db: Session = Depends(get_db)):
    """Record goods receipt — updates inventory if accepted."""
    order = db.query(Order).filter(Order.order_id == payload.order_id).first()
    if not order:
        raise HTTPException(404, "Order not found")

    grn = GoodsReceiptNote(
        grn_id=str(uuid.uuid4()),
        grn_number=f"GRN-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:5].upper()}",
        order_id=payload.order_id,
        po_id=payload.po_id,
        received_date=datetime.now(),
        received_by=payload.received_by,
        inspected_by=payload.inspected_by,
        ordered_qty=order.quantity,
        received_qty=payload.received_qty,
        accepted_qty=payload.accepted_qty,
        rejected_qty=payload.rejected_qty,
        quality_status=payload.quality_status,
        rejection_reason=payload.rejection_reason,
        added_to_inventory=payload.quality_status != "rejected",
        batch_number=payload.batch_number,
        expiry_date=payload.expiry_date,
    )
    db.add(grn)

    # Update inventory if accepted
    if payload.quality_status != "rejected":
        inv = db.query(Inventory).filter(Inventory.item_id == order.item_id).first()
        if inv:
            inv.current_stock = min(inv.max_capacity, inv.current_stock + payload.accepted_qty)
            inv.last_updated = datetime.now()

    # Update order status
    order.status = "delivered"
    db.commit()
    db.refresh(grn)
    return grn


@router.get("", response_model=list[GRNResponse])
def list_grns(db: Session = Depends(get_db)):
    return db.query(GoodsReceiptNote).order_by(GoodsReceiptNote.created_at.desc()).all()


@router.get("/{grn_id}", response_model=GRNResponse)
def get_grn(grn_id: str, db: Session = Depends(get_db)):
    grn = db.query(GoodsReceiptNote).filter(GoodsReceiptNote.grn_id == grn_id).first()
    if not grn:
        raise HTTPException(404, "GRN not found")
    return grn


@router.get("/order/{order_id}", response_model=list[GRNResponse])
def get_grn_by_order(order_id: str, db: Session = Depends(get_db)):
    return db.query(GoodsReceiptNote).filter(GoodsReceiptNote.order_id == order_id).all()
