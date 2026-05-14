"""Shared application settings loaded from backend/.env."""
import os
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hospital_supply.db")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
ORS_API_KEY = os.getenv("ORS_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
HOSPITAL_LAT = float(os.getenv("HOSPITAL_LAT", "12.9716"))
HOSPITAL_LNG = float(os.getenv("HOSPITAL_LNG", "77.5946"))
HOSPITAL_CITY = os.getenv("HOSPITAL_CITY", "Bengaluru")
ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "true").lower() not in {"0", "false", "no"}
