"""Inventory model."""
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String, ForeignKey("items.item_id"), unique=True, nullable=False)
    current_stock = Column(Integer, nullable=False)
    reorder_level = Column(Integer, nullable=False)
    max_capacity = Column(Integer, nullable=False)
    daily_consumption_normal = Column(Float, nullable=False)
    daily_consumption_disaster = Column(Float, nullable=False)
    last_updated = Column(DateTime, server_default=func.now())
