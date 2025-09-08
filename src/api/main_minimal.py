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

        # 嘗試獲取股票數據 - 如果失敗，只提供AI分析
        data = None
        data_available = False
        
        try:
            if symbol.endswith('.TW') or (symbol.isdigit() and len(symbol) == 4):
                # 台股
                if TW_FETCHER_AVAILABLE:
                    data = await tw_fetcher.get_stock_data(symbol, period)
            else:
                # 美股
                if US_FETCHER_AVAILABLE:
                    data = us_fetcher.get_stock_data(symbol, period)
            
            if data is not None and not data.empty:
                data_available = True
                logger.info(f"Stock data available for {symbol}")
            else:
                logger.warning(f"No stock data available for {symbol}, will provide AI-only analysis")
        
        except Exception as e:
            logger.warning(f"Stock data fetching failed for {symbol}: {e}, will provide AI-only analysis")

        # 如果有股票數據，進行技術分析
        if data_available:
            # 技術指標分析
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
        else:
            # 沒有股票數據時的基本結構
            analysis_result = {
                "symbol": symbol,
                "current_price": None,
                "price_change_1d": None,
                "volume_ratio": None,
                "period": period,
                "indicators": {"note": "Stock data not available"},
                "timestamp": datetime.now().isoformat(),
                "data_points": 0,
                "data_source": "ai_only"
            }

        # AI分析 - 總是嘗試提供AI分析，即使沒有明確請求
        if AI_AVAILABLE:
            try:
                # 使用簡化的 AI 分析
                ai_result = await ai_analyzer.get_simple_stock_suggestion(symbol, language)
                
                # 格式化為前端期望的結構
                analysis_result["ai_analysis"] = {
                    "recommendation": ai_result.recommendation,
                    "confidence": ai_result.confidence,
                    "reasoning": ai_result.reasoning,
                    "key_factors": ai_result.key_factors,
                    "price_target": ai_result.price_target,
                    "stop_loss": ai_result.stop_loss,
                    "entry_price": ai_result.entry_price,
                    "risk_score": ai_result.risk_score,
                    "analysis_type": ai_result.analysis_type,
                    "timestamp": ai_result.timestamp.isoformat()
                }
                logger.info(f"AI analysis completed successfully for {symbol}")
                
            except Exception as e:
                logger.warning(f"AI analysis failed for {symbol}: {e}")
                # 返回更有用的備用分析 - 適應有無股票數據的情況
                if data_available:
                    analysis_result["ai_analysis"] = {
                        "recommendation": "HOLD",
                        "confidence": 0.5,
                        "reasoning": f"基於技術指標，{symbol} 目前建議持有。當前價格 {current_price:.2f}，建議觀察市場動向。",
                        "key_factors": [
                            f"當前價格: ${current_price:.2f}",
                            f"日變化: {price_change_1d:+.2f}%",
                            f"成交量比率: {float(data['Volume'].iloc[-1] / data['Volume'].mean()):.2f}x",
                            "建議觀察支撐阻力位"
                        ],
                        "price_target": None,
                        "risk_score": 0.5,
                        "analysis_type": "fallback_with_data",
                        "timestamp": datetime.now().isoformat(),
                        "note": "AI analysis temporarily unavailable, using technical fallback"
                    }
                else:
                    # 提供更豐富的回退分析
                    symbol_name_map = {
                        "AAPL": "Apple Inc.",
                        "GOOGL": "Alphabet Inc.",
                        "MSFT": "Microsoft Corp.",
                        "TSLA": "Tesla Inc.",
                        "AMZN": "Amazon.com Inc.",
                        "META": "Meta Platforms Inc.",
                        "NVDA": "NVIDIA Corp.",
                        "NFLX": "Netflix Inc."
                    }
                    company_name = symbol_name_map.get(symbol, symbol)
                    
                    analysis_result["ai_analysis"] = {
                        "recommendation": "HOLD",
                        "confidence": 0.6,
                        "reasoning": f"基於 {company_name} 的長期基本面和市場地位，建議採取謹慎觀察策略。雖然即時數據暫時不可用，但該公司在行業中具有穩固地位。建議等待更多市場訊息後再做投資決策，同時關注公司最新財報和行業動態。",
                        "key_factors": [
                            f"{company_name} 在行業中具備競爭優勢",
                            "長期基本面相對穩健",
                            "建議關注最新財報發布",
                            "留意市場整體趨勢變化",
                            "等待技術分析數據恢復",
                            "考慮分批建倉降低風險",
                            "密切關注行業發展動向"
                        ],
                        "price_target": None,
                        "risk_score": 0.5,
                        "time_horizon": "中期",
                        "market_outlook": "整體市場存在不確定性，建議謹慎操作",
                        "analysis_type": "fallback_enhanced",
                        "timestamp": datetime.now().isoformat(),
                        "note": "Enhanced fallback analysis with market context"
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

# 簡化的認證端點（用於前端兼容性）
class AuthRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[dict] = None

@app.post("/api/auth/register")
async def register(request: AuthRequest):
    """簡化的用戶註冊（模擬）"""
    return {
        "access_token": "demo_token_" + str(datetime.now().timestamp()),
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": request.email,
            "full_name": request.username or "New User",
            "is_premium": False,
            "remaining_initial_quota": 100,
            "remaining_daily_quota": 50,
            "can_use_ai_analysis": True,
            "credits": 100
        }
    }

@app.post("/api/auth/login")
async def login(request: AuthRequest):
    """簡化的用戶登入（模擬）"""
    return {
        "access_token": "demo_token_" + str(datetime.now().timestamp()),
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": request.email,
            "full_name": "Demo User",
            "is_premium": True,
            "remaining_initial_quota": 50,
            "remaining_daily_quota": 25,
            "can_use_ai_analysis": True,
            "credits": 100
        }
    }

