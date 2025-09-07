#!/usr/bin/env python3
"""
TWSE/TPEx 開放資料 Datafeed 實現
專門為 TradingView Charting Library 設計
"""

import pandas as pd
import numpy as np
import requests
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import logging
from dataclasses import dataclass
import json
import time

logger = logging.getLogger(__name__)

@dataclass
class TWBar:
    """台股K線數據格式 (TradingView Charting Library 標準)"""
    time: int  # Unix timestamp in seconds
    open: float
    high: float
    low: float
    close: float
    volume: int

@dataclass
class TWSymbolInfo:
    """台股符號資訊"""
    symbol: str
    name: str
    exchange: str  # "TWSE" 或 "TPEx"
    type: str = "stock"
    timezone: str = "Asia/Taipei"
    session: str = "0900-1330"
    minmov: int = 1
    pricescale: int = 100
    has_intraday: bool = False
    supported_resolutions: List[str] = None

    def __post_init__(self):
        if self.supported_resolutions is None:
            self.supported_resolutions = ["1D"]

class TWStockDatafeed:
    """TWSE/TPEx 開放資料 Datafeed"""
    
    def __init__(self):
        self.base_urls = {
            "TWSE": "https://www.twse.com.tw/exchangeReport/",
            "TPEx": "https://www.tpex.org.tw/web/stock/"
        }
        
        # 台股代號對照表
        self.taiwan_stocks = {
            # TWSE 上市
            "2330": {"name": "台積電", "exchange": "TWSE"},
            "2317": {"name": "鴻海", "exchange": "TWSE"},
            "2454": {"name": "聯發科", "exchange": "TWSE"},
            "2881": {"name": "富邦金", "exchange": "TWSE"},
            "2412": {"name": "中華電", "exchange": "TWSE"},
            "2603": {"name": "長榮", "exchange": "TWSE"},
            "0050": {"name": "元大台灣50", "exchange": "TWSE"},
            "0056": {"name": "元大高股息", "exchange": "TWSE"},
            
            # TPEx 上櫃
            "3481": {"name": "群創", "exchange": "TPEx"},
            "5483": {"name": "中美晶", "exchange": "TPEx"},
            "6415": {"name": "矽力-KY", "exchange": "TPEx"},
        }
        
        # 快取機制
        self.cache = {}
        self.cache_ttl = 300  # 5分鐘快取
    
    def _get_cache_key(self, symbol: str, start_date: str, end_date: str) -> str:
        """生成快取鍵"""
        return f"tw_bars_{symbol}_{start_date}_{end_date}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """檢查快取是否有效"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp', 0)
        return (time.time() - cached_time) < self.cache_ttl
    
    def normalize_taiwan_symbol(self, symbol: str) -> tuple:
        """標準化台股符號並返回 (code, exchange)"""
        if symbol.endswith('.TW'):
            code = symbol[:-3]
            return code, "TWSE"
        elif symbol.endswith('.TWO'):
            code = symbol[:-4]  
            return code, "TPEx"
        else:
            # 純代號，查找對照表
            if symbol in self.taiwan_stocks:
                return symbol, self.taiwan_stocks[symbol]["exchange"]
            else:
                # 預設為上市
                return symbol, "TWSE"
    
    async def get_symbol_info(self, symbol: str) -> Optional[TWSymbolInfo]:
        """獲取台股符號資訊"""
        try:
            code, exchange = self.normalize_taiwan_symbol(symbol)
            
            if code in self.taiwan_stocks:
                stock_info = self.taiwan_stocks[code]
                return TWSymbolInfo(
                    symbol=f"{code}.{'TW' if exchange == 'TWSE' else 'TWO'}",
                    name=stock_info["name"],
                    exchange=exchange
                )
            else:
                # 未知股票，返回預設資訊
                return TWSymbolInfo(
                    symbol=f"{code}.{'TW' if exchange == 'TWSE' else 'TWO'}",
                    name=f"台股 {code}",
                    exchange=exchange
                )
        except Exception as e:
            logger.error(f"取得符號資訊失敗 {symbol}: {str(e)}")
            return None
    
    async def get_bars(
        self, 
        symbol: str, 
        from_timestamp: int, 
        to_timestamp: int,
        resolution: str = "1D"
    ) -> List[TWBar]:
        """獲取台股K線數據"""
        try:
            code, exchange = self.normalize_taiwan_symbol(symbol)
            
            start_date = datetime.fromtimestamp(from_timestamp).strftime('%Y%m%d')
            end_date = datetime.fromtimestamp(to_timestamp).strftime('%Y%m%d')
            
            # 檢查快取
            cache_key = self._get_cache_key(symbol, start_date, end_date)
            if self._is_cache_valid(cache_key):
                logger.info(f"使用快取數據: {symbol}")
                return self.cache[cache_key]['data']
            
            logger.info(f"從開放資料API獲取: {symbol} ({exchange})")
            
            if exchange == "TWSE":
                bars = await self._fetch_twse_data(code, from_timestamp, to_timestamp)
            else:
                bars = await self._fetch_tpex_data(code, from_timestamp, to_timestamp)
            
            # 儲存到快取
            self.cache[cache_key] = {
                'data': bars,
                'timestamp': time.time()
            }
            
            return bars
            
        except Exception as e:
            logger.error(f"獲取K線數據失敗 {symbol}: {str(e)}")
            return []
    
    async def _fetch_twse_data(self, code: str, from_ts: int, to_ts: int) -> List[TWBar]:
        """從 TWSE 開放資料API獲取數據"""
        bars = []
        
        try:
            current_date = datetime.fromtimestamp(from_ts)
            end_date = datetime.fromtimestamp(to_ts)
            
            async with aiohttp.ClientSession() as session:
                while current_date <= end_date:
                    date_str = current_date.strftime('%Y%m%d')
                    
                    # TWSE 每日交易資料API
                    url = f"{self.base_urls['TWSE']}MI_INDEX"
                    params = {
                        'response': 'json',
                        'date': date_str,
                        'type': 'ALLBUT0999'
                    }
                    
                    try:
                        async with session.get(url, params=params, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # 解析TWSE API回應
                                if 'data' in data and data['data']:
                                    for row in data['data']:
                                        if len(row) >= 9 and row[0] == code:
                                            try:
                                                bar = TWBar(
                                                    time=int(current_date.timestamp()),
                                                    open=self._parse_price(row[5]),
                                                    high=self._parse_price(row[6]),
                                                    low=self._parse_price(row[7]),
                                                    close=self._parse_price(row[8]),
                                                    volume=self._parse_volume(row[2])
                                                )
                                                bars.append(bar)
                                                logger.debug(f"TWSE數據: {code} {date_str} 收盤={bar.close}")
                                                break
                                            except Exception as e:
                                                logger.warning(f"解析TWSE數據失敗 {code} {date_str}: {str(e)}")
                    
                    except asyncio.TimeoutError:
                        logger.warning(f"TWSE API 逾時: {date_str}")
                    except Exception as e:
                        logger.warning(f"TWSE API 錯誤 {date_str}: {str(e)}")
                    
                    current_date += timedelta(days=1)
                    
                    # 避免請求過快
                    await asyncio.sleep(0.1)
        
        except Exception as e:
            logger.error(f"TWSE數據獲取失敗: {str(e)}")
        
        return bars
    
    async def _fetch_tpex_data(self, code: str, from_ts: int, to_ts: int) -> List[TWBar]:
        """從 TPEx 開放資料API獲取數據"""
        bars = []
        
        try:
            current_date = datetime.fromtimestamp(from_ts)
            end_date = datetime.fromtimestamp(to_ts)
            
            async with aiohttp.ClientSession() as session:
                while current_date <= end_date:
                    date_str = current_date.strftime('%Y/%m/%d')
                    
                    # TPEx 每日交易資料API
                    url = f"{self.base_urls['TPEx']}aftertrading/daily_trading_info/st43_result.php"
                    params = {
                        'l': 'zh-tw',
                        'd': date_str,
                        'stkno': code
                    }
                    
                    try:
                        async with session.get(url, params=params, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # 解析TPEx API回應
                                if 'aaData' in data and data['aaData']:
                                    for row in data['aaData']:
                                        if len(row) >= 6 and row[0] == code:
                                            try:
                                                bar = TWBar(
                                                    time=int(current_date.timestamp()),
                                                    open=self._parse_price(row[4]),
                                                    high=self._parse_price(row[5]),
                                                    low=self._parse_price(row[6]),
                                                    close=self._parse_price(row[2]),
                                                    volume=self._parse_volume(row[8])
                                                )
                                                bars.append(bar)
                                                logger.debug(f"TPEx數據: {code} {date_str} 收盤={bar.close}")
                                                break
                                            except Exception as e:
                                                logger.warning(f"解析TPEx數據失敗 {code} {date_str}: {str(e)}")
                    
                    except asyncio.TimeoutError:
                        logger.warning(f"TPEx API 逾時: {date_str}")
                    except Exception as e:
                        logger.warning(f"TPEx API 錯誤 {date_str}: {str(e)}")
                    
                    current_date += timedelta(days=1)
                    
                    # 避免請求過快
                    await asyncio.sleep(0.1)
        
        except Exception as e:
            logger.error(f"TPEx數據獲取失敗: {str(e)}")
        
        return bars
    
    def _parse_price(self, price_str: Union[str, float]) -> float:
        """解析價格字串"""
        try:
            if isinstance(price_str, (int, float)):
                return float(price_str)
            
            if isinstance(price_str, str):
                # 移除逗號和其他字符
                cleaned = price_str.replace(',', '').replace('--', '0').strip()
                if cleaned and cleaned != '--':
                    return float(cleaned)
            
            return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _parse_volume(self, volume_str: Union[str, int]) -> int:
        """解析成交量字串"""
        try:
            if isinstance(volume_str, (int, float)):
                return int(volume_str)
            
            if isinstance(volume_str, str):
                # 移除逗號和其他字符
                cleaned = volume_str.replace(',', '').replace('--', '0').strip()
                if cleaned and cleaned != '--':
                    return int(float(cleaned))
            
            return 0
        except (ValueError, TypeError):
            return 0
    
    async def search_symbols(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜尋台股符號"""
        results = []
        query_upper = query.upper()
        
        for code, info in self.taiwan_stocks.items():
            if (query_upper in code or 
                query in info["name"] or
                query_upper in info["name"].upper()):
                
                suffix = ".TW" if info["exchange"] == "TWSE" else ".TWO"
                results.append({
                    "symbol": f"{code}{suffix}",
                    "full_name": f"{info['exchange']}:{code}",
                    "description": info["name"],
                    "exchange": info["exchange"],
                    "type": "stock"
                })
                
                if len(results) >= limit:
                    break
        
        return results

# 全局實例
taiwan_datafeed = TWStockDatafeed()

def get_taiwan_datafeed() -> TWStockDatafeed:
    """獲取台股數據源實例"""
    return taiwan_datafeed

# 測試用例
async def test_taiwan_datafeed():
    """測試台股數據源"""
    datafeed = get_taiwan_datafeed()
    
    # 測試符號資訊
    symbol_info = await datafeed.get_symbol_info("2330.TW")
    print(f"符號資訊: {symbol_info}")
    
    # 測試K線數據
    end_time = int(datetime.now().timestamp())
    start_time = end_time - (30 * 24 * 60 * 60)  # 30天前
    
    bars = await datafeed.get_bars("2330.TW", start_time, end_time)
    print(f"獲取到 {len(bars)} 根K線")
    
    if bars:
        latest = bars[-1]
        print(f"最新數據: {datetime.fromtimestamp(latest.time)} 收盤={latest.close}")

if __name__ == "__main__":
    asyncio.run(test_taiwan_datafeed())