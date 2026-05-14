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
from backend.services.disaster_pipeline import build_avoid_polygon, build_fallback_route_geojson, haversine_km, is_in_disaster_zone, run_disaster_pipeline
from backend.services.ai_service import predict_demand_surge
from backend.services.external_apis import get_alternate_route
from backend.settings import HOSPITAL_CITY, HOSPITAL_LAT, HOSPITAL_LNG
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/disaster", tags=["Disaster"])


def _feature_from_geometry(geometry: dict, properties: dict | None = None) -> dict:
    return {
        "type": "Feature",
        "properties": properties or {},
        "geometry": geometry,
    }


def _original_route_feature(
    supplier: Supplier,
    event: DisasterEvent,
    order: Order | None = None,
) -> dict:
    """Create a clear blocked-route comparison path through the active risk zone."""
    waypoint_lng = event.lng if event.lng is not None else HOSPITAL_LNG
    waypoint_lat = event.lat if event.lat is not None else HOSPITAL_LAT
    return _feature_from_geometry(
        {
            "type": "LineString",
            "coordinates": [
                [supplier.lng, supplier.lat],
                [waypoint_lng, waypoint_lat],
                [HOSPITAL_LNG, HOSPITAL_LAT],
            ],
        },
        {
            "status": "blocked",
            "order_id": order.order_id if order else None,
            "supplier_id": supplier.supplier_id,
        },
    )


def _geojson_distance_km(geojson: dict | None) -> float | None:
    if not geojson:
        return None

    if geojson.get("type") == "FeatureCollection":
        features = geojson.get("features", [])
        geometry = features[0].get("geometry") if features else None
    elif geojson.get("type") == "Feature":
        geometry = geojson.get("geometry")
    else:
        geometry = geojson

    if not geometry or geometry.get("type") != "LineString":
        return None

    coords = geometry.get("coordinates", [])
    total = 0.0
    for start, end in zip(coords, coords[1:]):
        total += haversine_km(start[1], start[0], end[1], end[0])
    return round(total, 1)


