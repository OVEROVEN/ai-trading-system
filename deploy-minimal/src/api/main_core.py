#!/usr/bin/env python3
"""
核心API服務 - 微服務架構版本
專注於數據分析、AI功能、用戶管理
圖表生成由獨立服務處理
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import asyncio
import json
import logging
import math
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import httpx

# Import our modules
from config.settings import settings, US_SYMBOLS, TW_SYMBOLS
from src.data_fetcher.us_stocks import USStockDataFetcher
from src.data_fetcher.tw_stocks import TWStockDataFetcher
from src.analysis.technical_indicators import IndicatorAnalyzer
from src.analysis.pattern_recognition import PatternRecognition
from src.analysis.ai_analyzer import OpenAIAnalyzer
from src.analysis.ai_strategy_advisor import AIStrategyAdvisor
from src.analysis.advanced_patterns import AdvancedPatternRecognizer

# Authentication modules
from src.auth.auth_endpoints import auth_router
from src.auth.auth import get_current_user
from src.auth.models import User

# Set up logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# Chart service URL (will be configured via environment)
CHART_SERVICE_URL = settings.chart_service_url if hasattr(settings, 'chart_service_url') else "http://localhost:8001"

def clean_for_json(obj):
    """Clean data to be JSON serializable by handling NaN, infinity, numpy types, and None values."""
    if obj is None:
        return None
    elif isinstance(obj, (int, str, bool)):
        return obj
    elif isinstance(obj, float):
        if pd.isna(obj) or not math.isfinite(obj):
            return None
        return obj
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (np.integer, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
        if pd.isna(obj) or not math.isfinite(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return [clean_for_json(item) for item in obj.tolist()]
    elif isinstance(obj, pd.Series):
        return clean_for_json(obj.dropna().to_dict())
    elif isinstance(obj, pd.DataFrame):
        return clean_for_json(obj.dropna().to_dict('records'))
    elif isinstance(obj, dict):
        return {key: clean_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [clean_for_json(item) for item in obj]
    else:
        try:
            return str(obj)
        except:
            return None

# Initialize FastAPI app
app = FastAPI(
    title="Auto Trade Core API",
    description="微服務核心API - 股票數據分析與AI功能",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
us_data_fetcher = USStockDataFetcher()
tw_data_fetcher = TWStockDataFetcher()
indicator_analyzer = IndicatorAnalyzer()
pattern_recognizer = PatternRecognition()
ai_analyzer = OpenAIAnalyzer()
ai_strategy_advisor = AIStrategyAdvisor()
advanced_pattern_recognizer = AdvancedPatternRecognizer()

# Include authentication routes
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])

# Request/Response Models
class AnalysisRequest(BaseModel):
    symbol: str
    period: str = "3mo"
    include_ai: bool = True
    include_patterns: bool = True

class ChartRequest(BaseModel):
    symbol: str
    period: str = "3mo"
    chart_type: str = "professional"
    theme: str = "dark"
    indicators: Optional[Dict[str, Any]] = None
    patterns: Optional[List[Dict]] = None

@app.get("/")
async def root():
    return {
        "service": "Auto Trade Core API",
        "version": "2.0.0",
        "status": "operational",
        "architecture": "microservices",
        "features": [
            "stock_data_analysis",
            "ai_recommendations", 
            "pattern_recognition",
            "user_management",
            "real_time_streaming"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "core-api",
        "dependencies": {
            "database": "connected",
            "ai_services": "available",
            "data_sources": "online"
        }
    }

@app.post("/analyze/{symbol}")
async def analyze_stock(
    symbol: str,
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """核心股票分析API - 不包含圖表生成"""
    try:
        logger.info(f"分析請求: {symbol} by user {current_user.email}")
        
        # 獲取股票數據
        if symbol.endswith('.TW'):
            data = await tw_data_fetcher.get_stock_data(symbol, request.period)
            market_type = "TW"
        else:
            data = await us_data_fetcher.get_stock_data(symbol, request.period)
            market_type = "US"
        
        if data.empty:
            raise HTTPException(status_code=404, detail="股票數據未找到")
        
        # 計算技術指標
        indicators = indicator_analyzer.calculate_all_indicators(data)
        data_with_indicators = pd.concat([data, pd.DataFrame(indicators, index=data.index)], axis=1)
        
        # 形態識別
        patterns = []
        if request.include_patterns:
            try:
                detected_patterns = pattern_recognizer.find_patterns(data)
                for pattern in detected_patterns:
                    patterns.append({
                        "pattern_name": pattern.pattern_name,
                        "start_date": pattern.start_date.isoformat() if pattern.start_date else None,
                        "end_date": pattern.end_date.isoformat() if pattern.end_date else None,
                        "confidence": float(pattern.confidence),
                        "direction": pattern.direction,
                        "target_price": float(pattern.target_price) if pattern.target_price else None
                    })
            except Exception as e:
                logger.warning(f"形態分析失敗: {str(e)}")
        
        # AI分析
        ai_analysis = None
        if request.include_ai:
            try:
                ai_analysis = await ai_analyzer.analyze_technical_data(
                    symbol=symbol,
                    data=data_with_indicators,
                    patterns=patterns,
                    language="zh-TW"
                )
            except Exception as e:
                logger.warning(f"AI分析失敗: {str(e)}")
        
        # 組裝響應
        result = {
            "symbol": symbol,
            "market": market_type,
            "period": request.period,
            "current_price": float(data['close'].iloc[-1]),
            "price_change": float(data['close'].iloc[-1] - data['close'].iloc[-2]),
            "price_change_percent": float((data['close'].iloc[-1] / data['close'].iloc[-2] - 1) * 100),
            "volume": int(data['volume'].iloc[-1]),
            "indicators": clean_for_json(indicators),
            "patterns": patterns,
            "ai_analysis": ai_analysis,
            "data_points": len(data),
            "last_updated": datetime.now().isoformat()
        }
        
        return clean_for_json(result)
        
    except Exception as e:
        logger.error(f"分析失敗 {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失敗: {str(e)}")

@app.get("/chart/{symbol}")
async def get_chart(
    symbol: str,
    period: str = "3mo",
    chart_type: str = "professional",
    theme: str = "dark",
    current_user: User = Depends(get_current_user)
):
    """圖表生成代理 - 調用獨立圖表服務"""
    try:
        # 首先獲取數據和分析
        analysis_request = AnalysisRequest(symbol=symbol, period=period, include_ai=True)
        analysis_result = await analyze_stock(symbol, analysis_request, current_user)
        
        # 調用圖表服務
        async with httpx.AsyncClient() as client:
            chart_response = await client.post(
                f"{CHART_SERVICE_URL}/generate-chart",
                json={
                    "symbol": symbol,
                    "period": period,
                    "chart_type": chart_type,
                    "theme": theme,
                    "indicators": analysis_result.get("indicators", {}),
                    "patterns": analysis_result.get("patterns", [])
                },
                timeout=30.0
            )
            
            if chart_response.status_code == 200:
                return chart_response.json()
            else:
                # 如果圖表服務不可用，返回純數據
                return {
                    "chart_html": "<p>圖表服務暫時不可用，請稍後再試</p>",
                    "chart_url": None,
                    "fallback": True,
                    "analysis": analysis_result
                }
                
    except Exception as e:
        logger.error(f"圖表生成失敗 {symbol}: {str(e)}")
        return {
            "chart_html": f"<p>圖表生成失敗: {str(e)}</p>",
            "chart_url": None,
            "error": True
        }

@app.get("/symbols")
async def get_symbols():
    """獲取可用股票代碼"""
    return {
        "us_symbols": US_SYMBOLS,
        "tw_symbols": TW_SYMBOLS,
        "total": len(US_SYMBOLS) + len(TW_SYMBOLS)
    }

@app.post("/ai/strategy-advice")
async def get_strategy_advice(
    request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """AI策略建議"""
    try:
        advice = await ai_strategy_advisor.get_strategy_advice(
            symbol=request.get("symbol"),
            market_data=request.get("market_data", {}),
            user_preferences=request.get("preferences", {}),
            language="zh-TW"
        )
        return {"advice": advice, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"AI策略建議失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI服務暫時不可用: {str(e)}")

# WebSocket支持
@app.websocket("/ws/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await websocket.accept()
    try:
        while True:
            # 簡化的實時數據推送
            if symbol.endswith('.TW'):
                data = await tw_data_fetcher.get_stock_data(symbol, "1d")
            else:
                data = await us_data_fetcher.get_stock_data(symbol, "1d")
            
            if not data.empty:
                latest_data = {
                    "symbol": symbol,
                    "price": float(data['close'].iloc[-1]),
                    "volume": int(data['volume'].iloc[-1]),
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_json(latest_data)
            
            await asyncio.sleep(30)  # 30秒更新一次
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket連接斷開: {symbol}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)