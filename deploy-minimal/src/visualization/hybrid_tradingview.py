#!/usr/bin/env python3
"""
混合模式 TradingView 實現
美股使用 Widget，台股使用 Charting Library + TWSE/TPEx 開放資料
"""

from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class HybridTradingViewChart:
    """混合模式 TradingView 圖表"""
    
    def __init__(self):
        self.charting_library_version = "20.043"  # 或使用最新版本
    
    def is_taiwan_stock(self, symbol: str) -> bool:
        """判斷是否為台股"""
        symbol = symbol.upper().strip()
        return (symbol.endswith('.TW') or 
                symbol.endswith('.TWO') or 
                (symbol.isdigit() and len(symbol) == 4))
    
    def get_tradingview_symbol(self, symbol: str) -> str:
        """獲取 TradingView Widget 格式的符號"""
        symbol = symbol.upper().strip()
        
        if symbol.endswith('.TW'):
            code = symbol[:-3]
            return f"TPE:{code}"
        elif symbol.endswith('.TWO'):
            code = symbol[:-4]
            return f"TPX:{code}"
        else:
            return symbol
    
    def normalize_symbol(self, symbol: str) -> str:
        """標準化符號格式"""
        symbol = symbol.upper().strip()
        
        # 如果是純數字且長度為4，判斷為台股
        if symbol.isdigit() and len(symbol) == 4:
            return f"{symbol}.TW"
        
        return symbol
    
    def create_hybrid_chart(
        self,
        symbol: str,
        theme: str = "dark",
        stock_data: Dict = None,
        ai_recommendations: Dict = None,
        strategy_info: Dict = None
    ) -> str:
        """創建混合模式圖表"""
        
        normalized_symbol = self.normalize_symbol(symbol)
        is_taiwan = self.is_taiwan_stock(normalized_symbol)
        
        # 主題配置
        colors = self._get_theme_colors(theme)
        
        if is_taiwan:
            # 台股使用 Charting Library
            chart_html = self._create_charting_library_chart(normalized_symbol, colors)
            market_type = "台股 (Charting Library + TWSE/TPEx 開放資料)"
        else:
            # 美股使用 Widget
            chart_html = self._create_widget_chart(symbol, colors)
            market_type = "美股 (TradingView Widget)"
        
        # 創建完整的 HTML 頁面
        return self._create_complete_page(
            normalized_symbol, chart_html, market_type, colors,
            stock_data, ai_recommendations, strategy_info
        )
    
    def _get_theme_colors(self, theme: str) -> Dict[str, str]:
        """獲取主題顏色"""
        if theme == "dark":
            return {
                'background': '#1e222d',
                'panel_bg': '#2a2e39',
                'card_bg': '#131722',
                'text_color': '#d1d4dc',
                'input_bg': '#343a40',
                'border_color': '#495057'
            }
        else:
            return {
                'background': '#ffffff',
                'panel_bg': '#f8f9fa',
                'card_bg': '#ffffff',
                'text_color': '#2e2e2e',
                'input_bg': '#ffffff',
                'border_color': '#ced4da'
            }
    
    def _create_charting_library_chart(self, symbol: str, colors: Dict[str, str]) -> str:
        """創建 Charting Library 圖表 (台股)"""
        return f"""
        <div id="tv_chart_container" style="width: 100%; height: 100%;"></div>
        
        <!-- TradingView Charting Library -->
        <script type="text/javascript" src="/static/charting_library/charting_library.min.js"></script>
        <script type="text/javascript">
            function initChartingLibrary() {{
                const widget = window.tvWidget = new TradingView.widget({{
                    symbol: '{symbol}',
                    datafeed: new Datafeeds.UDFCompatibleDatafeed('/api/charting'),
                    interval: '1D',
                    container_id: 'tv_chart_container',
                    library_path: '/static/charting_library/',
                    
                    locale: 'zh_TW',
                    disabled_features: ['use_localstorage_for_settings'],
                    enabled_features: ['study_templates'],
                    charts_storage_url: '/api/charting/',
                    charts_storage_api_version: '1.1',
                    client_id: 'tradingview.com',
                    user_id: 'public_user_id',
                    
                    fullscreen: false,
                    autosize: true,
                    studies_overrides: {{}},
                    
                    theme: '{colors["background"].replace("#", "")}',
                    custom_css_url: '/static/charting_library/custom.css',
                    
                    timezone: 'Asia/Taipei',
                    
                    // 台股特定設置
                    debug: false,
                    
                    overrides: {{
                        "paneProperties.background": "{colors['background']}",
                        "paneProperties.vertGridProperties.color": "#363c4e",
                        "paneProperties.horzGridProperties.color": "#363c4e",
                        "symbolWatermarkProperties.transparency": 90,
                        "scalesProperties.textColor": "{colors['text_color']}",
                        "mainSeriesProperties.candleStyle.wickUpColor": "#089981",
                        "mainSeriesProperties.candleStyle.wickDownColor": "#f23645",
                        "mainSeriesProperties.candleStyle.upColor": "#089981",
                        "mainSeriesProperties.candleStyle.downColor": "#f23645"
                    }}
                }});
                
                widget.onChartReady(() => {{
                    console.log('台股 Charting Library 已載入完成');
                    
                    // 自動添加成交量指標
                    widget.chart().createStudy('Volume', false, false);
                    
                    // 監聽符號變更
                    widget.subscribe('onSymbolChanged', function(symbolInfo) {{
                        console.log('台股符號已變更:', symbolInfo);
                        window.onSymbolChanged && window.onSymbolChanged(symbolInfo.name);
                    }});
                }});
            }}
            
            // 檢查 Charting Library 是否載入
            if (typeof TradingView !== 'undefined' && TradingView.widget) {{
                initChartingLibrary();
            }} else {{
                // 如果 Charting Library 未載入，顯示錯誤
                document.getElementById('tv_chart_container').innerHTML = 
                    '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #dc3545;">' +
                    '<div><h3>⚠️ TradingView Charting Library 未安裝</h3>' +
                    '<p>台股圖表需要 Charting Library 支援</p>' +
                    '<p>請聯繫管理員安裝 Charting Library</p></div></div>';
            }}
        </script>
        """
    
    def _create_widget_chart(self, symbol: str, colors: Dict[str, str]) -> str:
        """創建 Widget 圖表 (美股)"""
        tv_symbol = self.get_tradingview_symbol(symbol)
        
        return f"""
        <div id="tradingview_widget" style="width: 100%; height: 100%;"></div>
        
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
            function initWidget() {{
                new TradingView.widget({{
                    "width": "100%",
                    "height": "100%",
                    "symbol": "{tv_symbol}",
                    "interval": "D",
                    "timezone": "America/New_York",
                    "theme": "{'dark' if colors['background'] == '#1e222d' else 'light'}",
                    "style": "1",
                    "locale": "zh_TW",
                    "toolbar_bg": "{colors['background']}",
                    "enable_publishing": false,
                    "allow_symbol_change": true,
                    "container_id": "tradingview_widget",
                    "autosize": true,
                    "fullscreen": false,
                    "studies": [
                        "RSI@tv-basicstudies",
                        "Volume@tv-basicstudies"
                    ],
                    "hide_side_toolbar": false,
                    "withdateranges": true,
                    "hide_legend": false,
                    "save_image": true,
                    "studies_overrides": {{
                        "volume.volume.color.0": "#f23645",
                        "volume.volume.color.1": "#089981",
                        "volume.volume.transparency": 80,
                        "RSI.RSI.color": "#2196F3"
                    }},
                    "overrides": {{
                        "paneProperties.background": "{colors['background']}",
                        "paneProperties.vertGridProperties.color": "#363c4e",
                        "paneProperties.horzGridProperties.color": "#363c4e",
                        "symbolWatermarkProperties.transparency": 90,
                        "scalesProperties.textColor": "{colors['text_color']}",
                        "mainSeriesProperties.candleStyle.wickUpColor": "#089981",
                        "mainSeriesProperties.candleStyle.wickDownColor": "#f23645",
                        "mainSeriesProperties.candleStyle.upColor": "#089981",
                        "mainSeriesProperties.candleStyle.downColor": "#f23645"
                    }},
                    "disabled_features": ["header_saveload"],
                    "enabled_features": ["move_logo_to_main_pane"]
                }});
                
                console.log('美股 TradingView Widget 已載入完成');
            }}
            
            // 確保頁面載入後再初始化
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initWidget);
            }} else {{
                initWidget();
            }}
        </script>
        """
    
    def _create_complete_page(
        self,
        symbol: str,
        chart_html: str,
        market_type: str,
        colors: Dict[str, str],
        stock_data: Dict = None,
        ai_recommendations: Dict = None,
        strategy_info: Dict = None
    ) -> str:
        """創建完整的 HTML 頁面"""
        
        is_taiwan = self.is_taiwan_stock(symbol)
        
        return f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} - 混合模式 TradingView 系統</title>
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
        
        .chart-section {{
            flex: 2.5;
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
        
        .chart-title {{
            font-size: 18px;
            font-weight: 600;
        }}
        
        .market-badge {{
            background: {'#28a745' if is_taiwan else '#007bff'};
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        }}
        
        .chart-content {{
            width: 100%;
            height: calc(100% - 70px);
            position: relative;
        }}
        
        .data-panel {{
            width: 400px;
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
        
        .market-switcher {{
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
        }}
        
        .switch-btn {{
            padding: 6px 12px;
            border: 1px solid {colors['border_color']};
            border-radius: 6px;
            background: {colors['panel_bg']};
            color: {colors['text_color']};
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s ease;
        }}
        
        .switch-btn:hover {{
            background: #007bff;
            color: white;
            border-color: #007bff;
        }}
        
        .switch-btn.active {{
            background: #007bff;
            color: white;
            border-color: #007bff;
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="chart-section">
            <div class="chart-header">
                <div>
                    <div class="chart-title">📊 {symbol}</div>
                    <div style="font-size: 12px; color: #6c757d; margin-top: 2px;">
                        {market_type}
                    </div>
                </div>
                <div class="market-badge">
                    {'🇹🇼 台股 (開放資料)' if is_taiwan else '🇺🇸 美股 (Widget)'}
                </div>
            </div>
            <div class="chart-content">
                {chart_html}
            </div>
        </div>
        
        <div class="data-panel">
            <!-- 市場切換器 -->
            <div class="info-card" style="padding: 15px;">
                <h4 style="margin-bottom: 10px;">🔄 測試不同市場</h4>
                <div class="market-switcher">
                    <button class="switch-btn" onclick="testSymbol('AAPL')">AAPL (美股Widget)</button>
                    <button class="switch-btn" onclick="testSymbol('2330.TW')">2330 (台股Library)</button>
                </div>
                <div style="display: flex; gap: 8px;">
                    <input type="text" id="customSymbol" placeholder="輸入符號..." 
                           style="flex: 1; padding: 8px; border: 1px solid {colors['border_color']}; border-radius: 4px; background: {colors['input_bg']}; color: {colors['text_color']};">
                    <button onclick="testSymbol(document.getElementById('customSymbol').value)" 
                            style="padding: 8px 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        測試
                    </button>
                </div>
            </div>
            
            <!-- 架構說明 -->
            <div class="info-card">
                <h4 style="margin-bottom: 15px;">🏗️ 混合架構說明</h4>
                <div style="font-size: 13px; line-height: 1.6;">
                    <div style="margin-bottom: 10px;">
                        <strong>🇺🇸 美股：</strong><br>
                        • 使用 TradingView Widget<br>
                        • TradingView 內建數據源<br>
                        • 即時更新，無需額外設定
                    </div>
                    <div>
                        <strong>🇹🇼 台股：</strong><br>
                        • 使用 TradingView Charting Library<br>
                        • TWSE/TPEx 開放資料<br>
                        • 自定義 Datafeed 實現<br>
                        • 完全合規，無版權問題
                    </div>
                </div>
            </div>
            
            <!-- 技術指標 -->
            <div class="info-card">
                <h4 style="margin-bottom: 15px;">📈 技術指標</h4>
                <div style="font-size: 13px;">
                    <div style="margin-bottom: 8px;">✅ K線圖</div>
                    <div style="margin-bottom: 8px;">✅ 成交量</div>
                    <div style="margin-bottom: 8px;">✅ RSI 指標</div>
                    <div style="margin-bottom: 8px;">
                        {'✅ 台股交易時間 (09:00-13:30)' if is_taiwan else '✅ 美股交易時間 (09:30-16:00)'}
                    </div>
                    <div>
                        {'✅ 台北時區 (Asia/Taipei)' if is_taiwan else '✅ 紐約時區 (America/New_York)'}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function testSymbol(symbol) {{
            if (!symbol || symbol.trim() === '') {{
                alert('請輸入有效的股票代號');
                return;
            }}
            
            // 構建新的 URL
            const newUrl = window.location.origin + '/chart/hybrid/' + symbol.trim().toUpperCase();
            window.location.href = newUrl;
        }}
        
        // 回調函數，用於處理符號變更
        window.onSymbolChanged = function(newSymbol) {{
            console.log('Symbol changed to:', newSymbol);
            // 可以在這裡更新右側數據面板
        }}
        
        // 高亮當前符號
        document.addEventListener('DOMContentLoaded', function() {{
            const currentSymbol = '{symbol}';
            const buttons = document.querySelectorAll('.switch-btn');
            
            buttons.forEach(btn => {{
                const btnText = btn.textContent;
                if (btnText.includes(currentSymbol) || 
                    (btnText.includes('2330') && currentSymbol.includes('2330')) ||
                    (btnText.includes('AAPL') && currentSymbol === 'AAPL')) {{
                    btn.classList.add('active');
                }}
            }});
        }});
    </script>
</body>
</html>
        """

# 全局實例
hybrid_chart = HybridTradingViewChart()

def get_hybrid_chart() -> HybridTradingViewChart:
    """獲取混合圖表實例"""
    return hybrid_chart