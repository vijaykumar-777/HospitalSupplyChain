from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.disaster_event import DisasterEvent
from backend.models.disaster_prediction import DisasterPrediction
from backend.models.affected_route import AffectedRoute
from backend.schemas import DisasterEventResponse, DisasterPredictionResponse, AffectedRouteResponse
from backend.services.external_apis import fetch_gdacs_alerts, fetch_reliefweb_alerts, fetch_news_disaster_alerts
from backend.services.ai_service import analyze_disaster_severity
from datetime import datetime, timedelta
import asyncio
import uuid

router = APIRouter(prefix="/api/disaster", tags=["Disaster"])

async def _poll_and_process_disasters(db: Session):
    gdacs_task = asyncio.create_task(fetch_gdacs_alerts())
    relief_task = asyncio.create_task(fetch_reliefweb_alerts())
    news_task = asyncio.create_task(fetch_news_disaster_alerts())
    
    gdacs, relief, news = await asyncio.gather(gdacs_task, relief_task, news_task)
    all_events = gdacs + relief + news
    
    added = 0
    for evt in all_events:
        # Deduplication check
        title = evt.get("title", "")
        # Very simple deduplication heuristic for demo
        recent_cutoff = datetime.now() - timedelta(hours=48)
        existing = db.query(DisasterEvent).filter(
            DisasterEvent.detected_at >= recent_cutoff,
            DisasterEvent.raw_text.ilike(f"%{title[:20]}%")
        ).first()
        
        if not existing and title:
            # Analyze severity using AI
            ai_res = analyze_disaster_severity(db, {"raw_text": title + " " + evt.get("description", ""), "source": evt.get("source")})
            
            new_evt = DisasterEvent(
                event_id=str(uuid.uuid4()),
                source=evt.get("source", "unknown"),
                disaster_type=ai_res.get("disaster_type", "other"),
                severity=ai_res.get("severity", 1),
                location_name="Parsed Location", # Could use AI or geocoding to refine
                detected_at=datetime.now(),
                is_active=True,
                raw_text=title,
                ai_summary=ai_res.get("summary")
            )
            db.add(new_evt)
            added += 1
            
    db.commit()
    return added

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


@router.post("/trigger-check")
async def trigger_disaster_check(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger disaster API poll (Phase 4)."""
    # For a true background task in FastAPI we would pass a sync wrapper that runs asyncio.run, 
    # but since this is an async endpoint we can just await it directly for feedback, or use background_tasks.
    # We'll await it so the user sees how many were added in the response.
    added = await _poll_and_process_disasters(db)
    return {"status": "ok", "message": f"Disaster check completed. {added} new events added."}


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
    return db.query(AffectedRoute).filter(AffectedRoute.event_id == active.event_id).all()
