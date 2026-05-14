"""AI Service using local Ollama instance for predictive analysis."""
import os
import json
import re
import logging
import httpx
from datetime import datetime
import uuid

from sqlalchemy.orm import Session
from backend.models.ai_predictions_log import AIPredictionsLog

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

def parse_ollama_json(raw: str) -> dict:
    """Robust JSON parsing to handle markdown blocks and trailing text."""
    cleaned = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: extract first {...} block
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Could not parse Ollama response: {raw[:200]}")

def _call_ollama(prompt: str) -> tuple[dict, int]:
    """Call Ollama API and return parsed JSON and latency."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"  # Ollama supports forcing JSON format output
    }
    
    start_time = datetime.now()
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            latency = int((datetime.now() - start_time).total_seconds() * 1000)
            return parse_ollama_json(data.get("response", "{}")), latency
    except Exception as e:
        logger.error(f"Ollama API error: {e}")
        # Return fallback mock if Ollama is unreachable, so demo doesn't crash
        latency = int((datetime.now() - start_time).total_seconds() * 1000)
        return {"error": str(e), "is_delayed": False}, latency

def log_prediction(db: Session, pred_type: str, input_payload: dict, output_payload: dict, latency: int, order_id: str = None, event_id: str = None):
    """Log every AI call to the database."""
    log_entry = AIPredictionsLog(
        log_id=str(uuid.uuid4()),
        prediction_type=pred_type,
        input_payload=input_payload,
        output_payload=output_payload,
        order_id=order_id,
        event_id=event_id,
        model_used=OLLAMA_MODEL,
        latency_ms=latency
    )
    db.add(log_entry)
    db.commit()

# --- PROMPT A: Delivery Delay Prediction ---
def predict_delivery_delay(db: Session, order_context: dict) -> dict:
    prompt = f"""
    You are an AI supply chain delay predictor. Analyze the following order context and predict if the delivery will be delayed.
    
    Input Context:
    {json.dumps(order_context, indent=2)}
    
    Expected JSON Output exactly:
    {{
      "is_delayed": true/false,
      "confidence": float (0.0 to 1.0),
      "extra_days": integer (0 if not delayed),
      "new_eta": "YYYY-MM-DD",
      "risk_level": "low/medium/high",
      "reason": "one concise sentence explaining why"
    }}
    """
    result, latency = _call_ollama(prompt)
    log_prediction(db, "delivery_delay", order_context, result, latency, order_id=order_context.get("order_id"))
    return result

# --- PROMPT B: Disaster Severity Analysis ---
def analyze_disaster_severity(db: Session, disaster_context: dict) -> dict:
    prompt = f"""
    You are an emergency management AI. Analyze the disaster event text and output its severity and supply chain impact.
    
    Input Context:
    {json.dumps(disaster_context, indent=2)}
    
    Expected JSON Output exactly:
    {{
      "disaster_type": "flood/earthquake/cyclone/fire/collapse",
      "severity": integer (1 to 5),
      "affected_radius_km": integer,
      "supply_routes_likely_blocked": true/false,
      "estimated_casualties": "low/medium/high",
      "suppliers_at_risk_ids": ["uuid1"],
      "summary": "two concise sentences summarizing the event"
    }}
    """
    result, latency = _call_ollama(prompt)
    log_prediction(db, "disaster_severity", disaster_context, result, latency, event_id=disaster_context.get("event_id"))
    return result

# --- PROMPT C: Demand Surge Prediction ---
def predict_demand_surge(db: Session, surge_context: dict) -> dict:
    prompt = f"""
    You are a hospital supply chain AI. Predict the demand surge for this item due to the active disaster.
    
    Input Context:
    {json.dumps(surge_context, indent=2)}
    
    Expected JSON Output exactly:
    {{
      "surge_multiplier": float,
      "urgency_window_hours": integer (6, 24, or 48),
      "predicted_stockout_in_hours": float,
      "recommended_emergency_order_qty": integer,
      "reasoning": "one concise sentence"
    }}
    """
    result, latency = _call_ollama(prompt)
    log_prediction(db, "demand_surge", surge_context, result, latency, event_id=surge_context.get("event_id"))
    return result

# --- PROMPT D: Emergency Supplier Ranking ---
def rank_emergency_suppliers(db: Session, ranking_context: dict) -> dict:
    prompt = f"""
    You are a hospital supply chain AI. Rank the available emergency suppliers for a critical item during a disaster.
    
    Input Context:
    {json.dumps(ranking_context, indent=2)}
    
    Rank by proximity, reliability, emergency certification, and lead time. Exclude suppliers inside the disaster zone.
    Expected JSON Output exactly:
    {{
      "ranked_suppliers": [
        {{
          "supplier_id": "uuid",
          "rank": integer (1, 2, 3...),
          "recommended": true/false,
          "reason": "one sentence"
        }}
      ]
    }}
    """
    result, latency = _call_ollama(prompt)
    log_prediction(db, "supplier_ranking", ranking_context, result, latency)
    return result
