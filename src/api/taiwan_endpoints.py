#!/usr/bin/env python3
"""
Enhanced Taiwan Stock Market API Endpoints
專門為台股市場設計的API端點，支援TWSE和TPEx
"""

from fastapi import FastAPI, HTTPException, Query, Path, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging
import pandas as pd
from enum import Enum

from ..data_fetcher.tw_stocks import TWStockDataFetcher
from ..analysis.technical_indicators import IndicatorAnalyzer
from ..visualization.tradingview_datafeed import setup_datafeed_routes

logger = logging.getLogger(__name__)

class TaiwanMarketEnum(str, Enum):
    """台灣市場類型"""
    TWSE = "TWSE"  # 上市
    TPEX = "TPEx"  # 上櫃

class StockTypeEnum(str, Enum):
    """股票類型"""
    STOCK = "stock"
    ETF = "etf" 
    INDEX = "index"
    WARRANT = "warrant"

class TaiwanStockInfo(BaseModel):
    """台股基本資訊"""
    symbol: str = Field(..., description="股票代號 (如: 2330.TW)")
    code: str = Field(..., description="純代號 (如: 2330)")
    name: str = Field(..., description="公司名稱")
    market: TaiwanMarketEnum = Field(..., description="交易市場")
    type: StockTypeEnum = Field(default=StockTypeEnum.STOCK, description="股票類型")
    industry: str = Field(default="", description="產業別")
    listing_date: Optional[datetime] = Field(None, description="上市日期")

class TaiwanQuoteData(BaseModel):
    """台股即時報價"""
    symbol: str
    code: str
    name: str
    current_price: float
    change: float
    change_percent: float
    volume: int
    high: float
    low: float
    open: float
    previous_close: float
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    timestamp: datetime
    market_open: bool

