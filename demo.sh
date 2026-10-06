#!/bin/bash
# Research Claim Integrity Auditor - Demo Script

echo "============================================================"
echo "Starting Research Claim Integrity Auditor Demo"
echo "============================================================"
echo ""
echo "To start the application manually:"
echo "  Backend: cd api && source .venv/Scripts/activate && uvicorn main:app --reload"
echo "  Frontend: cd web && npm run dev"
echo ""
echo "This script will now start the backend and run the automated demo verification."
echo "Starting FastAPI backend in background..."

# Start backend
cd api
.venv/Scripts/python -m uvicorn main:app --port 8000 &
BACKEND_PID=$!
cd ..

echo "Waiting for backend to be ready..."
sleep 5

echo "Starting automated demo run (3 papers)..."
.venv/Scripts/python run_demo.py

echo "Demo complete! Shutting down backend..."
kill $BACKEND_PID
