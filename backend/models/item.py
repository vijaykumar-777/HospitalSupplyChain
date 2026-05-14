"""Item model."""
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.sql import func
from backend.database import Base


class Item(Base):
    __tablename__ = "items"

    item_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(300), nullable=False)
    category = Column(String(50), nullable=False)  # medicine / instrument / consumable / equipment
    criticality = Column(String(50), nullable=False)  # low / medium / high / life_critical
    unit = Column(String(50), nullable=False)  # tablets, units, pcs, litres, vials
    disaster_surge_category = Column(String(100))  # trauma / burn / respiratory / general
    typical_monthly_demand = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
