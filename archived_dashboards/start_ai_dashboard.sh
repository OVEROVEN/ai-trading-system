#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}     🚀 AI Trading Dashboard System${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}     Advanced Stock Analysis & AI-Powered Trading${NC}"
echo -e "${BLUE}================================================${NC}"
echo

# Check if we're in the correct directory
if [ ! -f "src/api/main.py" ]; then
    echo -e "${RED}❌ Error: Please run this script from the auto_trade directory!${NC}"
    echo "   Current directory: $(pwd)"
    echo "   Expected: /path/to/auto_trade"
    exit 1
fi

echo -e "${YELLOW}📋 Starting system components...${NC}"
echo

# Start the Python API server
echo -e "${YELLOW}[1/2] 🐍 Starting Backend API Server (Port 8000)...${NC}"

if command -v uv &> /dev/null; then
    uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &
else
    python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &
fi

API_PID=$!
echo "   ⏳ API server starting... (PID: $API_PID)"

# Wait for API to initialize
sleep 5

# Start the Frontend Dashboard
echo -e "${YELLOW}[2/2] 🌐 Starting Frontend Dashboard (Port 3000)...${NC}"

if [ -d "frontend" ]; then
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    echo "   ⏳ Frontend starting... (PID: $FRONTEND_PID)"
    cd ..
else
    echo -e "${YELLOW}   ⚠️  Frontend directory not found. Only API is running.${NC}"
fi

echo
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   ✅ System Started Successfully!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   🌐 Dashboard:    http://localhost:3000${NC}"
echo -e "${GREEN}   📋 API Docs:     http://localhost:8000/docs${NC}"  
echo -e "${GREEN}   ⚡ Backend API:  http://localhost:8000${NC}"
echo -e "${GREEN}   📊 Health:       http://localhost:8000/health${NC}"
echo -e "${GREEN}================================================${NC}"
echo

echo -e "${BLUE}💡 Tips:${NC}"
echo "   • Open Dashboard in your browser: http://localhost:3000"
echo "   • Try analyzing AAPL, TSLA, or 2330.TW"
echo "   • Check API documentation at /docs endpoint"
echo

echo -e "${YELLOW}⚠️  To stop all services: Press Ctrl+C${NC}"
echo

# Handle cleanup on script termination
cleanup() {
    echo
    echo -e "${YELLOW}🛑 Stopping services...${NC}"
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        echo "   ✅ API server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "   ✅ Frontend stopped"
    fi
    echo -e "${GREEN}👋 All services stopped. Goodbye!${NC}"
    exit 0
}

trap cleanup INT TERM

echo "Press Ctrl+C to stop all services..."
wait