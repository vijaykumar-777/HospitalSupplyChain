# Hospital Supply Chain Demo

Hospital supply-chain risk dashboard with a FastAPI backend and a React/Vite frontend. The current demo focuses on three flows:

- viewing live inventory, suppliers, and orders
- generating AI-assisted delivery-delay predictions
- simulating a disaster and showing downstream supply-chain impact

## Quickstart

### Option 1: one command

```bash
./run.sh
```

This creates a local virtualenv, installs backend dependencies, seeds the SQLite database if `hospital_supply.db` is missing, and starts:

- backend: [http://localhost:8000](http://localhost:8000)
- frontend: [http://localhost:5173](http://localhost:5173)

### Option 2: manual startup

Backend:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
if [ ! -f hospital_supply.db ]; then python3 backend/data/seed_db.py; fi
python3 -m uvicorn backend.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Configuration

- backend env file: `backend/.env`
- example env file: `backend/.env.example`
- frontend API base URL: `VITE_API_BASE_URL`, defaults to `http://localhost:8000/api`
- Ollama is optional for demos. If it is unavailable, AI calls fall back to safe placeholder outputs so the UI flow still works.
- The hospital map position is driven by `HOSPITAL_LAT`, `HOSPITAL_LNG`, and `HOSPITAL_CITY` from `backend/.env`.

## Demo Script

1. Open the dashboard and verify orders, inventory, and supplier data are present.
2. Open `Disaster Intelligence`.
3. Click `Simulate Disaster`.
4. Confirm the active incident card appears, supplier markers light up, and reroute lines render on the map.
5. Visit `Orders` and verify impacted orders move to `delayed`.
6. Open an order detail page to view AI prediction and alternate suppliers.

## Verification

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

Backend:

```bash
pytest
```
