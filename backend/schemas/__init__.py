"""Pydantic schemas for API request/response models."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# --- Orders ---
class OrderCreate(BaseModel):
    item_id: str
    supplier_id: str
    quantity: int
    expected_delivery_date: date
    is_emergency_order: bool = False

class OrderStatusUpdate(BaseModel):
    status: str  # pending / in_transit / delivered / delayed / cancelled

class OrderResponse(BaseModel):
    order_id: str
    item_id: str
    supplier_id: str
    quantity: int
    order_date: datetime
    expected_delivery_date: date
    status: str
    is_emergency_order: bool
    triggered_by_disaster_event_id: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# --- Suppliers ---
class SupplierResponse(BaseModel):
    supplier_id: str
    name: str
    city: str
    state: str
    lat: float
    lng: float
    reliability_score: float
    avg_lead_days: int
    supply_categories: list
    is_emergency_certified: bool
    is_govt_reserve: bool
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    model_config = {"from_attributes": True}


# --- Purchase Orders ---
class POResponse(BaseModel):
    po_id: str
    po_number: str
    order_id: str
    raised_by: str
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    approval_status: str
    budget_code: str
    payment_terms: str
    payment_status: str
    total_value_inr: float
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class PORejectRequest(BaseModel):
    reason: str


# --- GRN ---
class GRNCreate(BaseModel):
    order_id: str
    po_id: str
    received_by: str
    inspected_by: str
    received_qty: int
    accepted_qty: int
    rejected_qty: int
    quality_status: str  # accepted / partially_accepted / rejected
    rejection_reason: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None

class GRNResponse(BaseModel):
    grn_id: str
    grn_number: str
    order_id: str
    po_id: str
    received_date: datetime
    received_by: str
    inspected_by: str
    ordered_qty: int
    received_qty: int
    accepted_qty: int
    rejected_qty: int
    quality_status: str
    rejection_reason: Optional[str] = None
    added_to_inventory: bool
    batch_number: Optional[str] = None
    expiry_date: Optional[date] = None
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# --- Inventory ---
class InventoryResponse(BaseModel):
    inventory_id: str
    item_id: str
    current_stock: int
    reorder_level: int
    max_capacity: int
    daily_consumption_normal: float
    daily_consumption_disaster: float
    last_updated: Optional[datetime] = None
    model_config = {"from_attributes": True}


# --- Delivery History ---
class DeliveryHistoryResponse(BaseModel):
    delivery_id: str
    order_id: str
    supplier_id: str
    item_id: str
    expected_date: date
    actual_date: Optional[date] = None
    delay_days: Optional[int] = None
    delay_reason: Optional[str] = None
    season: Optional[str] = None
    model_config = {"from_attributes": True}


# --- Disaster ---
class DisasterEventResponse(BaseModel):
    event_id: str
    source: str
    external_event_id: Optional[str] = None
    disaster_type: str
    severity: int
    location_name: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    affected_radius_km: Optional[int] = None
    detected_at: datetime
    is_active: bool
    raw_text: str
    ai_summary: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class DisasterPredictionResponse(BaseModel):
    pred_id: str
    event_id: str
    item_id: str
    surge_multiplier: float
    urgency_window_hours: int
    predicted_stockout_in_hours: Optional[float] = None
    ai_reasoning: Optional[str] = None
    model_config = {"from_attributes": True}

class AffectedRouteResponse(BaseModel):
    route_id: str
    event_id: str
    supplier_id: str
    order_id: Optional[str] = None
    original_route_name: Optional[str] = None
    is_blocked: bool
    disruption_risk: Optional[str] = None
    alternate_route_geojson: Optional[dict] = None
    alternate_mode: Optional[str] = None
    alternate_eta_hours: Optional[float] = None
    model_config = {"from_attributes": True}

class AIPredictionLogResponse(BaseModel):
    log_id: str
    prediction_type: str
    input_payload: dict
    output_payload: dict
    order_id: Optional[str] = None
    event_id: Optional[str] = None
    model_used: Optional[str] = None
    latency_ms: Optional[int] = None
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
