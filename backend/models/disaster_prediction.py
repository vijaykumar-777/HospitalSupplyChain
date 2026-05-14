"""Disaster Prediction model."""
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class DisasterPrediction(Base):
    __tablename__ = "disaster_predictions"

    pred_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey("disaster_events.event_id"), nullable=False)
    item_id = Column(String, ForeignKey("items.item_id"), nullable=False)
    surge_multiplier = Column(Float, nullable=False)
    urgency_window_hours = Column(Integer, nullable=False)  # 6 / 24 / 48
    predicted_stockout_in_hours = Column(Float)
    ai_reasoning = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
