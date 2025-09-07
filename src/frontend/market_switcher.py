#!/usr/bin/env python3
"""
Market Switcher - 美股/台股市場切換機制
提供統一的前端介面切換美股和台股市場
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, time
from dataclasses import dataclass
import pytz
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class MarketType(str, Enum):
    """市場類型"""
    US = "US"
    TAIWAN = "TW"
    AUTO = "AUTO"

class MarketStatus(str, Enum):
    """市場狀態"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PRE_MARKET = "PRE_MARKET"
    AFTER_HOURS = "AFTER_HOURS"
    HOLIDAY = "HOLIDAY"

@dataclass
class MarketInfo:
    """市場資訊"""
    market_type: MarketType
    name: str
    timezone: str
    regular_hours: str
    pre_market_hours: str
    after_hours: str
    currency: str
    status: MarketStatus
    next_open: Optional[datetime] = None
    next_close: Optional[datetime] = None

@dataclass
class SymbolInfo:
    """股票代號資訊"""
    symbol: str
    display_name: str
    market: MarketType
    exchange: str
    currency: str
    sector: str = ""
    is_etf: bool = False

class MarketSwitcher:
    """市場切換器"""
    
    def __init__(self):
        self.current_market = MarketType.AUTO
        
        # 市場基本資訊
        self.markets = {
            MarketType.US: MarketInfo(
                market_type=MarketType.US,
                name="美國股市",
                timezone="America/New_York",
                regular_hours="09:30-16:00",
                pre_market_hours="04:00-09:30",
                after_hours="16:00-20:00",
                currency="USD",
                status=MarketStatus.CLOSED
            ),
            MarketType.TAIWAN: MarketInfo(
                market_type=MarketType.TAIWAN,
                name="台灣股市",
                timezone="Asia/Taipei",
                regular_hours="09:00-13:30",
                pre_market_hours="",
                after_hours="",
                currency="TWD",
                status=MarketStatus.CLOSED
            )
        }
        
        # 預設股票清單
        self.default_symbols = {
            MarketType.US: [
                SymbolInfo("AAPL", "Apple Inc.", MarketType.US, "NASDAQ", "USD", "Technology"),
                SymbolInfo("GOOGL", "Alphabet Inc.", MarketType.US, "NASDAQ", "USD", "Technology"),
                SymbolInfo("MSFT", "Microsoft Corp.", MarketType.US, "NASDAQ", "USD", "Technology"),
                SymbolInfo("TSLA", "Tesla Inc.", MarketType.US, "NASDAQ", "USD", "Consumer Discretionary"),
                SymbolInfo("AMZN", "Amazon.com Inc.", MarketType.US, "NASDAQ", "USD", "Consumer Discretionary"),
                SymbolInfo("META", "Meta Platforms Inc.", MarketType.US, "NASDAQ", "USD", "Communication"),
                SymbolInfo("NVDA", "NVIDIA Corp.", MarketType.US, "NASDAQ", "USD", "Technology"),
                SymbolInfo("SPY", "SPDR S&P 500 ETF", MarketType.US, "NYSE", "USD", "ETF", True),
                SymbolInfo("QQQ", "Invesco QQQ Trust", MarketType.US, "NASDAQ", "USD", "ETF", True),
            ],
            MarketType.TAIWAN: [
                SymbolInfo("2330.TW", "台積電", MarketType.TAIWAN, "TWSE", "TWD", "半導體"),
                SymbolInfo("2317.TW", "鴻海", MarketType.TAIWAN, "TWSE", "TWD", "電子製造"),
                SymbolInfo("2454.TW", "聯發科", MarketType.TAIWAN, "TWSE", "TWD", "半導體"),
                SymbolInfo("2881.TW", "富邦金", MarketType.TAIWAN, "TWSE", "TWD", "金融保險"),
                SymbolInfo("2412.TW", "中華電", MarketType.TAIWAN, "TWSE", "TWD", "通信網路"),
                SymbolInfo("2603.TW", "長榮", MarketType.TAIWAN, "TWSE", "TWD", "航運"),
                SymbolInfo("0050.TW", "元大台灣50", MarketType.TAIWAN, "TWSE", "TWD", "ETF", True),
                SymbolInfo("0056.TW", "元大高股息", MarketType.TAIWAN, "TWSE", "TWD", "ETF", True),
                SymbolInfo("3481.TWO", "群創", MarketType.TAIWAN, "TPEx", "TWD", "光電"),
            ]
        }
        
        # 更新市場狀態
        self._update_market_status()
    
    def _update_market_status(self):
        """更新市場狀態"""
        # 更新美股狀態
        us_status = self._get_us_market_status()
        self.markets[MarketType.US].status = us_status
        
        # 更新台股狀態
        tw_status = self._get_taiwan_market_status()
        self.markets[MarketType.TAIWAN].status = tw_status
    
    def _get_us_market_status(self) -> MarketStatus:
        """獲取美股市場狀態"""
        try:
            eastern = pytz.timezone('America/New_York')
            now = datetime.now(eastern)
            current_time = now.time()
            
            # 檢查是否為工作日
            if now.weekday() >= 5:  # 週末
                return MarketStatus.CLOSED
            
            # 常規交易時間 9:30-16:00
            if time(9, 30) <= current_time <= time(16, 0):
                return MarketStatus.OPEN
            # 盤前交易 4:00-9:30
            elif time(4, 0) <= current_time < time(9, 30):
                return MarketStatus.PRE_MARKET
            # 盤後交易 16:00-20:00
            elif time(16, 0) < current_time <= time(20, 0):
                return MarketStatus.AFTER_HOURS
            else:
                return MarketStatus.CLOSED
                
        except Exception as e:
            logger.error(f"獲取美股狀態失敗: {str(e)}")
            return MarketStatus.CLOSED
    
    def _get_taiwan_market_status(self) -> MarketStatus:
        """獲取台股市場狀態"""
        try:
            taipei = pytz.timezone('Asia/Taipei')
            now = datetime.now(taipei)
            current_time = now.time()
            
            # 檢查是否為工作日
            if now.weekday() >= 5:  # 週末
                return MarketStatus.CLOSED
            
            # 常規交易時間 9:00-13:30
            if time(9, 0) <= current_time <= time(13, 30):
                return MarketStatus.OPEN
            else:
                return MarketStatus.CLOSED
                
        except Exception as e:
            logger.error(f"獲取台股狀態失敗: {str(e)}")
            return MarketStatus.CLOSED
    
    def switch_market(self, market_type: MarketType) -> Dict[str, Any]:
        """切換市場"""
        self.current_market = market_type
        self._update_market_status()
        
        return {
            "success": True,
            "current_market": market_type.value,
            "market_info": self._get_market_config(market_type),
            "default_symbols": self._get_default_symbols(market_type),
            "timestamp": datetime.now().isoformat()
        }
    
    def auto_detect_market(self, symbol: str) -> MarketType:
        """自動偵測符號所屬市場"""
        symbol = symbol.upper().strip()
        
        if symbol.endswith('.TW') or symbol.endswith('.TWO'):
            return MarketType.TAIWAN
        elif symbol.isdigit() and len(symbol) == 4:
            # 4位數字，可能是台股
            return MarketType.TAIWAN
        else:
            # 其他情況預設為美股
            return MarketType.US
    
    def get_optimal_market(self) -> MarketType:
        """獲取最佳市場 (基於當前時間)"""
        self._update_market_status()
        
        us_status = self.markets[MarketType.US].status
        tw_status = self.markets[MarketType.TAIWAN].status
        
        # 優先選擇開市的市場
        if us_status == MarketStatus.OPEN:
            return MarketType.US
        elif tw_status == MarketStatus.OPEN:
            return MarketType.TAIWAN
        # 如果都不開市，選擇有盤前/盤後交易的市場
        elif us_status in [MarketStatus.PRE_MARKET, MarketStatus.AFTER_HOURS]:
            return MarketType.US
        else:
            # 都休市時，根據時區選擇較接近開市的市場
            return self._get_next_open_market()
    
    def _get_next_open_market(self) -> MarketType:
        """獲取下一個開市的市場"""
        utc_now = datetime.now(pytz.UTC)
        
        # 計算到各市場開市的時間
        eastern = pytz.timezone('America/New_York')
        taipei = pytz.timezone('Asia/Taipei')
        
        # 美股開市時間 (9:30 AM ET)
        us_open = utc_now.astimezone(eastern).replace(hour=9, minute=30, second=0, microsecond=0)
        if us_open <= utc_now.astimezone(eastern):
            us_open += pytz.timedelta(days=1)
        
        # 台股開市時間 (9:00 AM CST)
        tw_open = utc_now.astimezone(taipei).replace(hour=9, minute=0, second=0, microsecond=0)
        if tw_open <= utc_now.astimezone(taipei):
            tw_open += pytz.timedelta(days=1)
        
        # 轉換為UTC進行比較
        us_open_utc = us_open.astimezone(pytz.UTC)
        tw_open_utc = tw_open.astimezone(pytz.UTC)
        
        return MarketType.US if us_open_utc < tw_open_utc else MarketType.TAIWAN
    
    def _get_market_config(self, market_type: MarketType) -> Dict[str, Any]:
        """獲取市場配置"""
        if market_type == MarketType.AUTO:
            market_type = self.get_optimal_market()
        
        market_info = self.markets[market_type]
        
        return {
            "type": market_type.value,
            "name": market_info.name,
            "timezone": market_info.timezone,
            "currency": market_info.currency,
            "trading_hours": market_info.regular_hours,
            "pre_market": market_info.pre_market_hours,
            "after_hours": market_info.after_hours,
            "status": market_info.status.value,
            "is_open": market_info.status == MarketStatus.OPEN
        }
    
    def _get_default_symbols(self, market_type: MarketType) -> List[Dict[str, Any]]:
        """獲取預設股票清單"""
        if market_type == MarketType.AUTO:
            market_type = self.get_optimal_market()
        
        symbols = self.default_symbols.get(market_type, [])
        return [
            {
                "symbol": sym.symbol,
                "name": sym.display_name,
                "exchange": sym.exchange,
                "currency": sym.currency,
                "sector": sym.sector,
                "is_etf": sym.is_etf
            }
            for sym in symbols
        ]
    
    def get_current_market_info(self) -> Dict[str, Any]:
        """獲取當前市場資訊"""
        current_market = self.current_market
        if current_market == MarketType.AUTO:
            current_market = self.get_optimal_market()
        
        return {
            "current_market": current_market.value,
            "market_config": self._get_market_config(current_market),
            "all_markets": {
                "US": self._get_market_config(MarketType.US),
                "TW": self._get_market_config(MarketType.TAIWAN)
            },
            "optimal_market": self.get_optimal_market().value
        }
    
    def normalize_symbol_for_market(self, symbol: str, target_market: MarketType = None) -> str:
        """為特定市場標準化符號"""
        if target_market is None:
            target_market = self.auto_detect_market(symbol)
        
        symbol = symbol.upper().strip()
        
        if target_market == MarketType.TAIWAN:
            # 台股符號處理
            if symbol.endswith('.TW') or symbol.endswith('.TWO'):
                return symbol
            elif symbol.isdigit() and len(symbol) == 4:
                # 預設為上市股票
                return f"{symbol}.TW"
            else:
                return symbol
        else:
            # 美股符號處理
            if symbol.endswith('.TW') or symbol.endswith('.TWO'):
                # 移除台股後綴
                return symbol.split('.')[0]
            return symbol
    
    def get_tradingview_symbol(self, symbol: str) -> str:
        """獲取 TradingView 格式的符號"""
        market = self.auto_detect_market(symbol)
        normalized = self.normalize_symbol_for_market(symbol, market)
        
        if market == MarketType.TAIWAN:
            if normalized.endswith('.TW'):
                code = normalized[:-3]
                return f"TPE:{code}"
            elif normalized.endswith('.TWO'):
                code = normalized[:-4]
                return f"TPX:{code}"  # TPEx 符號
            else:
                return f"TPE:{normalized}"
        else:
            return normalized
    
    def create_market_switch_html(self) -> str:
        """創建市場切換的 HTML 界面組件"""
        current_info = self.get_current_market_info()
        
        return f"""
        <div class="market-switcher" style="
            display: flex; 
            align-items: center; 
            gap: 10px; 
            padding: 10px; 
            background: rgba(0,0,0,0.1); 
            border-radius: 8px;
            margin-bottom: 15px;
        ">
            <div class="market-status">
                <span style="font-size: 12px; color: #6c757d;">當前市場:</span>
                <span style="font-weight: 600; color: #007bff;">
                    {current_info['market_config']['name']}
                </span>
                <span class="status-indicator" style="
                    display: inline-block;
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: {'#28a745' if current_info['market_config']['is_open'] else '#dc3545'};
                    margin-left: 5px;
                "></span>
            </div>
            
            <div class="market-buttons" style="display: flex; gap: 5px;">
                <button onclick="switchMarket('US')" 
                        class="market-btn {'active' if current_info['current_market'] == 'US' else ''}"
                        style="
                            padding: 4px 8px;
                            border: 1px solid #007bff;
                            border-radius: 4px;
                            background: {'#007bff' if current_info['current_market'] == 'US' else 'transparent'};
                            color: {'white' if current_info['current_market'] == 'US' else '#007bff'};
                            font-size: 11px;
                            cursor: pointer;
                        ">
                    美股 ({current_info['all_markets']['US']['status']})
                </button>
                
                <button onclick="switchMarket('TW')" 
                        class="market-btn {'active' if current_info['current_market'] == 'TW' else ''}"
                        style="
                            padding: 4px 8px;
                            border: 1px solid #007bff;
                            border-radius: 4px;
                            background: {'#007bff' if current_info['current_market'] == 'TW' else 'transparent'};
                            color: {'white' if current_info['current_market'] == 'TW' else '#007bff'};
                            font-size: 11px;
                            cursor: pointer;
                        ">
                    台股 ({current_info['all_markets']['TW']['status']})
                </button>
                
                <button onclick="switchMarket('AUTO')" 
                        class="market-btn {'active' if current_info['current_market'] == 'AUTO' else ''}"
                        style="
                            padding: 4px 8px;
                            border: 1px solid #28a745;
                            border-radius: 4px;
                            background: {'#28a745' if current_info['current_market'] == 'AUTO' else 'transparent'};
                            color: {'white' if current_info['current_market'] == 'AUTO' else '#28a745'};
                            font-size: 11px;
                            cursor: pointer;
                        ">
                    自動
                </button>
            </div>
        </div>
        
        <script>
        function switchMarket(marketType) {{
            // 發送市場切換請求到後端
            fetch('/api/market/switch', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{market: marketType}})
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    // 重新載入頁面或更新相關組件
                    location.reload();
                }} else {{
                    console.error('市場切換失敗:', data.error);
                }}
            }})
            .catch(error => {{
                console.error('切換市場時發生錯誤:', error);
            }});
        }}
        </script>
        """

# 全局市場切換器實例
market_switcher = MarketSwitcher()

def get_market_switcher() -> MarketSwitcher:
    """獲取全局市場切換器"""
    return market_switcher

# 示例使用
if __name__ == "__main__":
    switcher = MarketSwitcher()
    
    # 測試自動偵測
    test_symbols = ["AAPL", "2330", "2330.TW", "3481.TWO", "GOOGL"]
    
    for symbol in test_symbols:
        market = switcher.auto_detect_market(symbol)
        normalized = switcher.normalize_symbol_for_market(symbol, market)
        tv_symbol = switcher.get_tradingview_symbol(symbol)
        
        print(f"{symbol} -> 市場: {market.value}, 標準化: {normalized}, TradingView: {tv_symbol}")
    
    # 測試市場資訊
    print(f"\n當前市場資訊: {switcher.get_current_market_info()}")
    
    # 測試最佳市場
    optimal = switcher.get_optimal_market()
    print(f"最佳市場: {optimal.value}")