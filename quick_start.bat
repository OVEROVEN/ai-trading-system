@echo off
echo Starting AI Trading Dashboard...

REM Start API
start "API" cmd /c "uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"

REM Start Frontend  
timeout /t 3 >nul
cd frontend
start "Frontend" cmd /c "npm run dev"

echo.
echo Started! Visit: http://localhost:3000
pause