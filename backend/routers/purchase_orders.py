"""Purchase Orders router."""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.purchase_order import PurchaseOrder
from backend.schemas import POResponse, PORejectRequest

router = APIRouter(prefix="/api/purchase-orders", tags=["Purchase Orders"])


@router.get("", response_model=list[POResponse])
def list_purchase_orders(db: Session = Depends(get_db)):
    return db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc()).all()


@router.get("/{po_id}", response_model=POResponse)
def get_purchase_order(po_id: str, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.po_id == po_id).first()
    if not po:
        raise HTTPException(404, "Purchase order not found")
    return po


@router.patch("/{po_id}/approve", response_model=POResponse)
def approve_po(po_id: str, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.po_id == po_id).first()
    if not po:
        raise HTTPException(404, "Purchase order not found")
    po.approval_status = "approved"
    po.approval_date = datetime.now()
    po.approved_by = "Admin"
    db.commit()
    db.refresh(po)
    return po


@router.patch("/{po_id}/reject", response_model=POResponse)
def reject_po(po_id: str, payload: PORejectRequest, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.po_id == po_id).first()
    if not po:
        raise HTTPException(404, "Purchase order not found")
    po.approval_status = "rejected"
    db.commit()
    db.refresh(po)
    return po
