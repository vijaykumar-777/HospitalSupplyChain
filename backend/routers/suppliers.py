"""Suppliers router."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc
from backend.database import get_db
from backend.models.supplier import Supplier
from backend.models.delivery_history import DeliveryHistory
from backend.models.item import Item
from backend.schemas import SupplierResponse

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])


@router.get("", response_model=list[SupplierResponse])
def list_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).all()


@router.get("/alternates")
def get_alternate_suppliers(item_id: str = Query(...), db: Session = Depends(get_db)):
    """Return ranked alternate suppliers for a given item."""
    item = db.query(Item).filter(Item.item_id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    suppliers = db.query(Supplier).all()
    results = []
    for s in suppliers:
        cats = s.supply_categories if isinstance(s.supply_categories, list) else []
        if item.category in cats:
            results.append({
                "supplier_id": s.supplier_id,
                "name": s.name,
                "city": s.city,
                "reliability_score": s.reliability_score,
                "avg_lead_days": s.avg_lead_days,
                "is_emergency_certified": s.is_emergency_certified,
            })

    results.sort(key=lambda x: (-x["reliability_score"], x["avg_lead_days"]))
    return results


@router.get("/{supplier_id}")
def get_supplier_detail(supplier_id: str, db: Session = Depends(get_db)):
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(404, "Supplier not found")

    # Delivery stats
    deliveries = db.query(DeliveryHistory).filter(DeliveryHistory.supplier_id == supplier_id).all()
    total = len(deliveries)
    on_time = sum(1 for d in deliveries if d.delay_days is not None and d.delay_days <= 0)
    avg_delay = sum(d.delay_days for d in deliveries if d.delay_days and d.delay_days > 0) / max(1, total)

    return {
        "supplier": SupplierResponse.model_validate(supplier),
        "stats": {
            "total_deliveries": total,
            "on_time_count": on_time,
            "on_time_rate": round(on_time / max(1, total), 2),
            "avg_delay_days": round(avg_delay, 1),
        },
    }
