"""Disaster router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.disaster_event import DisasterEvent
from backend.models.disaster_prediction import DisasterPrediction
from backend.models.affected_route import AffectedRoute
from backend.schemas import DisasterEventResponse, DisasterPredictionResponse, AffectedRouteResponse

router = APIRouter(prefix="/api/disaster", tags=["Disaster"])


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
def trigger_disaster_check():
    """Placeholder — manually trigger disaster API poll (Phase 4)."""
    return {"status": "ok", "message": "Disaster check triggered (External APIs pending Phase 4)"}


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
