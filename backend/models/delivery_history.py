"""Delivery History model."""
import uuid
from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class DeliveryHistory(Base):
    __tablename__ = "delivery_history"

    delivery_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=False)
    supplier_id = Column(String, ForeignKey("suppliers.supplier_id"), nullable=False)
    item_id = Column(String, ForeignKey("items.item_id"), nullable=False)
    expected_date = Column(Date, nullable=False)
    actual_date = Column(Date)  # NULL if not yet delivered
    delay_days = Column(Integer)  # Negative = early, 0 = on time, positive = late
    delay_reason = Column(String(200))  # weather / stock_shortage / transport / disaster / customs / other
    season = Column(String(50))  # monsoon / summer / winter / post_monsoon
    created_at = Column(DateTime, server_default=func.now())
