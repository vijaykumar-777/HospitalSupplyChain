"""Predictions router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.ai_predictions_log import AIPredictionsLog
from backend.schemas import AIPredictionLogResponse

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.get("/log", response_model=list[AIPredictionLogResponse])
def get_prediction_log(db: Session = Depends(get_db)):
    return db.query(AIPredictionsLog).order_by(AIPredictionsLog.created_at.desc()).limit(100).all()


@router.post("/recheck-all")
def recheck_all_pending(db: Session = Depends(get_db)):
    """Placeholder — triggers AI re-prediction on all pending orders (Phase 3)."""
    return {"status": "ok", "message": "Re-prediction triggered (AI module pending Phase 3)"}
