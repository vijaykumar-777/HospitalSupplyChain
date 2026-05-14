"""Goods Receipt Note model."""
import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class GoodsReceiptNote(Base):
    __tablename__ = "goods_receipt_notes"

    grn_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    grn_number = Column(String(50), nullable=False, unique=True)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=False)
    po_id = Column(String, ForeignKey("purchase_orders.po_id"), nullable=False)
    received_date = Column(DateTime, nullable=False)
    received_by = Column(String(200), nullable=False)
    inspected_by = Column(String(200), nullable=False)
    ordered_qty = Column(Integer, nullable=False)
    received_qty = Column(Integer, nullable=False)
    accepted_qty = Column(Integer, nullable=False)
    rejected_qty = Column(Integer, nullable=False)
    quality_status = Column(String(50), nullable=False)  # accepted / partially_accepted / rejected
    rejection_reason = Column(String(300))  # damaged / expired / wrong_item / quantity_mismatch / packaging_defect
    added_to_inventory = Column(Boolean, default=False)
    batch_number = Column(String(100))
    expiry_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
