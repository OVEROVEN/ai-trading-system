#!/usr/bin/env python3
"""
增強版美股TradingView Widget實現
專門為美股優化的TradingView Widget，包含詳細的股票資訊和功能
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)

class EnhancedUSWidget:
    """增強版美股TradingView Widget"""
    
    def __init__(self):
        # 美股主要公司清單 (包含名稱和行業)
        self.us_stocks = {
            # 科技股 (FAANG+)
            "AAPL": {"name": "Apple Inc.", "industry": "Technology", "sector": "Consumer Electronics", "market_cap": "3.5T", "exchange": "NASDAQ"},
            "GOOGL": {"name": "Alphabet Inc.", "industry": "Technology", "sector": "Internet Services", "market_cap": "2.1T", "exchange": "NASDAQ"},
            "MSFT": {"name": "Microsoft Corp.", "industry": "Technology", "sector": "Software", "market_cap": "3.1T", "exchange": "NASDAQ"},
            "AMZN": {"name": "Amazon.com Inc.", "industry": "Technology", "sector": "E-commerce", "market_cap": "1.7T", "exchange": "NASDAQ"},
            "META": {"name": "Meta Platforms Inc.", "industry": "Technology", "sector": "Social Media", "market_cap": "1.3T", "exchange": "NASDAQ"},
            "NFLX": {"name": "Netflix Inc.", "industry": "Technology", "sector": "Streaming", "market_cap": "200B", "exchange": "NASDAQ"},
            
            # 芯片股
            "NVDA": {"name": "NVIDIA Corp.", "industry": "Technology", "sector": "Semiconductors", "market_cap": "1.8T", "exchange": "NASDAQ"},
            "AMD": {"name": "Advanced Micro Devices", "industry": "Technology", "sector": "Semiconductors", "market_cap": "220B", "exchange": "NASDAQ"},
            "INTC": {"name": "Intel Corp.", "industry": "Technology", "sector": "Semiconductors", "market_cap": "200B", "exchange": "NASDAQ"},
            
            # 電動車
            "TSLA": {"name": "Tesla Inc.", "industry": "Automotive", "sector": "Electric Vehicles", "market_cap": "800B", "exchange": "NASDAQ"},
            
            # 金融股
            "JPM": {"name": "JPMorgan Chase & Co.", "industry": "Financial", "sector": "Banking", "market_cap": "550B", "exchange": "NYSE"},
            "BAC": {"name": "Bank of America Corp.", "industry": "Financial", "sector": "Banking", "market_cap": "320B", "exchange": "NYSE"},
            "WFC": {"name": "Wells Fargo & Co.", "industry": "Financial", "sector": "Banking", "market_cap": "200B", "exchange": "NYSE"},
            
            # 醫療保健
            "JNJ": {"name": "Johnson & Johnson", "industry": "Healthcare", "sector": "Pharmaceuticals", "market_cap": "450B", "exchange": "NYSE"},
            "PFE": {"name": "Pfizer Inc.", "industry": "Healthcare", "sector": "Pharmaceuticals", "market_cap": "180B", "exchange": "NYSE"},
            
            # 工業股
            "BA": {"name": "Boeing Co.", "industry": "Industrial", "sector": "Aerospace", "market_cap": "130B", "exchange": "NYSE"},
            "CAT": {"name": "Caterpillar Inc.", "industry": "Industrial", "sector": "Machinery", "market_cap": "170B", "exchange": "NYSE"},
            
            # ETF
            "SPY": {"name": "SPDR S&P 500 ETF", "industry": "ETF", "sector": "Market Index", "market_cap": "500B", "exchange": "NYSE"},
            "QQQ": {"name": "Invesco QQQ Trust", "industry": "ETF", "sector": "Technology Index", "market_cap": "250B", "exchange": "NASDAQ"},
            "IWM": {"name": "iShares Russell 2000 ETF", "industry": "ETF", "sector": "Small Cap Index", "market_cap": "60B", "exchange": "NYSE"},
            
            # 加密貨幣相關
            "COIN": {"name": "Coinbase Global Inc.", "industry": "Technology", "sector": "Cryptocurrency", "market_cap": "60B", "exchange": "NASDAQ"},
            
            # 中概股
            "BABA": {"name": "Alibaba Group", "industry": "Technology", "sector": "E-commerce", "market_cap": "200B", "exchange": "NYSE"},
            "JD": {"name": "JD.com Inc.", "industry": "Technology", "sector": "E-commerce", "market_cap": "60B", "exchange": "NASDAQ"},
        }
        
        # 行業顏色配置
        self.industry_colors = {
            "Technology": "#2196F3",
            "Automotive": "#4CAF50",
            "Financial": "#FF9800", 
            "Healthcare": "#9C27B0",
            "Industrial": "#795548",
            "ETF": "#E91E63"
        }
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        獲取美股詳細資訊
        
        Args:
            symbol: 美股代號
            
        Returns:
            股票詳細資訊字典
        """
        symbol = symbol.upper().strip()
        
        if symbol in self.us_stocks:
            stock_info = self.us_stocks[symbol].copy()
            stock_info.update({
                "code": symbol,
                "full_symbol": symbol,
                "tradingview_symbol": symbol,
                "currency": "USD",
                "timezone": "America/New_York",
                "trading_hours": "09:30-16:00 ET",
                "industry_color": self.industry_colors.get(stock_info["industry"], "#666666")
            })
            return stock_info
        else:
            # 未知股票的預設資訊
            return {
                "code": symbol,
                "name": f"Unknown Stock {symbol}",
                "industry": "Unknown",
                "sector": "Unknown",
                "market_cap": "N/A",
                "exchange": "Unknown",
                "full_symbol": symbol,
                "tradingview_symbol": symbol,
                "currency": "USD",
                "timezone": "America/New_York", 
                "trading_hours": "09:30-16:00 ET",
                "industry_color": "#666666"
            }
    
    def create_enhanced_widget(
        self,
        symbol: str,
        theme: str = "dark",
        additional_studies: List[str] = None,
        custom_config: Dict[str, Any] = None,
        include_crypto: bool = False
    ) -> str:
        """
        創建增強版美股TradingView Widget
        
        Args:
            symbol: 美股代號
            theme: 主題 (dark/light)
            additional_studies: 額外的技術指標
            custom_config: 自定義配置
            include_crypto: 是否包含加密貨幣相關功能
            
        Returns:
            完整的HTML字符串
        """
        stock_info = self.get_stock_info(symbol)
        
        # 主題配置
        colors = self._get_theme_colors(theme)
        
        # 基礎技術指標
        base_studies = [
            "Volume@tv-basicstudies",
            "RSI@tv-basicstudies", 
            "MACD@tv-basicstudies",
            "MA@tv-basicstudies"  # 移動平均線
        ]
        
        # 合併額外的技術指標
        if additional_studies:
            studies = base_studies + additional_studies
        else:
            studies = base_studies
        
        # 基礎配置
        base_config = {
            "width": "100%",
            "height": "100%",
            "symbol": symbol,
            "interval": "D",
            "timezone": "America/New_York",
            "theme": theme,
            "style": "1",
            "locale": "en",
            "toolbar_bg": colors["background"],
            "enable_publishing": False,
            "allow_symbol_change": True,
            "container_id": "tradingview_widget",
            "autosize": True,
            "fullscreen": False,
            "studies": studies,
            "hide_side_toolbar": False,
            "withdateranges": True,
            "hide_legend": False,
            "save_image": True,
            "show_popup_button": True,
            "popup_width": "1000",
            "popup_height": "650"
        }
        
        # 合併自定義配置
        if custom_config:
            base_config.update(custom_config)
        
        return self._generate_widget_html(stock_info, base_config, colors, theme, include_crypto)
    
    def _get_theme_colors(self, theme: str) -> Dict[str, str]:
        """獲取主題顏色配置"""
        if theme == "dark":
            return {
                "background": "#1e222d",
                "panel_bg": "#2a2e39",
                "card_bg": "#131722",
                "text_color": "#d1d4dc",
                "input_bg": "#343a40",
                "border_color": "#495057",
                "accent": "#2962ff"
            }
        else:
            return {
                "background": "#ffffff",
                "panel_bg": "#f8f9fa",
                "card_bg": "#ffffff",
                "text_color": "#2e2e2e", 
                "input_bg": "#ffffff",
                "border_color": "#ced4da",
                "accent": "#1976d2"
            }
    
    def _generate_widget_html(
        self,
        stock_info: Dict[str, Any],
        config: Dict[str, Any],
        colors: Dict[str, str],
        theme: str,
        include_crypto: bool = False
    ) -> str:
        """生成完整的Widget HTML"""
        
        # 相關股票推薦
        related_stocks = self._get_related_stocks(stock_info["industry"], stock_info["code"])
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_info['name']} ({stock_info['code']}) - US Stock TradingView Chart</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: {colors['background']};
            color: {colors['text_color']};
            height: 100vh;
            overflow: hidden;
        }}
        
        .main-container {{
            display: flex;
            height: 100vh;
            gap: 15px;
            padding: 15px;
        }}
        
        .chart-container {{
            flex: 3;
            background: {colors['panel_bg']};
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            position: relative;
        }}
        
        .chart-header {{
            background: {colors['card_bg']};
            padding: 15px 20px;
            border-bottom: 1px solid {colors['border_color']};
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .stock-title {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .stock-code {{
            font-size: 20px;
            font-weight: 700;
            color: {colors['accent']};
        }}
        
        .stock-name {{
            font-size: 16px;
            color: {colors['text_color']};
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .industry-badge {{
            background: {stock_info['industry_color']};
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        }}
        
        .exchange-info {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: #6c757d;
        }}
        
        .trading-widget {{
            width: 100%;
            height: calc(100% - 70px);
        }}
        
        .info-panel {{
            width: 350px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            overflow-y: auto;
        }}
        
        .info-card {{
            background: {colors['panel_bg']};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .card-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .stock-detail {{
            font-size: 13px;
            line-height: 1.6;
        }}
        
        .detail-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid {colors['border_color']};
        }}
        
        .symbol-tester {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-bottom: 15px;
        }}
        
        .test-btn {{
            padding: 8px 12px;
            border: 1px solid {colors['border_color']};
            border-radius: 6px;
            background: {colors['panel_bg']};
            color: {colors['text_color']};
            cursor: pointer;
            font-size: 11px;
            transition: all 0.2s ease;
            text-align: center;
        }}
        
        .test-btn:hover {{
            background: {colors['accent']};
            color: white;
            border-color: {colors['accent']};
        }}
        
        .test-input {{
            width: 100%;
            padding: 8px 12px;
            border: 1px solid {colors['border_color']};
            border-radius: 6px;
            background: {colors['input_bg']};
            color: {colors['text_color']};
            font-size: 14px;
            margin-bottom: 8px;
        }}
        
        .test-submit {{
            width: 100%;
            padding: 8px 16px;
            background: {colors['accent']};
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .feature-list {{
            list-style: none;
            font-size: 13px;
            line-height: 1.6;
        }}
        
        .feature-list li {{
            padding: 4px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .feature-list li::before {{
            content: "✓";
            color: #4CAF50;
            font-weight: bold;
        }}
        
        .related-stocks {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }}
        
        .related-stock {{
            padding: 8px;
            background: {colors['card_bg']};
            border: 1px solid {colors['border_color']};
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
            font-size: 11px;
        }}
        
        .related-stock:hover {{
            background: {colors['accent']};
            color: white;
            border-color: {colors['accent']};
        }}
        
        .market-status {{
            padding: 10px;
            background: {colors['card_bg']};
            border-radius: 6px;
            text-align: center;
            font-size: 12px;
            margin-bottom: 15px;
        }}
        
        .status-open {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        
        .status-closed {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        @media (max-width: 1200px) {{
            .main-container {{
                flex-direction: column;
                gap: 10px;
                padding: 10px;
            }}
            
            .info-panel {{
                width: 100%;
                max-height: 200px;
                flex-direction: row;
                overflow-x: auto;
            }}
            
            .info-card {{
                min-width: 280px;
            }}
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="chart-container">
            <div class="chart-header">
                <div class="stock-title">
                    <div>
                        <div class="stock-code">{stock_info['code']}</div>
                        <div class="stock-name">{stock_info['name']}</div>
                    </div>
                    <div class="industry-badge">{stock_info['industry']}</div>
                </div>
                <div class="exchange-info">
                    <span>🇺🇸 {stock_info['exchange']}</span>
                    <span>•</span>
                    <span>{stock_info['trading_hours']}</span>
                    <span>•</span>
                    <span>Market Cap: {stock_info['market_cap']}</span>
                </div>
            </div>
            <div class="trading-widget">
                <div id="tradingview_widget" style="width: 100%; height: 100%;"></div>
            </div>
        </div>
        
        <div class="info-panel">
            <!-- 市場狀態 -->
            <div class="market-status" id="marketStatus">
                <i class="fas fa-clock"></i>
                US Market Status: Checking...
            </div>
            
            <!-- 股票詳細資訊 -->
            <div class="info-card">
                <div class="card-title">
                    <i class="fas fa-info-circle"></i>
                    Stock Information
                </div>
                <div class="stock-detail">
                    <div class="detail-item">
                        <span>Symbol:</span>
                        <span>{stock_info['code']}</span>
                    </div>
                    <div class="detail-item">
                        <span>Company:</span>
                        <span>{stock_info['name']}</span>
                    </div>
                    <div class="detail-item">
                        <span>Exchange:</span>
                        <span>{stock_info['exchange']}</span>
                    </div>
                    <div class="detail-item">
                        <span>Sector:</span>
                        <span>{stock_info['sector']}</span>
                    </div>
                    <div class="detail-item">
                        <span>Industry:</span>
                        <span>{stock_info['industry']}</span>
                    </div>
                    <div class="detail-item">
                        <span>Market Cap:</span>
                        <span>{stock_info['market_cap']}</span>
                    </div>
                    <div class="detail-item">
                        <span>Currency:</span>
                        <span>{stock_info['currency']}</span>
                    </div>
                </div>
            </div>
            
            <!-- 股票查詢 -->
            <div class="info-card">
                <div class="card-title">
                    <i class="fas fa-search"></i>
                    Stock Search
                </div>
                <input type="text" id="symbolInput" placeholder="Enter stock symbol (e.g., AAPL)..." class="test-input">
                <button onclick="testSymbol()" class="test-submit">Search</button>
                
                <div class="symbol-tester">
                    <button class="test-btn" onclick="loadSymbol('AAPL')">AAPL</button>
                    <button class="test-btn" onclick="loadSymbol('GOOGL')">GOOGL</button>
                    <button class="test-btn" onclick="loadSymbol('MSFT')">MSFT</button>
                    <button class="test-btn" onclick="loadSymbol('TSLA')">TSLA</button>
                    <button class="test-btn" onclick="loadSymbol('NVDA')">NVDA</button>
                    <button class="test-btn" onclick="loadSymbol('META')">META</button>
                </div>
            </div>
            
            <!-- 相關股票 -->
            <div class="info-card">
                <div class="card-title">
                    <i class="fas fa-chart-line"></i>
                    Related Stocks
                </div>
                <div class="related-stocks">
                    {self._generate_related_stocks_html(related_stocks)}
                </div>
            </div>
            
            <!-- 功能特色 -->
            <div class="info-card">
                <div class="card-title">
                    <i class="fas fa-star"></i>
                    Chart Features
                </div>
                <ul class="feature-list">
                    <li>Real-time price data</li>
                    <li>Candlestick charts</li>
                    <li>Volume analysis</li>
                    <li>RSI indicator</li>
                    <li>MACD momentum</li>
                    <li>Moving averages</li>
                    <li>Multiple timeframes</li>
                    <li>Drawing tools</li>
                    <li>Technical analysis</li>
                    <li>Market hours display</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- TradingView Widget Script -->
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
        // TradingView Widget 配置
        const widgetConfig = {json.dumps(config, ensure_ascii=True)};
        
        // 技術指標覆蓋設定
        widgetConfig.studies_overrides = {{
            "volume.volume.color.0": "#f23645",
            "volume.volume.color.1": "#26a69a",
            "volume.volume.transparency": 75,
            "RSI.RSI.color": "#2196F3",
            "RSI.upper band.color": "#787B86",
            "RSI.lower band.color": "#787B86",
            "RSI.RSI.linewidth": 2,
            "MACD.macd.color": "#2962FF",
            "MACD.signal.color": "#FF6D00",
            "MACD.histogram.color": "#26A69A",
            "MA.MA.color": "#FFB74D"
        }};
        
        // 圖表樣式覆蓋
        widgetConfig.overrides = {{
            "paneProperties.background": "{colors['background']}",
            "paneProperties.backgroundType": "solid",
            "paneProperties.vertGridProperties.color": "#363c4e",
            "paneProperties.horzGridProperties.color": "#363c4e",
            "symbolWatermarkProperties.transparency": 90,
            "scalesProperties.textColor": "{colors['text_color']}",
            "scalesProperties.fontSize": 12,
            "mainSeriesProperties.candleStyle.wickUpColor": "#26a69a",
            "mainSeriesProperties.candleStyle.wickDownColor": "#f23645",
            "mainSeriesProperties.candleStyle.upColor": "#26a69a",
            "mainSeriesProperties.candleStyle.downColor": "#f23645",
            "mainSeriesProperties.candleStyle.borderUpColor": "#26a69a",
            "mainSeriesProperties.candleStyle.borderDownColor": "#f23645",
            "mainSeriesProperties.candleStyle.wickVisible": true,
            "volumePaneSize": "medium"
        }};
        
        // 禁用功能
        widgetConfig.disabled_features = [
            "header_saveload"
        ];
        
        // 啟用功能
        widgetConfig.enabled_features = [
            "move_logo_to_main_pane",
            "study_templates",
            "side_toolbar_in_fullscreen_mode"
        ];
        
        // 初始化Widget
        function initTradingViewWidget() {{
            try {{
                new TradingView.widget(widgetConfig);
                console.log('US Stock TradingView Widget initialized:', '{stock_info["code"]}');
            }} catch (error) {{
                console.error('TradingView Widget initialization failed:', error);
                document.getElementById('tradingview_widget').innerHTML = 
                    '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #dc3545;">' +
                    '<div style="text-align: center;">' +
                    '<h3>⚠️ Chart Loading Failed</h3>' +
                    '<p>Please check network connection or try again later</p>' +
                    '</div></div>';
            }}
        }}
        
        // 股票查詢功能
        function testSymbol() {{
            const symbol = document.getElementById('symbolInput').value.trim().toUpperCase();
            if (symbol) {{
                loadSymbol(symbol);
            }} else {{
                alert('Please enter a stock symbol');
            }}
        }}
        
        function loadSymbol(symbol) {{
            const newUrl = `/chart/us-widget/${{symbol}}`;
            window.location.href = newUrl;
        }}
        
        // 市場狀態檢查
        function updateMarketStatus() {{
            const now = new Date();
            const nyTime = new Date(now.toLocaleString("en-US", {{timeZone: "America/New_York"}}));
            const hour = nyTime.getHours();
            const day = nyTime.getDay();
            
            const marketStatus = document.getElementById('marketStatus');
            
            // 週末
            if (day === 0 || day === 6) {{
                marketStatus.className = 'market-status status-closed';
                marketStatus.innerHTML = '<i class="fas fa-times-circle"></i> US Market: Closed (Weekend)';
            }}
            // 交易時間 09:30-16:00 ET
            else if (hour >= 9.5 && hour < 16) {{
                marketStatus.className = 'market-status status-open';
                marketStatus.innerHTML = '<i class="fas fa-check-circle"></i> US Market: Open (Live Data)';
            }}
            // 盤前 04:00-09:30 ET
            else if (hour >= 4 && hour < 9.5) {{
                marketStatus.className = 'market-status status-closed';
                marketStatus.innerHTML = '<i class="fas fa-clock"></i> US Market: Pre-Market';
            }}
            // 盤後 16:00-20:00 ET
            else if (hour >= 16 && hour < 20) {{
                marketStatus.className = 'market-status status-closed';
                marketStatus.innerHTML = '<i class="fas fa-clock"></i> US Market: After Hours';
            }}
            // 其他時間
            else {{
                marketStatus.className = 'market-status status-closed';
                marketStatus.innerHTML = '<i class="fas fa-times-circle"></i> US Market: Closed';
            }}
        }}
        
        // 頁面載入後初始化
        document.addEventListener('DOMContentLoaded', function() {{
            // 初始化市場狀態
            updateMarketStatus();
            setInterval(updateMarketStatus, 60000); // 每分鐘更新
            
            // 檢查TradingView是否可用
            if (typeof TradingView !== 'undefined') {{
                initTradingViewWidget();
            }} else {{
                // 等待TradingView載入
                let attempts = 0;
                const checkTradingView = setInterval(() => {{
                    attempts++;
                    if (typeof TradingView !== 'undefined') {{
                        clearInterval(checkTradingView);
                        initTradingViewWidget();
                    }} else if (attempts > 20) {{
                        clearInterval(checkTradingView);
                        console.error('TradingView loading timeout');
                    }}
                }}, 500);
            }}
            
            // 支援Enter鍵查詢
            document.getElementById('symbolInput').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    testSymbol();
                }}
            }});
        }});
    </script>
</body>
</html>
        """
    
    def _get_related_stocks(self, industry: str, current_symbol: str) -> List[str]:
        """獲取相關股票列表"""
        related = []
        for symbol, info in self.us_stocks.items():
            if (info["industry"] == industry and 
                symbol != current_symbol and 
                len(related) < 6):
                related.append(symbol)
        return related
    
    def _generate_related_stocks_html(self, related_stocks: List[str]) -> str:
        """生成相關股票的HTML"""
        html_parts = []
        for symbol in related_stocks:
            stock_info = self.us_stocks.get(symbol, {})
            name = stock_info.get("name", symbol)
            # 縮短公司名稱
            short_name = name.split()[0] if " " in name else name
            html_parts.append(
                f'<div class="related-stock" onclick="loadSymbol(\'{symbol}\')">'
                f'<div style="font-weight: bold;">{symbol}</div>'
                f'<div style="font-size: 10px; opacity: 0.8;">{short_name}</div>'
                f'</div>'
            )
        return ''.join(html_parts)

# 全局實例
enhanced_us_widget = EnhancedUSWidget()

def get_enhanced_us_widget() -> EnhancedUSWidget:
    """獲取增強版美股Widget實例"""
    return enhanced_us_widget

def create_us_chart(symbol: str, theme: str = "dark") -> str:
    """
    快速創建美股圖表的便利函數
    
    Args:
        symbol: 美股代號
        theme: 主題 (dark/light)
        
    Returns:
        完整的HTML字符串
    """
    widget = get_enhanced_us_widget()
    return widget.create_enhanced_widget(symbol, theme)