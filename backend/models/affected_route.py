"""Affected Route model."""
import uuid
from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class AffectedRoute(Base):
    __tablename__ = "affected_routes"

    route_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey("disaster_events.event_id"), nullable=False)
    supplier_id = Column(String, ForeignKey("suppliers.supplier_id"), nullable=False)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=True)
    original_route_name = Column(String(200))
    is_blocked = Column(Boolean, default=False)
    disruption_risk = Column(String(50))  # low / medium / high / blocked
    alternate_route_geojson = Column(JSON)
    alternate_mode = Column(String(50))  # road / rail / air
    alternate_eta_hours = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
