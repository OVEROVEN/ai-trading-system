"""
Ultra-minimal FastAPI for Cloud Run - API Only
移除所有視覺化依賴，專注於核心API功能
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import logging
import math
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 只導入核心模組
# 優雅處理配置載入錯誤
try:
    from config.settings import settings, US_SYMBOLS, TW_SYMBOLS
except Exception as e:
    # 如果配置載入失敗，創建基本設置
    import os
    from pydantic import BaseModel
    
    class BasicSettings(BaseModel):
        log_level: str = "INFO"
        openai_api_key: str = ""
        
    settings = BasicSettings()
    if os.getenv("OPENAI_API_KEY"):
        settings.openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # 基本符號清單
    US_SYMBOLS = ["AAPL", "GOOGL", "TSLA", "SPY", "QQQ", "MSFT", "AMZN", "NVDA"]
    TW_SYMBOLS = ["2330.TW", "2317.TW", "0050.TW", "2454.TW", "2881.TW"]
    
    logger.warning(f"Configuration loading failed, using basic settings: {e}")
from src.data_fetcher.us_stocks import USStockDataFetcher
from src.data_fetcher.tw_stocks import TWStockDataFetcher
from src.analysis.technical_indicators import IndicatorAnalyzer

# 嘗試導入可選模組 - 改進錯誤處理
try:
    from src.analysis.ai_analyzer import OpenAIAnalyzer
    # 檢查是否有OpenAI API Key
    if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
        AI_AVAILABLE = True
    else:
        AI_AVAILABLE = False
        logging.warning("OpenAI API key not configured, AI analysis disabled")
except ImportError as e:
    AI_AVAILABLE = False
    logging.warning(f"AI analysis module not available: {e}")
except Exception as e:
    AI_AVAILABLE = False
    logging.warning(f"AI analyzer initialization failed: {e}")

# 設置日誌 - 優雅處理設置錯誤
try:
    log_level = getattr(settings, 'log_level', 'INFO')
    logging.basicConfig(level=getattr(logging, log_level.upper()))
except Exception:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def clean_for_json(obj):
    """清理數據為JSON可序列化格式"""
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
    elif isinstance(obj, (np.integer, np.floating)):
        if pd.isna(obj) or not math.isfinite(obj):
            return None
        return float(obj)
    elif isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items() if clean_for_json(v) is not None}
    elif isinstance(obj, (list, tuple)):
        return [clean_for_json(item) for item in obj if clean_for_json(item) is not None]
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        return str(obj)

# 初始化FastAPI
app = FastAPI(
    title="AI Trading System API - Minimal",
    description="Minimal API for stock analysis and trading insights",
    version="1.0.0"
)

# CORS設置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化數據獲取器 - 添加錯誤處理
try:
    us_fetcher = USStockDataFetcher()
    US_FETCHER_AVAILABLE = True
except Exception as e:
    logger.warning(f"US stock fetcher initialization failed: {e}")
    US_FETCHER_AVAILABLE = False

try:
    tw_fetcher = TWStockDataFetcher()
    TW_FETCHER_AVAILABLE = True
except Exception as e:
    logger.warning(f"Taiwan stock fetcher initialization failed: {e}")
    TW_FETCHER_AVAILABLE = False

try:
    indicator_analyzer = IndicatorAnalyzer()
    INDICATOR_AVAILABLE = True
except Exception as e:
    logger.warning(f"Technical indicator analyzer initialization failed: {e}")
    INDICATOR_AVAILABLE = False

if AI_AVAILABLE:
    try:
        ai_analyzer = OpenAIAnalyzer()
        logger.info("AI analyzer initialized successfully")
    except Exception as e:
        logger.warning(f"Could not initialize AI analyzer: {e}")
        AI_AVAILABLE = False

# Pydantic模型
class StockAnalysisRequest(BaseModel):
    symbol: str
    period: str = "3mo"
    include_ai: bool = True
    language: str = "zh"

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, bool]

# API端點
@app.get("/", response_class=JSONResponse)
async def root():
    """根端點"""
    return {
        "message": "AI Trading System API - Minimal Version",
        "version": "1.0.0",
        "status": "running",
        "features": {
            "stock_analysis": True,
            "technical_indicators": True,
            "ai_analysis": AI_AVAILABLE,
            "visualization": False  # 禁用視覺化
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康檢查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "us_market_data": US_FETCHER_AVAILABLE,
            "taiwan_market_data": TW_FETCHER_AVAILABLE,
            "technical_analysis": INDICATOR_AVAILABLE,
            "ai_analysis": AI_AVAILABLE
        }
    }

@app.get("/symbols")
async def get_symbols():
    """獲取支持的股票代碼"""
    return {
        "us_symbols": US_SYMBOLS,
        "tw_symbols": TW_SYMBOLS,
        "total": len(US_SYMBOLS) + len(TW_SYMBOLS)
    }

@app.post("/analyze/{symbol}")
async def analyze_stock(symbol: str, request: StockAnalysisRequest = None):
    """分析股票"""
    try:
        # 使用路徑參數的symbol，如果有請求體則覆蓋設置
        if request:
            period = request.period
            include_ai = request.include_ai
            language = request.language
        else:
            period = "3mo"
            include_ai = False
            language = "zh"

        logger.info(f"Analyzing {symbol} for period {period}")

        # 獲取股票數據 - 添加服務可用性檢查
        if symbol.endswith('.TW') or (symbol.isdigit() and len(symbol) == 4):
            # 台股
            if not TW_FETCHER_AVAILABLE:
                raise HTTPException(status_code=503, detail="Taiwan stock data service unavailable")
            data = await tw_fetcher.get_stock_data(symbol, period)
            if data is None or data.empty:
                raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        else:
            # 美股
            if not US_FETCHER_AVAILABLE:
                raise HTTPException(status_code=503, detail="US stock data service unavailable")
            data = us_fetcher.get_stock_data(symbol, period)
            if data is None or data.empty:
                raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")

        # 技術指標分析 - 添加可用性檢查
        if INDICATOR_AVAILABLE:
            indicators = indicator_analyzer.calculate_all_indicators(data)
        else:
            indicators = {"error": "Technical indicator analysis unavailable"}
        
        # 基礎分析結果
        current_price = float(data['Close'].iloc[-1])
        price_change_1d = float((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2] * 100) if len(data) > 1 else 0
        
        analysis_result = {
            "symbol": symbol,
            "current_price": current_price,
            "price_change_1d": price_change_1d,
            "volume_ratio": float(data['Volume'].iloc[-1] / data['Volume'].mean()),
            "period": period,
            "indicators": clean_for_json(indicators),
            "timestamp": datetime.now().isoformat(),
            "data_points": len(data)
        }

        # AI分析（如果可用且請求）
        if AI_AVAILABLE and include_ai:
            try:
                ai_result = await ai_analyzer.analyze_technical_data(
                    symbol, analysis_result, language
                )
                analysis_result["ai_analysis"] = ai_result
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                analysis_result["ai_analysis"] = {
                    "error": "AI analysis temporarily unavailable",
                    "recommendation": "HOLD"
                }

        return clean_for_json(analysis_result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/signals/{symbol}")
async def get_trading_signals(symbol: str, period: str = "3mo"):
    """獲取交易信號"""
    try:
        # 簡化的信號生成
        if symbol.endswith('.TW') or (symbol.isdigit() and len(symbol) == 4):
            data = await tw_fetcher.get_stock_data(symbol, period)
        else:
            data = us_fetcher.get_stock_data(symbol, period)
        
        if data is None or data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")

        indicators = indicator_analyzer.calculate_all_indicators(data)
        
        # 簡化的信號邏輯
        rsi = indicators.get('RSI', 50)
        signal = "HOLD"
        if rsi < 30:
            signal = "BUY"
        elif rsi > 70:
            signal = "SELL"
        
        return {
            "symbol": symbol,
            "signal": signal,
            "confidence": abs(50 - rsi) / 20,  # 簡化的信心度計算
            "indicators": clean_for_json(indicators),
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signals for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Signal generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)