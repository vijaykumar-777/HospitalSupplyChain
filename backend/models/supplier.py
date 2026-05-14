"""Supplier model."""
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from backend.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    reliability_score = Column(Float, nullable=False)  # 0.0–1.0
    avg_lead_days = Column(Integer, nullable=False)
    supply_categories = Column(JSON, nullable=False)  # e.g. ["medicines","instruments"]
    is_emergency_certified = Column(Boolean, default=False)
    is_govt_reserve = Column(Boolean, default=False)
    contact_email = Column(String(200))
    contact_phone = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
