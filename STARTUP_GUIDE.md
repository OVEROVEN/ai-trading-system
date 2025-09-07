# 🚀 AI Trading System - Startup Guide

## Quick Start by Platform

### Windows Users
```bash
# Option 1: Double-click to run
quick_start.bat

# Option 2: Command line
.\quick_start.bat

# Option 3: Advanced launcher
.\start_ai_dashboard.bat
```

### Mac/Linux Users
```bash
# Option 1: Simple startup
./quick_start.sh

# Option 2: Advanced launcher with colors
./start_ai_dashboard.sh

# Option 3: Manual startup
chmod +x *.sh
./quick_start.sh
```

### Universal Method (All Platforms)
```bash
# Start API server
uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd frontend
npm run dev
```

## Access Points
- 🌐 **Frontend Dashboard**: http://localhost:3000
- 📋 **API Documentation**: http://localhost:8000/docs
- ⚡ **Backend API**: http://localhost:8000
- 📊 **Health Check**: http://localhost:8000/health

## Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- `uv` package manager (recommended)

## Troubleshooting

### Permission Issues (Mac/Linux)
```bash
chmod +x *.sh
```

### Missing Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install
```

### Port Conflicts
If ports 3000 or 8000 are in use:
```bash
# Custom ports
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8080
cd frontend && npm run dev -- --port 3001
```