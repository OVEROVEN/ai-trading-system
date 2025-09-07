#!/usr/bin/env python3
"""
增強版台股TradingView Widget實現
結合TWSE開放資料，提供專業級台股圖表顯示
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EnhancedTaiwanWidget:
    """增強版台股TradingView Widget"""
    
    def __init__(self):
        # 台股主要公司清單 (包含名稱和行業)
        self.taiwan_stocks = {
            # 科技股
            "2330": {"name": "台積電", "industry": "半導體", "exchange": "TWSE", "market_cap": "large"},
            "2454": {"name": "聯發科", "industry": "半導體", "exchange": "TWSE", "market_cap": "large"},
            "2317": {"name": "鴻海", "industry": "電子製造", "exchange": "TWSE", "market_cap": "large"},
            "3711": {"name": "日月光投控", "industry": "半導體", "exchange": "TWSE", "market_cap": "large"},
            "2379": {"name": "瑞昱", "industry": "半導體", "exchange": "TWSE", "market_cap": "medium"},
            "3034": {"name": "聯詠", "industry": "半導體", "exchange": "TWSE", "market_cap": "medium"},
            
            # 金融股
            "2882": {"name": "國泰金", "industry": "金融", "exchange": "TWSE", "market_cap": "large"},
            "2881": {"name": "富邦金", "industry": "金融", "exchange": "TWSE", "market_cap": "large"},
            "2892": {"name": "第一金", "industry": "金融", "exchange": "TWSE", "market_cap": "large"},
            "2891": {"name": "中信金", "industry": "金融", "exchange": "TWSE", "market_cap": "large"},
            
            # 傳統產業
            "2412": {"name": "中華電", "industry": "電信", "exchange": "TWSE", "market_cap": "large"},
            "2603": {"name": "長榮", "industry": "航運", "exchange": "TWSE", "market_cap": "large"},
            "2609": {"name": "陽明", "industry": "航運", "exchange": "TWSE", "market_cap": "medium"},
            "1303": {"name": "南亞", "industry": "塑化", "exchange": "TWSE", "market_cap": "large"},
            "1301": {"name": "台塑", "industry": "塑化", "exchange": "TWSE", "market_cap": "large"},
            
            # ETF
            "0050": {"name": "元大台灣50", "industry": "ETF", "exchange": "TWSE", "market_cap": "large"},
            "0056": {"name": "元大高股息", "industry": "ETF", "exchange": "TWSE", "market_cap": "large"},
            "00878": {"name": "國泰永續高股息", "industry": "ETF", "exchange": "TWSE", "market_cap": "medium"},
            
            # 上櫃股票
            "3481": {"name": "群創", "industry": "面板", "exchange": "TPEx", "market_cap": "medium"},
            "6415": {"name": "矽力-KY", "industry": "半導體", "exchange": "TPEx", "market_cap": "medium"},
            "5483": {"name": "中美晶", "industry": "半導體", "exchange": "TPEx", "market_cap": "small"},
        }
        
        # 產業顏色配置
        self.industry_colors = {
            "半導體": "#4CAF50",
            "電子製造": "#2196F3", 
            "金融": "#FF9800",
            "電信": "#9C27B0",
            "航運": "#00BCD4",
            "塑化": "#795548",
            "面板": "#607D8B",
            "ETF": "#E91E63"
        }
    
    def normalize_taiwan_symbol(self, symbol: str) -> Tuple[str, str, str]:
        """
        標準化台股符號並返回 (純代號, 交易所, 完整符號)
        
        Args:
            symbol: 輸入的股票代號
            
        Returns:
            (code, exchange, full_symbol) 例如: ("2330", "TWSE", "2330.TW")
        """
        symbol = symbol.upper().strip()
        
        # 移除各種可能的後綴
        if symbol.endswith('.TW'):
            code = symbol[:-3]
            exchange = "TWSE"
        elif symbol.endswith('.TWO'):
            code = symbol[:-4]
            exchange = "TPEx"
        else:
            code = symbol
            # 根據股票清單判斷交易所
            if code in self.taiwan_stocks:
                exchange = self.taiwan_stocks[code]["exchange"]
            else:
                # 預設為上市
                exchange = "TWSE"
        
        # 生成完整符號
        suffix = ".TW" if exchange == "TWSE" else ".TWO"
        full_symbol = f"{code}{suffix}"
        
        return code, exchange, full_symbol
    
    def get_tradingview_symbol(self, symbol: str) -> str:
        """
        獲取適合TradingView Widget的符號格式
        
        Args:
            symbol: 台股代號
            
        Returns:
            TradingView格式的符號 (例如: "TWSE:2330")
        """
        code, exchange, full_symbol = self.normalize_taiwan_symbol(symbol)
        
        # TradingView台股符號格式 (根據官方文檔)
        if exchange == "TWSE":
            return f"TWSE:{code}"  # Taiwan Stock Exchange
        else:
            return f"GTSM:{code}"  # GreTai Securities Market (上櫃)
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        獲取台股詳細資訊
        
        Args:
            symbol: 台股代號
            
        Returns:
            股票詳細資訊字典
        """
        code, exchange, full_symbol = self.normalize_taiwan_symbol(symbol)
        
        if code in self.taiwan_stocks:
            stock_info = self.taiwan_stocks[code].copy()
            stock_info.update({
                "code": code,
                "full_symbol": full_symbol,
                "tradingview_symbol": self.get_tradingview_symbol(symbol),
                "currency": "TWD",
                "timezone": "Asia/Taipei",
                "trading_hours": "09:00-13:30",
                "industry_color": self.industry_colors.get(stock_info["industry"], "#666666")
            })
            return stock_info
        else:
            # 未知股票的預設資訊
            return {
                "code": code,
                "name": f"台股 {code}",
                "industry": "未分類",
                "exchange": exchange,
                "market_cap": "unknown",
                "full_symbol": full_symbol,
                "tradingview_symbol": self.get_tradingview_symbol(symbol),
                "currency": "TWD",
                "timezone": "Asia/Taipei",
                "trading_hours": "09:00-13:30",
                "industry_color": "#666666"
            }
    
    def create_enhanced_widget(
        self,
        symbol: str,
        theme: str = "dark",
        additional_studies: List[str] = None,
        custom_config: Dict[str, Any] = None
    ) -> str:
        """
        創建增強版台股TradingView Widget
        
        Args:
            symbol: 台股代號
            theme: 主題 (dark/light)
            additional_studies: 額外的技術指標
            custom_config: 自定義配置
            
        Returns:
            完整的HTML字符串
        """
        stock_info = self.get_stock_info(symbol)
        tradingview_symbol = stock_info["tradingview_symbol"]
        
        # 主題配置
        colors = self._get_theme_colors(theme)
        
        # 基礎技術指標
        base_studies = [
            "Volume@tv-basicstudies",
            "RSI@tv-basicstudies",
            "MACD@tv-basicstudies"
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
            "symbol": tradingview_symbol,
            "interval": "D",
            "timezone": "Asia/Taipei",
            "theme": theme,
            "style": "1",
            "locale": "zh_TW",
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
            "save_image": True
        }
        
        # 合併自定義配置
        if custom_config:
            base_config.update(custom_config)
        
        return self._generate_widget_html(stock_info, base_config, colors, theme)
    
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
        theme: str
    ) -> str:
        """生成完整的Widget HTML"""
        
        return f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock_info['name']} ({stock_info['code']}) - 台股TradingView圖表</title>
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
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            font-size: 13px;
        }}
        
        .detail-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid {colors['border_color']};
        }}
        
        .symbol-tester {{
            display: flex;
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
            font-size: 12px;
            transition: all 0.2s ease;
        }}
        
        .test-btn:hover {{
            background: {colors['accent']};
            color: white;
            border-color: {colors['accent']};
        }}
        
        .test-input {{
            flex: 1;
            padding: 8px 12px;
            border: 1px solid {colors['border_color']};
            border-radius: 6px;
            background: {colors['input_bg']};
            color: {colors['text_color']};
            font-size: 14px;
        }}
        
        .test-submit {{
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
                    <span>🇹🇼 {stock_info['exchange']}</span>
                    <span>•</span>
                    <span>{stock_info['trading_hours']}</span>
                    <span>•</span>
                    <span>Asia/Taipei</span>
                </div>
            </div>
            <div class="trading-widget">
                <div id="tradingview_widget" style="width: 100%; height: 100%;"></div>
            </div>
        </div>
        
        <div class="info-panel">
            <!-- 股票詳細資訊 -->
            <div class="info-card">
                <div class="card-title">
                    <i class="fas fa-info-circle"></i>
                    股票資訊
                </div>
                <div class="stock-detail">
                    <div class="detail-item">
                        <span>代號:</span>
                        <span>{stock_info['code']}</span>
                    </div>
                    <div class="detail-item">
                        <span>名稱:</span>
                        <span>{stock_info['name']}</span>
                    </div>
                    <div class="detail-item">
                        <span>交易所:</span>
                        <span>{stock_info['exchange']}</span>
                    </div>
                    <div class="detail-item">
                        <span>產業:</span>
                        <span>{stock_info['industry']}</span>
                    </div>
                    <div class="detail-item">
                        <span>市值:</span>
                        <span>{stock_info['market_cap']}</span>
                    </div>
                    <div class="detail-item">
                        <span>幣別:</span>
                        <span>{stock_info['currency']}</span>
                    </div>
                </div>
            </div>
            
            <!-- 符號測試器 -->
            <div class="info-card">
                <div class="card-title">
                    <i class="fas fa-search"></i>
                    股票查詢
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; gap: 8px; margin-bottom: 8px;">
                        <input type="text" id="symbolInput" placeholder="輸入股票代號..." class="test-input">
                        <button onclick="testSymbol()" class="test-submit">查詢</button>
                    </div>
                </div>
                <div class="symbol-tester">
                    <button class="test-btn" onclick="loadSymbol('2330')">台積電</button>
                    <button class="test-btn" onclick="loadSymbol('2454')">聯發科</button>
                    <button class="test-btn" onclick="loadSymbol('2881')">富邦金</button>
                </div>
                <div class="symbol-tester">
                    <button class="test-btn" onclick="loadSymbol('0050')">台灣50</button>
                    <button class="test-btn" onclick="loadSymbol('2603')">長榮</button>
                    <button class="test-btn" onclick="loadSymbol('2412')">中華電</button>
                </div>
            </div>
            
            <!-- 功能特色 -->
            <div class="info-card">
                <div class="card-title">
                    <i class="fas fa-star"></i>
                    圖表功能
                </div>
                <ul class="feature-list">
                    <li>即時K線圖表</li>
                    <li>成交量分析</li>
                    <li>RSI技術指標</li>
                    <li>MACD動量指標</li>
                    <li>多時間週期切換</li>
                    <li>圖表工具繪製</li>
                    <li>專業技術分析</li>
                    <li>台股交易時間</li>
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
            "MACD.histogram.color": "#26A69A"
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
            "header_saveload",
            "study_dialog_search_control"
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
                console.log('台股TradingView Widget 初始化成功:', '{stock_info["tradingview_symbol"]}');
            }} catch (error) {{
                console.error('TradingView Widget 初始化失敗:', error);
                document.getElementById('tradingview_widget').innerHTML = 
                    '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #dc3545;">' +
                    '<div style="text-align: center;">' +
                    '<h3>⚠️ 圖表載入失敗</h3>' +
                    '<p>請檢查網路連接或稍後重試</p>' +
                    '</div></div>';
            }}
        }}
        
        // 符號查詢功能
        function testSymbol() {{
            const symbol = document.getElementById('symbolInput').value.trim();
            if (symbol) {{
                loadSymbol(symbol);
            }} else {{
                alert('請輸入股票代號');
            }}
        }}
        
        function loadSymbol(symbol) {{
            const newUrl = `/chart/taiwan-widget/${{symbol}}`;
            window.location.href = newUrl;
        }}
        
        // 頁面載入後初始化
        document.addEventListener('DOMContentLoaded', function() {{
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
                        console.error('TradingView 載入超時');
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

# 全局實例
enhanced_taiwan_widget = EnhancedTaiwanWidget()

def get_enhanced_taiwan_widget() -> EnhancedTaiwanWidget:
    """獲取增強版台股Widget實例"""
    return enhanced_taiwan_widget

def create_taiwan_chart(symbol: str, theme: str = "dark") -> str:
    """
    快速創建台股圖表的便利函數
    
    Args:
        symbol: 台股代號
        theme: 主題 (dark/light)
        
    Returns:
        完整的HTML字符串
    """
    widget = get_enhanced_taiwan_widget()
    return widget.create_enhanced_widget(symbol, theme)