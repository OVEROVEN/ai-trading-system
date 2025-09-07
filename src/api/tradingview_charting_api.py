#!/usr/bin/env python3
"""
TradingView Charting Library API for Taiwan Stocks
專門為台股設計的完整 Charting Library 後端
"""

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime
import json

from ..data_fetcher.twse_tpex_datafeed import get_taiwan_datafeed, TWStockDatafeed

logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/api/charting", tags=["TradingView Charting Library"])

# 獲取台股數據源
tw_datafeed = get_taiwan_datafeed()

@router.get("/config")
async def get_charting_config():
    """
    TradingView Charting Library 配置端點
    對應 onReady 回調
    """
    config = {
        "supports_search": True,
        "supports_group_request": False,
        "supports_marks": False,
        "supports_timescale_marks": False,
        "supports_time": True,
        "exchanges": [
            {
                "value": "TWSE",
                "name": "Taiwan Stock Exchange",
                "desc": "台灣證券交易所"
            },
            {
                "value": "TPEx", 
                "name": "Taipei Exchange",
                "desc": "證券櫃檯買賣中心"
            }
        ],
        "symbols_types": [
            {"name": "股票", "value": "stock"},
            {"name": "ETF", "value": "etf"}
        ],
        "supported_resolutions": ["1D"],
        "supports_resolution": True
    }
    
    return JSONResponse(content=config)

@router.get("/symbols")
async def search_symbols(
    query: str = Query(..., description="搜尋關鍵字"),
    type: str = Query("", description="符號類型"),
    exchange: str = Query("", description="交易所"),
    limit: int = Query(30, description="最大結果數")
):
    """
    符號搜尋端點
    對應 searchSymbols 回調
    """
    try:
        results = await tw_datafeed.search_symbols(query, limit)
        
        # 過濾結果
        if exchange:
            results = [r for r in results if r["exchange"] == exchange]
        
        if type:
            results = [r for r in results if r["type"] == type]
        
        return JSONResponse(content=results[:limit])
        
    except Exception as e:
        logger.error(f"符號搜尋失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols/{symbol}")
async def resolve_symbol(symbol: str):
    """
    符號解析端點
    對應 resolveSymbol 回調
    """
    try:
        symbol_info = await tw_datafeed.get_symbol_info(symbol)
        
        if not symbol_info:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        response = {
            "symbol": symbol_info.symbol,
            "full_name": f"{symbol_info.exchange}:{symbol_info.symbol}",
            "description": symbol_info.name,
            "type": symbol_info.type,
            "session": symbol_info.session,
            "timezone": symbol_info.timezone,
            "ticker": symbol_info.symbol,
            "minmov": symbol_info.minmov,
            "pricescale": symbol_info.pricescale,
            "has_intraday": symbol_info.has_intraday,
            "has_weekly_and_monthly": True,
            "supported_resolutions": symbol_info.supported_resolutions,
            "volume_precision": 0,
            "data_status": "delayed_streaming"
        }
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"符號解析失敗 {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_history(
    symbol: str = Query(..., description="股票符號"),
    resolution: str = Query("1D", description="時間週期"),
    from_time: int = Query(..., alias="from", description="開始時間戳"),
    to_time: int = Query(..., alias="to", description="結束時間戳"),
    countback: Optional[int] = Query(None, description="數據數量限制")
):
    """
    歷史數據端點
    對應 getBars 回調
    """
    try:
        logger.info(f"獲取歷史數據: {symbol}, {resolution}, {from_time}-{to_time}")
        
        # 獲取K線數據
        bars = await tw_datafeed.get_bars(symbol, from_time, to_time, resolution)
        
        if not bars:
            return JSONResponse(content={
                "s": "no_data",
                "nextTime": None
            })
        
        # 排序並限制數量
        bars.sort(key=lambda x: x.time)
        if countback and len(bars) > countback:
            bars = bars[-countback:]
        
        # 轉換為 TradingView 格式
        response = {
            "s": "ok",
            "t": [bar.time for bar in bars],
            "o": [bar.open for bar in bars],
            "h": [bar.high for bar in bars],
            "l": [bar.low for bar in bars],
            "c": [bar.close for bar in bars],
            "v": [bar.volume for bar in bars]
        }
        
        logger.info(f"返回 {len(bars)} 根K線數據")
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"獲取歷史數據失敗 {symbol}: {str(e)}")
        return JSONResponse(content={
            "s": "error", 
            "errmsg": str(e)
        })

@router.get("/marks")
async def get_marks(
    symbol: str = Query(..., description="股票符號"),
    from_time: int = Query(..., alias="from", description="開始時間戳"),
    to_time: int = Query(..., alias="to", description="結束時間戳"),
    resolution: str = Query("1D", description="時間週期")
):
    """
    標記端點
    對應 getMarks 回調 (可選)
    """
    # 暫時返回空標記
    return JSONResponse(content=[])

@router.get("/timescale_marks")
async def get_timescale_marks(
    symbol: str = Query(..., description="股票符號"),
    from_time: int = Query(..., alias="from", description="開始時間戳"),
    to_time: int = Query(..., alias="to", description="結束時間戳"),
    resolution: str = Query("1D", description="時間週期")
):
    """
    時間軸標記端點
    對應 getTimescaleMarks 回調 (可選)
    """
    # 暫時返回空標記
    return JSONResponse(content=[])

@router.get("/server_time")
async def get_server_time():
    """
    服務器時間端點
    對應 getServerTime 回調
    """
    return JSONResponse(content={
        "timestamp": int(datetime.now().timestamp())
    })

# 用於測試的端點
@router.get("/test/{symbol}")
async def test_symbol_data(symbol: str):
    """測試台股符號數據獲取"""
    try:
        # 測試符號資訊
        symbol_info = await tw_datafeed.get_symbol_info(symbol)
        
        # 測試歷史數據
        end_time = int(datetime.now().timestamp())
        start_time = end_time - (30 * 24 * 60 * 60)  # 30天前
        
        bars = await tw_datafeed.get_bars(symbol, start_time, end_time)
        
        return {
            "symbol_info": symbol_info.__dict__ if symbol_info else None,
            "bars_count": len(bars),
            "latest_bar": bars[-1].__dict__ if bars else None,
            "test_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"測試失敗 {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def setup_charting_routes(app):
    """將 Charting Library 路由添加到 FastAPI 應用"""
    app.include_router(router)
    return app

# 測試用例
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    
    app = FastAPI(title="TradingView Charting Library API for Taiwan Stocks")
    setup_charting_routes(app)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)