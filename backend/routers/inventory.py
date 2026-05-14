"""Inventory router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.inventory import Inventory
from backend.models.item import Item
from backend.schemas import InventoryResponse

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.get("", response_model=list[InventoryResponse])
def list_inventory(db: Session = Depends(get_db)):
    return db.query(Inventory).all()


@router.get("/{item_id}")
def get_item_stock(item_id: str, db: Session = Depends(get_db)):
    inv = db.query(Inventory).filter(Inventory.item_id == item_id).first()
    if not inv:
        raise HTTPException(404, "Inventory record not found")
    item = db.query(Item).filter(Item.item_id == item_id).first()
    return {
        "inventory": InventoryResponse.model_validate(inv),
        "item_name": item.name if item else None,
        "category": item.category if item else None,
        "criticality": item.criticality if item else None,
        "stock_status": "critical" if inv.current_stock <= inv.reorder_level else "ok",
        "days_until_stockout": round(inv.current_stock / max(0.1, inv.daily_consumption_normal), 1),
    }
