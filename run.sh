#!/bin/bash
echo "Starting Hospital Supply Chain System..."

# Start Ollama (assuming it's installed and qwen2.5:7b is pulled)
echo "Ensuring Ollama is running..."
# ollama serve &
# sleep 5

# Start backend
echo "Starting FastAPI Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting React Frontend..."
cd frontend
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
