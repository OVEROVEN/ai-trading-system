#!/usr/bin/env python3
"""
TradingView Charting Library Datafeed Implementation
支援台股+美股統一前端的完整 Datafeed 架構
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse
import pandas as pd

# Import your existing data fetchers
from ..data_fetcher.us_stocks import USStockDataFetcher
from ..data_fetcher.tw_stocks import TWStockDataFetcher

logger = logging.getLogger(__name__)

@dataclass
class SymbolInfo:
    """TradingView 符號資訊格式"""
    symbol: str
    full_name: str
    description: str
    type: str  # "stock", "index", "forex", etc.
    session: str  # "24x7", "regular", "extended"
    timezone: str  # "Asia/Taipei", "America/New_York"
    ticker: str
    minmov: int = 1
    pricescale: int = 100
    has_intraday: bool = False
    has_weekly_and_monthly: bool = True
    supported_resolutions: List[str] = None
    volume_precision: int = 0
    data_status: str = "streaming"  # "streaming", "endofday", "pulsed", "delayed_streaming"

    def __post_init__(self):
        if self.supported_resolutions is None:
            self.supported_resolutions = ["1D", "1W", "1M"]

@dataclass 
class BarData:
    """TradingView K線數據格式"""
    time: int  # Unix timestamp in seconds
    open: float
    high: float
    low: float
    close: float
    volume: float = 0

class TradingViewDatafeed:
    """
    TradingView Charting Library Datafeed 實現
    支援美股+台股統一介面
    """
    
    def __init__(self):
        self.us_fetcher = USStockDataFetcher()
        self.tw_fetcher = TWStockDataFetcher()
        
        # 符號對照表
        self.symbol_mapping = {
            # 台股熱門股票
            "2330.TW": {"name": "台灣積體電路", "exchange": "TWSE", "type": "stock"},
            "2317.TW": {"name": "鴻海精密", "exchange": "TWSE", "type": "stock"},
            "2454.TW": {"name": "聯發科", "exchange": "TWSE", "type": "stock"},
            "2881.TW": {"name": "富邦金", "exchange": "TWSE", "type": "stock"},
            "0050.TW": {"name": "元大台灣50", "exchange": "TWSE", "type": "etf"},
            "00677U.TW": {"name": "富邦VIX", "exchange": "TWSE", "type": "etf"},
            
            # 上櫃股票 (TPEx) - 使用 .TWO 後綴
            "5483.TWO": {"name": "中美晶", "exchange": "TPEx", "type": "stock"},
            "3481.TWO": {"name": "群創", "exchange": "TPEx", "type": "stock"},
            
            # 美股
            "AAPL": {"name": "Apple Inc.", "exchange": "NASDAQ", "type": "stock"},
            "GOOGL": {"name": "Alphabet Inc.", "exchange": "NASDAQ", "type": "stock"},
            "MSFT": {"name": "Microsoft Corp.", "exchange": "NASDAQ", "type": "stock"},
            "TSLA": {"name": "Tesla Inc.", "exchange": "NASDAQ", "type": "stock"},
            "SPY": {"name": "SPDR S&P 500 ETF", "exchange": "NYSE", "type": "etf"},
            "QQQ": {"name": "Invesco QQQ Trust", "exchange": "NASDAQ", "type": "etf"},
        }
        
        # 時間範圍對應表
        self.resolution_mapping = {
            "1": "1m",
            "5": "5m", 
            "15": "15m",
            "30": "30m",
            "60": "1h",
            "1D": "1d",
            "1W": "1wk",
            "1M": "1mo"
        }
    
    def get_server_config(self) -> Dict[str, Any]:
        """
        返回 TradingView Datafeed 配置
        對應 TradingView 的 onReady 回調
        """
        return {
            "supports_search": True,
            "supports_group_request": False,
            "supports_marks": False,
            "supports_timescale_marks": False,
            "supports_time": True,
            "exchanges": [
                {"value": "TWSE", "name": "Taiwan Stock Exchange", "desc": "台灣證券交易所"},
                {"value": "TPEx", "name": "Taipei Exchange", "desc": "證券櫃檯買賣中心"},
                {"value": "NASDAQ", "name": "NASDAQ", "desc": "NASDAQ"},
                {"value": "NYSE", "name": "New York Stock Exchange", "desc": "NYSE"}
            ],
            "symbols_types": [
                {"name": "股票", "value": "stock"},
                {"name": "ETF", "value": "etf"},
                {"name": "指數", "value": "index"}
            ],
            "supported_resolutions": ["1", "5", "15", "30", "60", "1D", "1W", "1M"],
            "supports_resolution": True
        }
    
    def is_taiwan_symbol(self, symbol: str) -> bool:
        """判斷是否為台股符號"""
        return symbol.endswith('.TW') or symbol.endswith('.TWO')
    
    def normalize_symbol(self, symbol: str) -> str:
        """標準化符號格式"""
        symbol = symbol.upper().strip()
        
        # 台股數字代碼自動加上 .TW
        if symbol.isdigit() and len(symbol) == 4:
            return f"{symbol}.TW"
        
        return symbol
    
    async def search_symbols(self, query: str, exchange: str = "", limit: int = 30) -> List[Dict[str, Any]]:
        """
        符號搜尋功能
        對應 TradingView 的 searchSymbols
        """
        query = query.upper().strip()
        results = []
        
        for symbol, info in self.symbol_mapping.items():
            # 過濾交易所
            if exchange and info["exchange"] != exchange:
                continue
                
            # 符號或名稱匹配
            if (query in symbol or 
                query in info["name"].upper() or
                (self.is_taiwan_symbol(symbol) and query in symbol.replace('.TW', '').replace('.TWO', ''))):
                
                results.append({
                    "symbol": symbol,
                    "full_name": f"{info['exchange']}:{symbol}",
                    "description": info["name"],
                    "exchange": info["exchange"],
                    "ticker": symbol,
                    "type": info["type"]
                })
                
            if len(results) >= limit:
                break
        
        return results
    
    async def resolve_symbol(self, symbol: str) -> SymbolInfo:
        """
        解析符號資訊
        對應 TradingView 的 resolveSymbol
        """
        symbol = self.normalize_symbol(symbol)
        
        if symbol not in self.symbol_mapping:
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        info = self.symbol_mapping[symbol]
        
        # 根據市場設定時區和交易時段
        if self.is_taiwan_symbol(symbol):
            timezone = "Asia/Taipei"
            session = "0900-1330"  # 台股交易時間
        else:
            timezone = "America/New_York" 
            session = "0930-1600"  # 美股常規交易時間
        
        return SymbolInfo(
            symbol=symbol,
            full_name=f"{info['exchange']}:{symbol}",
            description=info["name"],
            type=info["type"],
            session=session,
            timezone=timezone,
            ticker=symbol,
            minmov=1,
            pricescale=100,
            has_intraday=False,  # 目前只支援日K
            has_weekly_and_monthly=True,
            supported_resolutions=["1D", "1W", "1M"],
            volume_precision=0,
            data_status="delayed_streaming"  # 延遲數據
        )
    
    async def get_bars(
        self,
        symbol: str,
        resolution: str,
        from_timestamp: int,
        to_timestamp: int,
        count_back: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        獲取 K線數據
        對應 TradingView 的 getBars
        """
        try:
            symbol = self.normalize_symbol(symbol)
            
            # 轉換時間戳
            start_date = datetime.fromtimestamp(from_timestamp)
            end_date = datetime.fromtimestamp(to_timestamp)
            
            # 根據符號類型選擇數據源
            if self.is_taiwan_symbol(symbol):
                df = self.tw_fetcher.fetch_historical_data(symbol, start_date, end_date)
            else:
                df = self.us_fetcher.fetch_historical_data(symbol, start_date, end_date)
            
            if df.empty:
                return {
                    "s": "no_data",
                    "nextTime": None
                }
            
            # 轉換為 TradingView 格式
            bars = []
            for index, row in df.iterrows():
                # 確保 index 是 datetime
                if isinstance(index, str):
                    timestamp = pd.to_datetime(index)
                else:
                    timestamp = index
                
                bar = BarData(
                    time=int(timestamp.timestamp()),
                    open=float(row.get('open', 0)),
                    high=float(row.get('high', 0)),
                    low=float(row.get('low', 0)),
                    close=float(row.get('close', 0)),
                    volume=float(row.get('volume', 0))
                )
                bars.append(bar)
            
            # 按時間排序
            bars.sort(key=lambda x: x.time)
            
            # 限制數量
            if count_back and len(bars) > count_back:
                bars = bars[-count_back:]
            
            # 轉換為 TradingView 格式
            result = {
                "s": "ok",
                "t": [bar.time for bar in bars],
                "o": [bar.open for bar in bars],
                "h": [bar.high for bar in bars],
                "l": [bar.low for bar in bars],
                "c": [bar.close for bar in bars],
                "v": [bar.volume for bar in bars]
            }
            
            # 如果數據不足，標記為 no_data
            if len(bars) == 0:
                result["s"] = "no_data"
            
            logger.info(f"返回 {len(bars)} 根 K線數據 for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"獲取 K線數據失敗 {symbol}: {str(e)}")
            return {"s": "error", "errmsg": str(e)}
    
    async def get_marks(self, symbol: str, from_timestamp: int, to_timestamp: int, resolution: str) -> List[Dict]:
        """
        獲取標記（可選實現）
        對應 TradingView 的 getMarks
        """
        # 暫時返回空標記
        return []
    
    async def get_timescale_marks(self, symbol: str, from_timestamp: int, to_timestamp: int, resolution: str) -> List[Dict]:
        """
        獲取時間軸標記（可選實現）
        對應 TradingView 的 getTimescaleMarks
        """
        # 暫時返回空標記
        return []

# FastAPI 路由設定
def setup_datafeed_routes(app: FastAPI):
    """設定 TradingView Datafeed API 路由"""
    
    datafeed = TradingViewDatafeed()
    
    @app.get("/api/tradingview/config")
    async def get_config():
        """獲取 Datafeed 配置"""
        return datafeed.get_server_config()
    
    @app.get("/api/tradingview/symbols")
    async def search_symbols(
        query: str = Query(..., description="搜尋關鍵字"),
        type: str = Query("", description="符號類型"),
        exchange: str = Query("", description="交易所"),
        limit: int = Query(30, description="最大結果數")
    ):
        """搜尋符號"""
        try:
            results = await datafeed.search_symbols(query, exchange, limit)
            return results
        except Exception as e:
            logger.error(f"搜尋符號失敗: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/tradingview/symbols/{symbol}")
    async def resolve_symbol(symbol: str = Path(..., description="股票符號")):
        """解析符號資訊"""
        try:
            symbol_info = await datafeed.resolve_symbol(symbol)
            return asdict(symbol_info)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"解析符號失敗 {symbol}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/tradingview/history")
    async def get_history(
        symbol: str = Query(..., description="股票符號"),
        resolution: str = Query("1D", description="時間週期"),
        from_time: int = Query(..., alias="from", description="開始時間戳"),
        to_time: int = Query(..., alias="to", description="結束時間戳"),
        countback: Optional[int] = Query(None, description="數據數量限制")
    ):
        """獲取歷史數據"""
        try:
            bars = await datafeed.get_bars(symbol, resolution, from_time, to_time, countback)
            return bars
        except Exception as e:
            logger.error(f"獲取歷史數據失敗 {symbol}: {str(e)}")
            return {"s": "error", "errmsg": str(e)}
    
    @app.get("/api/tradingview/marks")
    async def get_marks(
        symbol: str = Query(..., description="股票符號"),
        from_time: int = Query(..., alias="from", description="開始時間戳"),
        to_time: int = Query(..., alias="to", description="結束時間戳"),
        resolution: str = Query("1D", description="時間週期")
    ):
        """獲取標記"""
        try:
            marks = await datafeed.get_marks(symbol, from_time, to_time, resolution)
            return marks
        except Exception as e:
            logger.error(f"獲取標記失敗: {str(e)}")
            return []
    
    @app.get("/api/tradingview/time")
    async def get_server_time():
        """獲取服務器時間"""
        return {"timestamp": int(datetime.now().timestamp())}

# 示例使用
if __name__ == "__main__":
    # 測試 Datafeed
    async def test_datafeed():
        datafeed = TradingViewDatafeed()
        
        # 測試搜尋
        results = await datafeed.search_symbols("2330")
        print(f"搜尋結果: {results}")
        
        # 測試符號解析
        symbol_info = await datafeed.resolve_symbol("2330.TW")
        print(f"符號資訊: {symbol_info}")
        
        # 測試獲取 K線
        end_time = int(datetime.now().timestamp())
        start_time = end_time - (30 * 24 * 60 * 60)  # 30天前
        
        bars = await datafeed.get_bars("2330.TW", "1D", start_time, end_time)
        print(f"K線數據: {bars}")
    
    # 運行測試
    asyncio.run(test_datafeed())