"""Disaster Event model."""
import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from backend.database import Base


class DisasterEvent(Base):
    __tablename__ = "disaster_events"

    event_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=False)  # gdacs / reliefweb / newsapi / simulated
    external_event_id = Column(String(200))
    disaster_type = Column(String(50), nullable=False)  # flood / earthquake / cyclone / fire / collapse / other
    severity = Column(Integer, nullable=False)  # 1–5
    location_name = Column(String(300), nullable=False)
    lat = Column(Float)
    lng = Column(Float)
    affected_radius_km = Column(Integer)
    detected_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    raw_text = Column(Text, nullable=False)
    ai_summary = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