@app.get("/api/auth/me")
async def get_user():
    """獲取用戶信息（模擬）"""
    return {
        "id": 1,
        "email": "demo@example.com",
        "full_name": "Demo User",
        "is_premium": True,
        "remaining_initial_quota": 50,
        "remaining_daily_quota": 25,
        "can_use_ai_analysis": True,
        "credits": 100,
        "subscription": "premium"
    }

@app.get("/api/auth/google/login")
async def google_oauth_login(
    redirect_uri: str = "https://auto-trade-frontend-610357573971.asia-northeast1.run.app/auth/google/callback"
):
    """Google OAuth 登入端點（真實實現）"""
    try:
        # 導入 OAuth 模組
        from src.auth.oauth import google_oauth, oauth_state_manager
        
        if not google_oauth.is_configured():
            logger.warning("Google OAuth not configured, using demo mode")
            return {
                "authorization_url": "https://demo-oauth-disabled.local/login",
                "state": "demo_oauth_disabled",
                "error": "Google OAuth client may be deleted or invalid",
                "note": "Please contact administrator to reconfigure Google OAuth credentials"
            }
        
        # 創建狀態參數用於 CSRF 保護
        state = oauth_state_manager.create_state(redirect_uri)
        
        # 生成授權 URL
        auth_url = google_oauth.get_authorization_url(redirect_uri, state)
        
        return {
            "authorization_url": auth_url,
            "state": state,
            "redirect_uri": redirect_uri
        }
        
    except ImportError as e:
        logger.warning(f"OAuth module not available: {e}")
        # 降級到模擬模式
        return {
            "authorization_url": "https://accounts.google.com/oauth/demo?state=demo_" + str(datetime.now().timestamp()),
            "state": "demo_state_" + str(datetime.now().timestamp()),
            "note": "OAuth module not available, using demo mode"
        }

class GoogleCallbackRequest(BaseModel):
    code: str
    state: str
    redirect_uri: str = "https://auto-trade-frontend-610357573971.asia-northeast1.run.app/auth/google/callback"

@app.post("/api/auth/google/callback")
async def google_oauth_callback(request: GoogleCallbackRequest):
    """Google OAuth 回調處理（真實實現）"""
    try:
        from src.auth.oauth import google_oauth, oauth_state_manager
        
        # 驗證狀態參數
        state_data = oauth_state_manager.verify_state(request.state)
        if not state_data:
            raise HTTPException(status_code=400, detail="無效的狀態參數")
        
        # 使用授權碼交換訪問令牌
        token_data = await google_oauth.exchange_code_for_token(request.code, request.redirect_uri)
        
        # 獲取用戶信息
        user_info = await google_oauth.get_user_info(token_data["access_token"])
        
        # 返回用戶數據（簡化版本，不涉及數據庫）
        return {
            "access_token": "google_oauth_" + str(datetime.now().timestamp()),
            "token_type": "bearer",
            "user": {
                "id": int(user_info.get("id", "1")),
                "email": user_info.get("email"),
                "full_name": user_info.get("name", "Google User"),
                "is_premium": True,
                "remaining_initial_quota": 100,
                "remaining_daily_quota": 50,
                "can_use_ai_analysis": True,
                "credits": 100,
                "avatar_url": user_info.get("picture")
            }
        }
        
    except ImportError as e:
        logger.warning(f"OAuth module not available: {e}")
        # 降級到模擬模式
        return {
            "access_token": "google_demo_token_" + str(datetime.now().timestamp()),
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": "demo@gmail.com",
                "full_name": "Google Demo User",
                "is_premium": True,
                "remaining_initial_quota": 75,
                "remaining_daily_quota": 35,
                "can_use_ai_analysis": True,
                "credits": 100
            },
            "note": "OAuth module not available, using demo mode"
        }

# 添加 OAuth 狀態檢查端點
@app.get("/api/auth/oauth/status")
async def oauth_status():
    """檢查 OAuth 配置狀態"""
    try:
        from src.auth.oauth import google_oauth
        return {
            "google_oauth_available": google_oauth.is_configured(),
            "google_client_id_configured": bool(google_oauth.client_id),
            "client_id_preview": google_oauth.client_id[:20] + "..." if google_oauth.client_id else None,
            "status": "configured" if google_oauth.is_configured() else "missing_credentials"
        }
    except ImportError:
        return {
            "google_oauth_available": False,
            "status": "module_not_available"
        }

# 同時改進AI分析，使用OpenAI直接搜索和分析
@app.post("/api/ai-analysis")
async def ai_analysis_with_search(request: StockAnalysisRequest):
    """使用OpenAI進行智能股票分析（含網路搜索）"""
    if not AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI analysis service unavailable")
    
    try:
        symbol = request.symbol
        language = request.language
        
        # 使用AI analyzer的簡化分析功能
        result = await ai_analyzer.get_simple_stock_suggestion(symbol, language)
        
        return {
            "symbol": symbol,
            "analysis": result,
            "timestamp": datetime.now().isoformat(),
            "source": "OpenAI GPT-4",
            "method": "web_search_analysis"
        }
    
    except Exception as e:
        logger.error(f"AI analysis failed for {symbol}: {e}")
        # 返回備用分析
        return {
            "symbol": symbol,
            "analysis": {
                "recommendation": "HOLD",
                "confidence": 0.5,
                "reasoning": f"基於當前市場情況，{symbol} 建議持有觀望。請注意市場風險。",
                "price_target": None
            },
            "timestamp": datetime.now().isoformat(),
            "source": "Fallback Analysis",
            "method": "basic_analysis"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)