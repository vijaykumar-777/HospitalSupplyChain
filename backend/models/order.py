"""Order model."""
import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String, ForeignKey("items.item_id"), nullable=False)
    supplier_id = Column(String, ForeignKey("suppliers.supplier_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    order_date = Column(DateTime, nullable=False)
    expected_delivery_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)  # pending / in_transit / delivered / delayed / cancelled
    is_emergency_order = Column(Boolean, default=False)
    triggered_by_disaster_event_id = Column(String, ForeignKey("disaster_events.event_id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
