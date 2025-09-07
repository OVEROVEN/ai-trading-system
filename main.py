from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI(
    title="AI Trading System",
    description="Professional AI-powered trading analysis platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "🚀 AI Trading System is running!",
        "status": "operational", 
        "version": "1.0.0",
        "features": ["stock_analysis", "ai_recommendations", "redemption_codes"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-trading-system",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "timestamp": "2024-09-01T15:00:00Z"
    }

@app.get("/api/redemption")
async def redemption_info():
    return {
        "message": "兌換碼系統已就緒",
        "status": "available",
        "endpoints": {
            "redeem": "/api/redemption/redeem",
            "status": "/api/redemption/status"
        }
    }

@app.get("/docs-summary")
async def docs_summary():
    return {
        "api_documentation": "/docs",
        "health_check": "/health",
        "redemption_api": "/api/redemption",
        "interactive_docs": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
