import logging
from datetime import datetime, timedelta
import asyncio
import uuid
from math import radians, sin, cos, sqrt, atan2, pi

from sqlalchemy.orm import Session
from backend.models.disaster_event import DisasterEvent
from backend.models.disaster_prediction import DisasterPrediction
from backend.models.affected_route import AffectedRoute
from backend.models.inventory import Inventory
from backend.models.item import Item
from backend.models.order import Order
from backend.models.supplier import Supplier

from backend.services.external_apis import fetch_gdacs_alerts, fetch_reliefweb_alerts, fetch_news_disaster_alerts, geocode_city, get_alternate_route
from backend.services.ai_service import analyze_disaster_severity, predict_demand_surge, rank_emergency_suppliers
from backend.settings import HOSPITAL_CITY, HOSPITAL_LAT, HOSPITAL_LNG

logger = logging.getLogger(__name__)

ORS_HOSTED_MAX_AVOID_ROUTE_KM = 145.0
ORS_HOSTED_MAX_AVOID_RADIUS_KM = 7.5

def haversine_km(lat1, lng1, lat2, lng2) -> float:
    R = 6371
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

def is_in_disaster_zone(supplier_lat, supplier_lng, event_lat, event_lng, radius_km) -> bool:
    return haversine_km(supplier_lat, supplier_lng, event_lat, event_lng) <= radius_km


def build_avoid_polygon(event_lat: float, event_lng: float, radius_km: float, points: int = 64) -> dict:
    """Approximate a circular disaster zone as a polygon for route avoidance."""
    coords = []
    lat_scale = radius_km / 111.0
    lng_scale = radius_km / max(1e-6, 111.0 * cos(radians(event_lat)))

    for idx in range(points):
        theta = 2 * pi * idx / points
        lat = event_lat + lat_scale * sin(theta)
        lng = event_lng + lng_scale * cos(theta)
        coords.append([lng, lat])

    coords.append(coords[0])
    return {"type": "Polygon", "coordinates": [coords]}


def build_hosted_ors_avoid_polygon(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    event_lat: float,
    event_lng: float,
    radius_km: float,
) -> dict | None:
    """Build an ORS-compatible avoid polygon for short routes on the hosted API."""
    if haversine_km(origin_lat, origin_lng, dest_lat, dest_lng) > ORS_HOSTED_MAX_AVOID_ROUTE_KM:
        return None
    return build_avoid_polygon(event_lat, event_lng, min(radius_km, ORS_HOSTED_MAX_AVOID_RADIUS_KM))


def build_bypass_waypoints(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    event_lat: float,
    event_lng: float,
    radius_km: float,
) -> list[tuple[float, float]]:
    """Generate road-routing waypoints that steer long routes around a disaster center."""
    lat_to_km = 111.0
    lng_to_km = max(1e-6, 111.0 * cos(radians(event_lat)))
    origin_x, origin_y = origin_lng * lng_to_km, origin_lat * lat_to_km
    dest_x, dest_y = dest_lng * lng_to_km, dest_lat * lat_to_km
    event_x, event_y = event_lng * lng_to_km, event_lat * lat_to_km

    route_x = dest_x - origin_x
    route_y = dest_y - origin_y
    route_len = max(1e-6, sqrt(route_x**2 + route_y**2))
    perp_x = -route_y / route_len
    perp_y = route_x / route_len
    clearance_km = max(20.0, min(radius_km * 1.25, 180.0))

    candidates = []
    for side in (1, -1):
        waypoint_x = event_x + side * perp_x * clearance_km
        waypoint_y = event_y + side * perp_y * clearance_km
        waypoint_lat = waypoint_y / lat_to_km
        waypoint_lng = waypoint_x / lng_to_km
        straight_distance = (
            haversine_km(origin_lat, origin_lng, waypoint_lat, waypoint_lng)
            + haversine_km(waypoint_lat, waypoint_lng, dest_lat, dest_lng)
        )
        candidates.append((straight_distance, waypoint_lng, waypoint_lat))

    return [(lng, lat) for _, lng, lat in sorted(candidates)]


def infer_disaster_location(raw_text: str) -> tuple[float, float, str]:
    """Use known demo-friendly Indian locations before falling back near the hospital."""
    text = (raw_text or "").lower()
    known_locations = [
        (("coastal karnataka", "mangaluru", "mangalore", "nh-66", "nh-75"), 12.9141, 74.8560, "Coastal Karnataka"),
        (("kerala", "kochi", "ernakulam"), 9.9312, 76.2673, "Kerala"),
        (("chennai", "tamil nadu"), 13.0827, 80.2707, "Chennai, Tamil Nadu"),
        (("andhra", "visakhapatnam", "cyclone"), 17.6868, 83.2185, "Andhra Coast"),
        (("bengaluru", "bangalore"), 12.9716, 77.5946, HOSPITAL_CITY),
    ]

    for keywords, lat, lng, label in known_locations:
        if any(keyword in text for keyword in keywords):
            return lat, lng, label

    # Deterministic fallback keeps demos repeatable while avoiding a hardcoded single point.
    offset_index = sum(ord(char) for char in text[:80]) % 4
    offsets = [(0.75, -1.1), (-0.55, 1.05), (1.0, 0.8), (-0.85, -0.75)]
    lat_offset, lng_offset = offsets[offset_index]
    return HOSPITAL_LAT + lat_offset, HOSPITAL_LNG + lng_offset, f"Near {HOSPITAL_CITY}"


