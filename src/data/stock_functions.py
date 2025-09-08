#!/usr/bin/env python3
"""
股票數據函數 - 供 OpenAI Function Calling 使用
使用 Alpha Vantage API 獲取真實股票數據
"""

import os
import json
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

# Alpha Vantage API 配置
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")  # 免費 API Key
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

class StockDataFetcher:
    """股票數據獲取器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ALPHA_VANTAGE_API_KEY
        self.base_url = ALPHA_VANTAGE_BASE_URL
        self.last_request_time = 0
        self.request_interval = 12  # Alpha Vantage 免費版限制：每分鐘5次請求
    
    def _rate_limit(self):
        """API 請求頻率限制"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.request_interval:
            sleep_time = self.request_interval - time_since_last_request
            logger.info(f"Rate limiting: waiting {sleep_time:.1f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """發送 API 請求"""
        self._rate_limit()
        params['apikey'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 檢查 Alpha Vantage 錯誤
            if "Error Message" in data:
                raise Exception(f"Alpha Vantage error: {data['Error Message']}")
            if "Note" in data:
                raise Exception(f"API limit reached: {data['Note']}")
                
            return data
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise

def get_stock_quote(symbol: str) -> Dict[str, Any]:
    """
    獲取股票即時報價
    
    Args:
        symbol: 股票代碼 (例如: AAPL, GOOGL)
        
    Returns:
        包含股票基本信息的字典
    """
    logger.info(f"Fetching quote for {symbol}")
    fetcher = StockDataFetcher()
    
    try:
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }
        
        data = fetcher._make_request(params)
        
        if 'Global Quote' not in data:
            return {
                "error": f"No quote data found for {symbol}",
                "symbol": symbol
            }
        
        quote = data['Global Quote']
        
        result = {
            "symbol": quote.get('01. symbol', symbol),
            "price": float(quote.get('05. price', 0)),
            "change": float(quote.get('09. change', 0)),
            "change_percent": quote.get('10. change percent', '0%').replace('%', ''),
            "volume": int(quote.get('06. volume', 0)),
            "latest_trading_day": quote.get('07. latest trading day'),
            "previous_close": float(quote.get('08. previous close', 0)),
            "open": float(quote.get('02. open', 0)),
            "high": float(quote.get('03. high', 0)),
            "low": float(quote.get('04. low', 0))
        }
        
        logger.info(f"Successfully fetched quote for {symbol}: ${result['price']}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        return {
            "error": str(e),
            "symbol": symbol
        }

def get_stock_technical_indicators(symbol: str, indicator: str = "RSI", interval: str = "daily", time_period: int = 14) -> Dict[str, Any]:
    """
    獲取股票技術指標
    
    Args:
        symbol: 股票代碼
        indicator: 指標類型 (RSI, MACD, SMA, EMA)
        interval: 時間間隔 (daily, weekly, monthly)  
        time_period: 時間週期
        
    Returns:
        技術指標數據
    """
    logger.info(f"Fetching {indicator} for {symbol}")
    fetcher = StockDataFetcher()
    
    try:
        params = {
            'function': indicator,
            'symbol': symbol,
            'interval': interval,
            'time_period': time_period,
            'series_type': 'close'
        }
        
        data = fetcher._make_request(params)
        
        # 找到技術指標數據鍵
        indicator_key = None
        for key in data.keys():
            if 'Technical Analysis' in key:
                indicator_key = key
                break
        
        if not indicator_key:
            return {
                "error": f"No {indicator} data found for {symbol}",
                "symbol": symbol
            }
        
        indicator_data = data[indicator_key]
        
        # 獲取最新的幾個數據點
        recent_data = {}
        for date in sorted(indicator_data.keys(), reverse=True)[:5]:
            recent_data[date] = indicator_data[date]
        
        # 獲取最新值
        latest_date = max(indicator_data.keys())
        latest_values = indicator_data[latest_date]
        
        result = {
            "symbol": symbol,
            "indicator": indicator,
            "latest_date": latest_date,
            "latest_values": latest_values,
            "recent_data": recent_data
        }
        
        logger.info(f"Successfully fetched {indicator} for {symbol}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching {indicator} for {symbol}: {e}")
        return {
            "error": str(e),
            "symbol": symbol,
            "indicator": indicator
        }

def get_stock_daily_data(symbol: str, outputsize: str = "compact") -> Dict[str, Any]:
    """
    獲取股票每日歷史數據
    
    Args:
        symbol: 股票代碼
        outputsize: 數據量 ("compact" 最近100天, "full" 完整歷史)
        
    Returns:
        每日價格數據
    """
    logger.info(f"Fetching daily data for {symbol}")
    fetcher = StockDataFetcher()
    
    try:
        params = {
            'function': 'TIME_SERIES_DAILY_ADJUSTED',
            'symbol': symbol,
            'outputsize': outputsize
        }
        
        data = fetcher._make_request(params)
        
        if 'Time Series (Daily)' not in data:
            return {
                "error": f"No daily data found for {symbol}",
                "symbol": symbol
            }
        
        time_series = data['Time Series (Daily)']
        
        # 轉換為更好用的格式
        daily_data = []
        for date in sorted(time_series.keys(), reverse=True)[:30]:  # 最近30天
            day_data = time_series[date]
            daily_data.append({
                "date": date,
                "open": float(day_data['1. open']),
                "high": float(day_data['2. high']),
                "low": float(day_data['3. low']),
                "close": float(day_data['4. close']),
                "volume": int(day_data['6. volume'])
            })
        
        result = {
            "symbol": symbol,
            "data": daily_data,
            "latest_date": daily_data[0]['date'] if daily_data else None,
            "data_points": len(daily_data)
        }
        
        logger.info(f"Successfully fetched {len(daily_data)} days of data for {symbol}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching daily data for {symbol}: {e}")
        return {
            "error": str(e),
            "symbol": symbol
        }

def search_company_info(symbol: str) -> Dict[str, Any]:
    """
    搜索公司基本信息
    
    Args:
        symbol: 股票代碼
        
    Returns:
        公司基本信息
    """
    logger.info(f"Fetching company info for {symbol}")
    fetcher = StockDataFetcher()
    
    try:
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        
        data = fetcher._make_request(params)
        
        if not data or 'Symbol' not in data:
            return {
                "error": f"No company info found for {symbol}",
                "symbol": symbol
            }
        
        result = {
            "symbol": data.get('Symbol'),
            "name": data.get('Name'),
            "description": data.get('Description', '')[:200] + '...' if data.get('Description') else '',
            "industry": data.get('Industry'),
            "sector": data.get('Sector'),
            "market_cap": data.get('MarketCapitalization'),
            "pe_ratio": data.get('PERatio'),
            "dividend_yield": data.get('DividendYield'),
            "52_week_high": data.get('52WeekHigh'),
            "52_week_low": data.get('52WeekLow'),
            "analyst_target_price": data.get('AnalystTargetPrice'),
            "eps": data.get('EPS'),
            "beta": data.get('Beta')
        }
        
        logger.info(f"Successfully fetched company info for {symbol}: {result['name']}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {e}")
        return {
            "error": str(e),
            "symbol": symbol
        }

# Function Calling 用的函數定義
STOCK_FUNCTIONS = [
    {
        "name": "get_stock_quote",
        "description": "獲取股票的即時報價，包括當前價格、漲跌幅、成交量等基本信息",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代碼，例如 AAPL, GOOGL, MSFT"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "get_stock_technical_indicators", 
        "description": "獲取股票技術指標，如 RSI、MACD、移動平均等",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代碼"
                },
                "indicator": {
                    "type": "string",
                    "enum": ["RSI", "MACD", "SMA", "EMA"],
                    "description": "技術指標類型"
                },
                "interval": {
                    "type": "string", 
                    "enum": ["daily", "weekly", "monthly"],
                    "description": "時間間隔"
                },
                "time_period": {
                    "type": "integer",
                    "description": "時間週期，例如14天RSI"
                }
            },
            "required": ["symbol", "indicator"]
        }
    },
    {
        "name": "get_stock_daily_data",
        "description": "獲取股票的每日歷史價格數據，包括開高低收成交量",
        "parameters": {
            "type": "object", 
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代碼"
                },
                "outputsize": {
                    "type": "string",
                    "enum": ["compact", "full"],
                    "description": "數據量大小"
                }
            },
            "required": ["symbol"]
        }
    },
    {
        "name": "search_company_info",
        "description": "搜索公司基本信息，包括公司名稱、行業、市值、本益比等財務數據",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string", 
                    "description": "股票代碼"
                }
            },
            "required": ["symbol"]
        }
    }
]

# 函數映射
FUNCTION_MAP = {
    "get_stock_quote": get_stock_quote,
    "get_stock_technical_indicators": get_stock_technical_indicators, 
    "get_stock_daily_data": get_stock_daily_data,
    "search_company_info": search_company_info
}