def _route_payload(route: AffectedRoute, event: DisasterEvent, db: Session) -> dict | None:
    supplier = db.query(Supplier).filter(Supplier.supplier_id == route.supplier_id).first()
    if not supplier:
        return None

    order = db.query(Order).filter(Order.order_id == route.order_id).first() if route.order_id else None
    item = db.query(Item).filter(Item.item_id == order.item_id).first() if order else None
    original_distance = haversine_km(supplier.lat, supplier.lng, HOSPITAL_LAT, HOSPITAL_LNG)
    original_eta = round(max(1.0, original_distance / 42), 1)
    alternate_distance = _geojson_distance_km(route.alternate_route_geojson)
    alternate_eta = route.alternate_eta_hours or (round(max(1.0, (alternate_distance or original_distance) / 45), 1))
    risk_reduction = 82 if route.is_blocked else 45

    return {
        "route_id": route.route_id,
        "event_id": route.event_id,
        "supplier_id": route.supplier_id,
        "supplier_name": supplier.name,
        "supplier_city": supplier.city,
        "supplier_lat": supplier.lat,
        "supplier_lng": supplier.lng,
        "supplier_reliability_score": supplier.reliability_score,
        "supplier_emergency_certified": supplier.is_emergency_certified,
        "order_id": route.order_id,
        "item_name": item.name if item else None,
        "quantity": order.quantity if order else None,
        "criticality": item.criticality if item else None,
        "original_route_name": route.original_route_name,
        "original_route_geojson": _original_route_feature(supplier, event, order),
        "original_status": "blocked" if route.is_blocked else "at_risk",
        "is_blocked": route.is_blocked,
        "disruption_risk": route.disruption_risk,
        "original_eta_hours": original_eta,
        "alternate_route_geojson": route.alternate_route_geojson,
        "alternate_mode": route.alternate_mode,
        "alternate_eta_hours": alternate_eta,
        "alternate_distance_km": alternate_distance,
        "risk_reduction_percent": risk_reduction,
        "reason": "Original route intersects the disaster polygon. The recommended alternate route uses an avoidance corridor and keeps the supplier connected to the receiving hospital.",
        "hospital_lat": HOSPITAL_LAT,
        "hospital_lng": HOSPITAL_LNG,
        "hospital_city": HOSPITAL_CITY,
    }

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
    
    # 2. Demand Surge Predictions (Demo: multiple life-critical items for a fuller response plan)
    critical_inventory = db.query(Inventory).join(Item).filter(Item.criticality == "life_critical").limit(5).all()
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

    # 3. Affected Routes (Demo: Delay a realistic set of pending/in-transit orders)
    pending_orders = db.query(Order).filter(Order.status.in_(["pending", "in_transit"])).limit(8).all()
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

        alternate_distance = _geojson_distance_km(route_geojson) or haversine_km(
            supplier.lat,
            supplier.lng,
            HOSPITAL_LAT,
            HOSPITAL_LNG,
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
            alternate_eta_hours=round(max(1.0, alternate_distance / 45), 1),
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
        route_data = _route_payload(route, active, db)
        if route_data:
            payload.append(route_data)
    return payload


@router.get("/map-data")
def get_disaster_map_data(db: Session = Depends(get_db)):
    active = db.query(DisasterEvent).filter(DisasterEvent.is_active == True).first()
    suppliers = db.query(Supplier).all()
    routes = []
    zone_geojson = None

    if active and active.lat is not None and active.lng is not None:
        radius = active.affected_radius_km or 150
        zone_geojson = _feature_from_geometry(
            build_avoid_polygon(active.lat, active.lng, radius),
            {
                "severity": active.severity,
                "type": active.disaster_type,
                "radius_km": radius,
            },
        )
        active_routes = db.query(AffectedRoute).filter(AffectedRoute.event_id == active.event_id).all()
        routes = [route_data for route in active_routes if (route_data := _route_payload(route, active, db))]

    supplier_payload = []
    for supplier in suppliers:
        inside_zone = bool(active and active.lat is not None and active.lng is not None and is_in_disaster_zone(
            supplier.lat,
            supplier.lng,
            active.lat,
            active.lng,
            active.affected_radius_km or 150,
        ))
        impacted = any(route["supplier_id"] == supplier.supplier_id for route in routes)
        risk_level = "blocked" if inside_zone or impacted else ("low" if supplier.reliability_score >= 0.8 else "medium")
        supplier_payload.append({
            "supplier_id": supplier.supplier_id,
            "name": supplier.name,
            "city": supplier.city,
            "state": supplier.state,
            "lat": supplier.lat,
            "lng": supplier.lng,
            "status": "blocked" if inside_zone or impacted else "safe",
            "reliability_score": supplier.reliability_score,
            "emergency_certified": supplier.is_emergency_certified,
            "is_govt_reserve": supplier.is_govt_reserve,
            "inside_disaster_zone": inside_zone,
            "risk_level": risk_level,
            "supply_categories": supplier.supply_categories,
            "avg_lead_days": supplier.avg_lead_days,
        })

    demand_surge = []
    if active:
        predictions = db.query(DisasterPrediction).filter(DisasterPrediction.event_id == active.event_id).all()
        for prediction in predictions:
            item = db.query(Item).filter(Item.item_id == prediction.item_id).first()
            inventory = db.query(Inventory).filter(Inventory.item_id == prediction.item_id).first()
            demand_surge.append({
                "item_id": prediction.item_id,
                "item_name": item.name if item else None,
                "current_stock": inventory.current_stock if inventory else None,
                "surge_multiplier": prediction.surge_multiplier,
                "stockout_hours": prediction.predicted_stockout_in_hours,
                "recommended_order_qty": int((inventory.daily_consumption_disaster if inventory else 10) * prediction.surge_multiplier * 7),
                "urgency": "critical" if (prediction.predicted_stockout_in_hours or 999) <= 24 else "monitor",
                "reason": prediction.ai_reasoning,
            })

    event_payload = None
    if active:
        event_payload = {
            "event_id": active.event_id,
            "source": active.source,
            "disaster_type": active.disaster_type,
            "severity": active.severity,
            "location_name": active.location_name,
            "lat": active.lat,
            "lng": active.lng,
            "affected_radius_km": active.affected_radius_km,
            "detected_at": active.detected_at,
            "raw_text": active.raw_text,
            "summary": active.ai_summary,
            "zone_geojson": zone_geojson,
        }

    return {
        "event": event_payload,
        "hospital": {
            "name": f"{HOSPITAL_CITY} Central Hospital",
            "lat": HOSPITAL_LAT,
            "lng": HOSPITAL_LNG,
            "city": HOSPITAL_CITY,
        },
        "suppliers": supplier_payload,
        "routes": routes,
        "demand_surge": demand_surge,
        "emergency_suppliers": sorted(
            supplier_payload,
            key=lambda supplier: (
                not supplier["emergency_certified"],
                -supplier["reliability_score"],
                supplier["avg_lead_days"],
            ),
        )[:5],
    }
