"""AI Predictions Log model."""
import uuid
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from backend.database import Base


class AIPredictionsLog(Base):
    __tablename__ = "ai_predictions_log"

    log_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_type = Column(String(50), nullable=False)  # delivery_delay / disaster_severity / demand_surge / route_disruption
    input_payload = Column(JSON, nullable=False)
    output_payload = Column(JSON, nullable=False)
    order_id = Column(String, ForeignKey("orders.order_id"), nullable=True)
    event_id = Column(String, ForeignKey("disaster_events.event_id"), nullable=True)
    model_used = Column(String(100))
    latency_ms = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
