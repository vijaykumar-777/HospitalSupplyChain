"""Purchase Order model."""
import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    po_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    po_number = Column(String(50), nullable=False, unique=True)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=False)
    raised_by = Column(String(200), nullable=False)
    approved_by = Column(String(200))
    approval_date = Column(DateTime)
    approval_status = Column(String(50), nullable=False)  # draft / pending_approval / approved / rejected
    budget_code = Column(String(100), nullable=False)
    payment_terms = Column(String(50), nullable=False)  # advance / NET30 / NET60
    payment_status = Column(String(50), nullable=False)  # pending / paid / overdue
    total_value_inr = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
