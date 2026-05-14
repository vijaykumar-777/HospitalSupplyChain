"""Disaster History model (synthetic past events for AI context)."""
import uuid
from sqlalchemy import Column, String, Integer, Float, Text, JSON
from backend.database import Base


class DisasterHistoryRecord(Base):
    __tablename__ = "disaster_history"

    hist_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    disaster_type = Column(String(50), nullable=False)  # flood / earthquake / cyclone / fire / collapse
    severity = Column(Integer, nullable=False)  # 1–5
    location_name = Column(String(300), nullable=False)
    year = Column(Integer, nullable=False)
    items_most_affected = Column(JSON, nullable=False)  # Array of item categories
    avg_supply_delay_added_days = Column(Float)
    demand_multipliers = Column(JSON)  # e.g. {"trauma": 4.2, "respiratory": 2.8}
    notes = Column(Text)
