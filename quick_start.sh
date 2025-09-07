#!/bin/bash

echo "🚀 Starting AI Trading Dashboard..."
echo

# Start API in background
echo "Starting API server..."
if command -v uv &> /dev/null; then
    uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &
else
    python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &
fi

API_PID=$!
echo "API started with PID: $API_PID"

# Wait for API to start
sleep 3

# Start Frontend
echo "Starting frontend..."
if [ -d "frontend" ]; then
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
    cd ..
else
    echo "⚠️  Frontend directory not found. Only API is running."
fi

echo
echo "✅ Started! Visit: http://localhost:3000"
echo "📋 API Docs: http://localhost:8000/docs"
echo
echo "Press Ctrl+C to stop all services"

# Handle cleanup on script termination
cleanup() {
    echo
    echo "🛑 Stopping services..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    echo "✅ All services stopped"
    exit 0
}

trap cleanup INT TERM

# Keep script running
wait