def build_fallback_route_geojson(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    event_lat: float,
    event_lng: float,
    radius_km: float,
) -> dict:
    """Return a rerouted polyline that visibly skirts around the disaster zone."""
    clearance_lat = (radius_km / 111.0) * 1.35
    clearance_lng = (radius_km / max(1e-6, 111.0 * cos(radians(event_lat)))) * 1.35
    waypoint_lat = event_lat + clearance_lat if origin_lat <= dest_lat else event_lat - clearance_lat
    waypoint_lng = event_lng + clearance_lng

    return {
        "type": "Feature",
        "properties": {"fallback": True},
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [origin_lng, origin_lat],
                [waypoint_lng, waypoint_lat],
                [dest_lng, dest_lat],
            ],
        },
    }

async def run_disaster_pipeline(db: Session):
    """Full pipeline: poll, geocode, analyze severity, predict surges, reroute."""
    
    gdacs_task = asyncio.create_task(fetch_gdacs_alerts())
    relief_task = asyncio.create_task(fetch_reliefweb_alerts())
    news_task = asyncio.create_task(fetch_news_disaster_alerts())
    
    gdacs, relief, news = await asyncio.gather(gdacs_task, relief_task, news_task)
    all_events = gdacs + relief + news
    
    added_count = 0
    
    for evt in all_events:
        title = evt.get("title", "")
        desc = evt.get("description", "")
        if not title:
            continue
            
        recent_cutoff = datetime.now() - timedelta(hours=48)
        existing = db.query(DisasterEvent).filter(
            DisasterEvent.detected_at >= recent_cutoff,
            DisasterEvent.raw_text.ilike(f"%{title[:20]}%")
        ).first()
        
        if existing:
            continue

        db.query(DisasterEvent).filter(DisasterEvent.is_active == True).update({"is_active": False})
            
        event_lat, event_lng, location_name = infer_disaster_location(f"{title} {desc}")
        
        # 1. AI Severity Analysis
        ai_res = analyze_disaster_severity(db, {"raw_text": title + " " + desc, "source": evt.get("source")})
        
        radius_km = ai_res.get("affected_radius_km", 150)
        
        new_evt = DisasterEvent(
            event_id=str(uuid.uuid4()),
            source=evt.get("source", "unknown"),
            disaster_type=ai_res.get("disaster_type", "other"),
            severity=ai_res.get("severity", 1),
            location_name=location_name,
            lat=event_lat,
            lng=event_lng,
            affected_radius_km=radius_km,
            detected_at=datetime.now(),
            is_active=True,
            raw_text=title,
            ai_summary=ai_res.get("summary")
        )
        db.add(new_evt)
        db.flush()
        
        # 2. Demand Surge Predictions
        # For demo, just pick top 5 critical items instead of all
        critical_inventory = db.query(Inventory).join(Item).filter(Item.criticality == "life_critical").limit(5).all()
        for inv in critical_inventory:
            item = db.query(Item).filter(Item.item_id == inv.item_id).first()
            surge_context = {
                "event_id": new_evt.event_id,
                "disaster_type": new_evt.disaster_type,
                "severity": new_evt.severity,
                "item_name": item.name,
                "current_stock": inv.current_stock,
                "daily_consumption": inv.daily_consumption_disaster
            }
            surge_res = predict_demand_surge(db, surge_context)
            
            # Optionally store to disaster_predictions
            pred = DisasterPrediction(
                event_id=new_evt.event_id,
                item_id=item.item_id,
                surge_multiplier=surge_res.get("surge_multiplier", 1.0),
                urgency_window_hours=surge_res.get("urgency_window_hours", 24),
                predicted_stockout_in_hours=surge_res.get("predicted_stockout_in_hours", 48.0),
                ai_reasoning=surge_res.get("reasoning", "Monitor closely"),
                created_at=datetime.now()
            )
            db.add(pred)
            
        # 3. Affected Routes & Re-Routing
        pending_orders = db.query(Order).filter(Order.status.in_(["pending", "in_transit"])).limit(8).all()
        for order in pending_orders:
            supplier = db.query(Supplier).filter(Supplier.supplier_id == order.supplier_id).first()
            if not supplier:
                continue
            
            sup_lat = supplier.lat
            sup_lng = supplier.lng
            
            if is_in_disaster_zone(sup_lat, sup_lng, event_lat, event_lng, radius_km):
                # Supplier affected!
                order.status = "delayed"
                route_geojson = await get_alternate_route(
                    sup_lat,
                    sup_lng,
                    HOSPITAL_LAT,
                    HOSPITAL_LNG,
                    build_hosted_ors_avoid_polygon(
                        sup_lat,
                        sup_lng,
                        HOSPITAL_LAT,
                        HOSPITAL_LNG,
                        event_lat,
                        event_lng,
                        radius_km,
                    ),
                    build_bypass_waypoints(
                        sup_lat,
                        sup_lng,
                        HOSPITAL_LAT,
                        HOSPITAL_LNG,
                        event_lat,
                        event_lng,
                        radius_km,
                    ),
                )
                if not route_geojson:
                    route_geojson = build_fallback_route_geojson(
                        sup_lat,
                        sup_lng,
                        HOSPITAL_LAT,
                        HOSPITAL_LNG,
                        event_lat,
                        event_lng,
                        radius_km,
                    )

                estimated_distance_km = haversine_km(sup_lat, sup_lng, HOSPITAL_LAT, HOSPITAL_LNG) * 1.25
                
                route = AffectedRoute(
                    route_id=str(uuid.uuid4()),
                    event_id=new_evt.event_id,
                    supplier_id=order.supplier_id,
                    order_id=order.order_id,
                    original_route_name="Primary supplier route",
                    is_blocked=True,
                    alternate_route_geojson=route_geojson,
                    alternate_mode="road",
                    alternate_eta_hours=round(max(1.0, estimated_distance_km / 45), 1),
                    disruption_risk="high",
                    created_at=datetime.now()
                )
                db.add(route)
        
        db.commit()
        added_count += 1
        
    return added_count
