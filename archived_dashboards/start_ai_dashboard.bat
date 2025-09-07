@echo off
title AI Trading Dashboard System
color 0A
echo.
echo ================================================
echo     🚀 AI Trading Dashboard System
echo ================================================
echo     Advanced Stock Analysis ^& AI-Powered Trading
echo ================================================
echo.

REM Check if we're in the correct directory
if not exist "src\api\main.py" (
    echo ❌ Error: Please run this script from the auto_trade directory!
    echo    Current directory: %CD%
    echo    Expected: C:\Users\user\Undemy\auto_trade
    pause
    exit /b 1
)

echo 📋 Starting system components...
echo.

REM Start the Python API server
echo [1/2] 🐍 Starting Backend API Server (Port 8000)...
start "Trading API Server" cmd /c "echo Starting API Server... && echo ======================== && uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 && echo. && echo API Server stopped. && pause"

REM Wait for API to initialize
echo    ⏳ Waiting for API server to initialize...
timeout /t 5 /nobreak >nul

REM Start the Frontend Dashboard
echo [2/2] 🌐 Starting Frontend Dashboard (Port 3000)...
cd frontend
start "AI Trading Dashboard" cmd /c "echo Starting Frontend Dashboard... && echo ================================ && npm run dev && echo. && echo Frontend stopped. && pause"

echo.
echo ================================================
echo   ✅ System Started Successfully!
echo ================================================
echo   🌐 Dashboard:    http://localhost:3000
echo   📋 API Docs:     http://localhost:8000/docs  
echo   ⚡ Backend API:  http://localhost:8000
echo   📊 Health:       http://localhost:8000/health
echo ================================================
echo.
echo 💡 Tips:
echo    • Open Dashboard in your browser: http://localhost:3000
echo    • Try analyzing AAPL, TSLA, or 2330.TW
echo    • Check API documentation at /docs endpoint
echo.
echo ⚠️  To stop all services: Close this window or Ctrl+C
echo.
echo Press any key to exit this launcher (services will continue)...
pause >nul

echo.
echo 👋 Launcher closed. Services are still running.
echo    Close individual windows to stop services.