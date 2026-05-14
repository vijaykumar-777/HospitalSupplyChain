#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting Hospital Supply Chain System..."

# Start Ollama (assuming it's installed and qwen2.5:7b is pulled)
echo "Ensuring Ollama is running..."
# ollama serve &
# sleep 5

# Start backend
echo "Starting FastAPI Backend..."
cd "$ROOT_DIR"
# Use Python 3.12 as 3.14 is currently too experimental for numpy/pandas
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

if [ ! -f "$ROOT_DIR/hospital_supply.db" ]; then
  echo "Seeding demo database..."
  python backend/data/seed_db.py
fi

python -m uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting React Frontend..."
cd "$ROOT_DIR/frontend"
npm install
npm run dev &
FRONTEND_PID=$!

echo "========================================================"
echo "System is live!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "========================================================"
echo "Press Ctrl+C to stop all services."

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