class TaiwanHistoricalRequest(BaseModel):
    """台股歷史數據請求"""
    symbol: str = Field(..., description="股票代號")
    start_date: Optional[str] = Field(None, description="開始日期 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="結束日期 (YYYY-MM-DD)")
    period: str = Field("3mo", description="數據期間 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)")
    include_indicators: bool = Field(True, description="包含技術指標")
    indicators: List[str] = Field(default=["sma_20", "sma_50", "rsi", "macd"], description="指標列表")

class TaiwanMarketOverview(BaseModel):
    """台股市場總覽"""
    market_status: str
    taiex_index: Optional[float] = None
    taiex_change: Optional[float] = None
    taiex_change_percent: Optional[float] = None
    tpex_index: Optional[float] = None
    tpex_change: Optional[float] = None
    tpex_change_percent: Optional[float] = None
    total_volume: Optional[int] = None
    advancing_stocks: Optional[int] = None
    declining_stocks: Optional[int] = None
    unchanged_stocks: Optional[int] = None
    timestamp: datetime

class TaiwanStockAPIEndpoints:
    """台股API端點類"""
    
    def __init__(self):
        self.tw_fetcher = TWStockDataFetcher()
        self.indicator_analyzer = IndicatorAnalyzer()
        
        # 台股代號對照表
        self.taiwan_stocks = {
            # TWSE 上市公司
            "2330": {"name": "台積電", "industry": "半導體", "market": "TWSE", "type": "stock"},
            "2317": {"name": "鴻海", "industry": "電子製造", "market": "TWSE", "type": "stock"},
            "2454": {"name": "聯發科", "industry": "半導體", "market": "TWSE", "type": "stock"},
            "2881": {"name": "富邦金", "industry": "金融保險", "market": "TWSE", "type": "stock"},
            "2412": {"name": "中華電", "industry": "通信網路", "market": "TWSE", "type": "stock"},
            "2603": {"name": "長榮", "industry": "航運", "market": "TWSE", "type": "stock"},
            "2002": {"name": "中鋼", "industry": "鋼鐵", "market": "TWSE", "type": "stock"},
            "1216": {"name": "統一", "industry": "食品", "market": "TWSE", "type": "stock"},
            "1301": {"name": "台塑", "industry": "塑膠", "market": "TWSE", "type": "stock"},
            
            # ETF
            "0050": {"name": "元大台灣50", "industry": "ETF", "market": "TWSE", "type": "etf"},
            "0056": {"name": "元大高股息", "industry": "ETF", "market": "TWSE", "type": "etf"}, 
            "006208": {"name": "富邦台50", "industry": "ETF", "market": "TWSE", "type": "etf"},
            "00677U": {"name": "富邦VIX", "industry": "ETF", "market": "TWSE", "type": "etf"},
            "00632R": {"name": "元大台灣50反1", "industry": "ETF", "market": "TWSE", "type": "etf"},
            
            # TPEx 上櫃公司
            "3481": {"name": "群創", "industry": "光電", "market": "TPEx", "type": "stock"},
            "5483": {"name": "中美晶", "industry": "半導體", "market": "TPEx", "type": "stock"},
            "6415": {"name": "矽力-KY", "industry": "半導體", "market": "TPEx", "type": "stock"},
            "4966": {"name": "譜瑞-KY", "industry": "半導體", "market": "TPEx", "type": "stock"},
        }
    
    def normalize_symbol(self, symbol: str) -> str:
        """標準化股票代號"""
        symbol = symbol.upper().strip()
        
        # 移除可能的後綴
        if symbol.endswith('.TW'):
            return symbol
        elif symbol.endswith('.TWO'):
            return symbol
        elif symbol.isdigit() and len(symbol) >= 4:
            # 判斷是上市還是上櫃
            code = symbol[:4] if len(symbol) > 4 else symbol
            if code in self.taiwan_stocks:
                market = self.taiwan_stocks[code]["market"]
                suffix = ".TW" if market == "TWSE" else ".TWO"
                return f"{code}{suffix}"
            else:
                # 預設為上市
                return f"{code}.TW"
        else:
            return symbol
    
    def get_stock_info(self, symbol: str) -> TaiwanStockInfo:
        """獲取股票基本資訊"""
        normalized = self.normalize_symbol(symbol)
        code = normalized.replace('.TW', '').replace('.TWO', '')
        
        if code in self.taiwan_stocks:
            stock_data = self.taiwan_stocks[code]
            return TaiwanStockInfo(
                symbol=normalized,
                code=code,
                name=stock_data["name"],
                market=TaiwanMarketEnum(stock_data["market"]),
                type=StockTypeEnum(stock_data["type"]),
                industry=stock_data["industry"]
            )
        else:
            # 未知股票，使用預設值
            market = TaiwanMarketEnum.TWSE if normalized.endswith('.TW') else TaiwanMarketEnum.TPEX
            return TaiwanStockInfo(
                symbol=normalized,
                code=code,
                name=f"台股 {code}",
                market=market,
                type=StockTypeEnum.STOCK,
                industry="未分類"
            )

def setup_taiwan_routes(app: FastAPI):
    """設定台股專用API路由"""
    
    tw_api = TaiwanStockAPIEndpoints()
    
    @app.get("/api/taiwan/market-overview", response_model=TaiwanMarketOverview)
    async def get_market_overview():
        """
        獲取台股市場總覽
        包含大盤指數、漲跌家數等資訊
        """
        try:
            market_open = tw_api.tw_fetcher.is_tw_market_open()
            
            # 這裡可以接入真實的大盤數據API
            # 暫時使用模擬數據
            return TaiwanMarketOverview(
                market_status="開盤中" if market_open else "休市",
                taiex_index=17250.45,
                taiex_change=125.30,
                taiex_change_percent=0.73,
                tpex_index=185.67,
                tpex_change=2.15,
                tpex_change_percent=1.17,
                total_volume=180000000,
                advancing_stocks=892,
                declining_stocks=567,
                unchanged_stocks=234,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"獲取市場總覽失敗: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/taiwan/stocks/search")
    async def search_taiwan_stocks(
        query: str = Query(..., description="搜尋關鍵字"),
        market: Optional[TaiwanMarketEnum] = Query(None, description="市場篩選"),
        limit: int = Query(20, description="返回結果數量限制")
    ) -> List[TaiwanStockInfo]:
        """
        搜尋台股
        支援代號、公司名稱、產業搜尋
        """
        try:
            results = []
            query_upper = query.upper()
            
            for code, stock_data in tw_api.taiwan_stocks.items():
                # 市場篩選
                if market and stock_data["market"] != market.value:
                    continue
                
                # 關鍵字匹配
                if (query_upper in code or 
                    query in stock_data["name"] or 
                    query in stock_data["industry"]):
                    
                    suffix = ".TW" if stock_data["market"] == "TWSE" else ".TWO"
                    symbol = f"{code}{suffix}"
                    
                    results.append(TaiwanStockInfo(
                        symbol=symbol,
                        code=code,
                        name=stock_data["name"],
                        market=TaiwanMarketEnum(stock_data["market"]),
                        type=StockTypeEnum(stock_data["type"]),
                        industry=stock_data["industry"]
                    ))
                
                if len(results) >= limit:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"搜尋台股失敗: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/taiwan/stocks/{symbol}/info", response_model=TaiwanStockInfo)
    async def get_stock_info(
        symbol: str = Path(..., description="股票代號")
    ):
        """
        獲取個股基本資訊
        """
        try:
            return tw_api.get_stock_info(symbol)
        except Exception as e:
            logger.error(f"獲取股票資訊失敗 {symbol}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/taiwan/stocks/{symbol}/quote", response_model=TaiwanQuoteData)
    async def get_stock_quote(
        symbol: str = Path(..., description="股票代號")
    ):
        """
        獲取個股即時報價
        """
        try:
            normalized_symbol = tw_api.normalize_symbol(symbol)
            stock_info = tw_api.get_stock_info(normalized_symbol)
            
            # 獲取即時報價
            quote = tw_api.tw_fetcher.get_real_time_quote(normalized_symbol)
            
            if quote:
                return TaiwanQuoteData(
                    symbol=normalized_symbol,
                    code=stock_info.code,
                    name=stock_info.name,
                    current_price=quote["price"],
                    change=quote["change"],
                    change_percent=quote["change_percent"],
                    volume=quote["volume"],
                    high=quote.get("high", quote["price"]),
                    low=quote.get("low", quote["price"]),
                    open=quote.get("open", quote["price"]),
                    previous_close=quote["price"] - quote["change"],
                    timestamp=quote["timestamp"],
                    market_open=tw_api.tw_fetcher.is_tw_market_open()
                )
            else:
                # 使用歷史數據作為後備
                end_date = datetime.now()
                start_date = end_date - timedelta(days=5)
                
                df = tw_api.tw_fetcher.fetch_historical_data(
                    normalized_symbol, start_date, end_date
                )
                
                if not df.empty:
                    latest = df.iloc[-1]
                    prev_close = df.iloc[-2]["close"] if len(df) > 1 else latest["close"]
                    
                    return TaiwanQuoteData(
                        symbol=normalized_symbol,
                        code=stock_info.code,
                        name=stock_info.name,
                        current_price=latest["close"],
                        change=latest["close"] - prev_close,
                        change_percent=((latest["close"] - prev_close) / prev_close) * 100,
                        volume=int(latest["volume"]),
                        high=latest["high"],
                        low=latest["low"],
                        open=latest["open"],
                        previous_close=prev_close,
                        timestamp=datetime.now(),
                        market_open=tw_api.tw_fetcher.is_tw_market_open()
                    )
                else:
                    raise HTTPException(status_code=404, detail=f"無法獲取 {symbol} 的報價數據")
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"獲取報價失敗 {symbol}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/taiwan/stocks/{symbol}/historical")
    async def get_historical_data(
        symbol: str = Path(..., description="股票代號"),
        request: TaiwanHistoricalRequest = None
    ):
        """
        獲取個股歷史數據
        支援技術指標計算
        """
        try:
            if request is None:
                request = TaiwanHistoricalRequest(symbol=symbol)
            
            normalized_symbol = tw_api.normalize_symbol(symbol)
            
            # 解析日期參數
            if request.start_date and request.end_date:
                start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
                end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
            else:
                # 根據period設定日期範圍
                end_date = datetime.now()
                period_mapping = {
                    "1d": 1, "5d": 5, "1mo": 30, "3mo": 90, 
                    "6mo": 180, "1y": 365, "2y": 730, "5y": 1825
                }
                days = period_mapping.get(request.period, 90)
                start_date = end_date - timedelta(days=days)
            
            # 獲取歷史數據
            df = tw_api.tw_fetcher.fetch_historical_data(
                normalized_symbol, start_date, end_date
            )
            
            if df.empty:
                raise HTTPException(status_code=404, detail=f"找不到 {symbol} 的歷史數據")
            
            # 計算技術指標
            if request.include_indicators:
                for indicator in request.indicators:
                    if indicator == "sma_20":
                        df['sma_20'] = df['close'].rolling(window=20).mean()
                    elif indicator == "sma_50":
                        df['sma_50'] = df['close'].rolling(window=50).mean()
                    elif indicator == "rsi":
                        df['rsi'] = tw_api.indicator_analyzer._calculate_rsi(df['close'])
                    elif indicator == "macd":
                        macd_data = tw_api.indicator_analyzer._calculate_macd(df['close'])
                        df['macd'] = macd_data['macd']
                        df['macd_signal'] = macd_data['signal']
                        df['macd_histogram'] = macd_data['histogram']
            
            # 轉換為JSON格式
            result = {
                "symbol": normalized_symbol,
                "period": request.period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "data_points": len(df),
                "data": []
            }
            
            for date, row in df.iterrows():
                data_point = {
                    "date": date.isoformat() if hasattr(date, 'isoformat') else str(date),
                    "open": float(row['open']) if pd.notna(row['open']) else None,
                    "high": float(row['high']) if pd.notna(row['high']) else None,
                    "low": float(row['low']) if pd.notna(row['low']) else None,
                    "close": float(row['close']) if pd.notna(row['close']) else None,
                    "volume": int(row['volume']) if pd.notna(row['volume']) else 0,
                }
                
                # 添加技術指標
                if request.include_indicators:
                    for indicator in request.indicators:
                        if indicator in df.columns and pd.notna(row[indicator]):
                            data_point[indicator] = float(row[indicator])
                
                result["data"].append(data_point)
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"獲取歷史數據失敗 {symbol}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/taiwan/stocks/popular")
    async def get_popular_stocks():
        """
        獲取熱門台股列表
        """
        try:
            popular_codes = ["2330", "2317", "2454", "2881", "2412", "0050", "0056"]
            results = []
            
            for code in popular_codes:
                try:
                    stock_info = tw_api.get_stock_info(code)
                    results.append(stock_info)
                except Exception as e:
                    logger.warning(f"獲取熱門股票 {code} 資訊失敗: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"獲取熱門股票列表失敗: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # 設定 TradingView Datafeed 路由
    setup_datafeed_routes(app)
    
    return app

# 示例使用
if __name__ == "__main__":
    # 測試用例
    tw_api = TaiwanStockAPIEndpoints()
    
    # 測試符號標準化
    test_symbols = ["2330", "2330.TW", "3481", "3481.TWO"]
    for symbol in test_symbols:
        normalized = tw_api.normalize_symbol(symbol)
        stock_info = tw_api.get_stock_info(symbol)
        print(f"{symbol} -> {normalized} -> {stock_info.name} ({stock_info.market})")