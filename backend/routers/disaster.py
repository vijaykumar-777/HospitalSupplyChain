from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.disaster_event import DisasterEvent
from backend.models.disaster_prediction import DisasterPrediction
from backend.models.affected_route import AffectedRoute
from backend.models.inventory import Inventory
from backend.models.item import Item
from backend.models.order import Order
from backend.models.supplier import Supplier
from backend.schemas import DisasterEventResponse, DisasterPredictionResponse, AffectedRouteResponse
from backend.services.disaster_pipeline import build_avoid_polygon, build_fallback_route_geojson, run_disaster_pipeline
from backend.services.ai_service import predict_demand_surge
from backend.services.external_apis import get_alternate_route
from backend.settings import HOSPITAL_CITY, HOSPITAL_LAT, HOSPITAL_LNG
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/api/disaster", tags=["Disaster"])

@router.post("/simulate")
async def simulate_disaster(db: Session = Depends(get_db)):
    """Inject a fake disaster into the pipeline for demo purposes."""
    db.query(DisasterEvent).filter(DisasterEvent.is_active == True).update({"is_active": False})

    evt = DisasterEvent(
        event_id=str(uuid.uuid4()),
        source="demo-simulation",
        disaster_type="flood",
        severity=4,
        location_name="Coastal Karnataka",
        lat=12.9141,
        lng=74.8560,
        affected_radius_km=150,
        detected_at=datetime.now(),
        is_active=True,
        raw_text="SEVERE FLOOD WARNING: Coastal Karnataka rivers have breached danger marks. NH-66 and NH-75 severely affected.",
        ai_summary="Severe flooding in coastal Karnataka affecting major highways. Expect significant delays for supply routes."
    )
    db.add(evt)
    db.flush()
    
    # 2. Demand Surge Predictions (Demo: Top 2 items)
    critical_inventory = db.query(Inventory).join(Item).filter(Item.criticality == "life_critical").limit(2).all()
    for inv in critical_inventory:
        item = db.query(Item).filter(Item.item_id == inv.item_id).first()
        surge_context = {
            "event_id": evt.event_id,
            "disaster_type": evt.disaster_type,
            "severity": evt.severity,
            "item_name": item.name,
            "current_stock": inv.current_stock,
            "daily_consumption": inv.daily_consumption_disaster
        }
        surge_res = predict_demand_surge(db, surge_context)
        pred = DisasterPrediction(
            event_id=evt.event_id,
            item_id=item.item_id,
            surge_multiplier=surge_res.get("surge_multiplier", 1.0),
            urgency_window_hours=surge_res.get("urgency_window_hours", 24),
            predicted_stockout_in_hours=surge_res.get("predicted_stockout_in_hours", 48.0),
            ai_reasoning=surge_res.get("reasoning", "Monitor closely"),
            created_at=datetime.now()
        )
        db.add(pred)

    # 3. Affected Routes (Demo: Delay first 2 pending orders)
    pending_orders = db.query(Order).filter(Order.status == "pending").limit(2).all()
    avoid_polygon = build_avoid_polygon(evt.lat, evt.lng, evt.affected_radius_km or 150)
    for order in pending_orders:
        order.status = "delayed"
        supplier = db.query(Supplier).filter(Supplier.supplier_id == order.supplier_id).first()
        if not supplier:
            continue

        route_geojson = await get_alternate_route(
            supplier.lat,
            supplier.lng,
            HOSPITAL_LAT,
            HOSPITAL_LNG,
            avoid_polygon,
        )
        if not route_geojson:
            route_geojson = build_fallback_route_geojson(
                supplier.lat,
                supplier.lng,
                HOSPITAL_LAT,
                HOSPITAL_LNG,
                evt.lat,
                evt.lng,
                evt.affected_radius_km or 150,
            )

        route = AffectedRoute(
            route_id=str(uuid.uuid4()),
            event_id=evt.event_id,
            supplier_id=order.supplier_id,
            order_id=order.order_id,
            original_route_name="Primary supplier route",
            is_blocked=True,
            alternate_route_geojson=route_geojson,
            alternate_mode="road",
            alternate_eta_hours=float(timedelta(days=5).total_seconds() / 3600),
            disruption_risk="high",
            created_at=datetime.now()
        )
        db.add(route)

    db.commit()
    return {"status": "ok", "message": "Disaster simulation injected and effects calculated"}

@router.get("/events", response_model=list[DisasterEventResponse])
def list_events(db: Session = Depends(get_db)):
    return db.query(DisasterEvent).order_by(DisasterEvent.is_active.desc(), DisasterEvent.detected_at.desc()).all()


@router.get("/events/{event_id}")
def get_event_detail(event_id: str, db: Session = Depends(get_db)):
    event = db.query(DisasterEvent).filter(DisasterEvent.event_id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
    preds = db.query(DisasterPrediction).filter(DisasterPrediction.event_id == event_id).all()
    routes = db.query(AffectedRoute).filter(AffectedRoute.event_id == event_id).all()
    return {
        "event": DisasterEventResponse.model_validate(event),
        "predictions": [DisasterPredictionResponse.model_validate(p) for p in preds],
        "affected_routes": [AffectedRouteResponse.model_validate(r) for r in routes],
    }


@router.get("/active")
def get_active_event(db: Session = Depends(get_db)):
    event = db.query(DisasterEvent).filter(DisasterEvent.is_active == True).first()
    if not event:
        return {"active": False, "event": None}
    return {"active": True, "event": DisasterEventResponse.model_validate(event)}


@router.get("/context")
def get_disaster_context():
    return {
        "hospital": {
            "lat": HOSPITAL_LAT,
            "lng": HOSPITAL_LNG,
            "city": HOSPITAL_CITY,
        }
    }


@router.post("/trigger-check")
async def trigger_disaster_check(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger disaster API poll (Phase 4/6)."""
    added = await run_disaster_pipeline(db)
    return {"status": "ok", "message": f"Disaster check completed. {added} new events added and processed."}


@router.get("/surge-predictions", response_model=list[DisasterPredictionResponse])
def get_surge_predictions(db: Session = Depends(get_db)):
    active = db.query(DisasterEvent).filter(DisasterEvent.is_active == True).first()
    if not active:
        return []
    return db.query(DisasterPrediction).filter(DisasterPrediction.event_id == active.event_id).all()


@router.get("/routes", response_model=list[AffectedRouteResponse])
def get_affected_routes(db: Session = Depends(get_db)):
    active = db.query(DisasterEvent).filter(DisasterEvent.is_active == True).first()
    if not active:
        return []
    routes = db.query(AffectedRoute).filter(AffectedRoute.event_id == active.event_id).all()
    payload = []
    for route in routes:
        supplier = db.query(Supplier).filter(Supplier.supplier_id == route.supplier_id).first()
        payload.append({
            "route_id": route.route_id,
            "event_id": route.event_id,
            "supplier_id": route.supplier_id,
            "supplier_name": supplier.name if supplier else None,
            "supplier_city": supplier.city if supplier else None,
            "supplier_lat": supplier.lat if supplier else None,
            "supplier_lng": supplier.lng if supplier else None,
            "order_id": route.order_id,
            "original_route_name": route.original_route_name,
            "is_blocked": route.is_blocked,
            "disruption_risk": route.disruption_risk,
            "alternate_route_geojson": route.alternate_route_geojson,
            "alternate_mode": route.alternate_mode,
            "alternate_eta_hours": route.alternate_eta_hours,
            "hospital_lat": HOSPITAL_LAT,
            "hospital_lng": HOSPITAL_LNG,
            "hospital_city": HOSPITAL_CITY,
        })
    return payload
