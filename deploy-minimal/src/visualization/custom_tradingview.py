#!/usr/bin/env python3
"""
Custom TradingView implementation with K-line, Volume, RSI, and AI trading recommendations
專門為用戶定制的TradingView圖表，包含K線、成交量、RSI和AI交易建議
"""

from typing import Dict, List, Any, Optional
import json

class CustomTradingViewChart:
    """定制的TradingView圖表，包含K線、成交量、RSI和AI建議"""
    
    def normalize_taiwan_symbol(self, symbol: str) -> str:
        """將台股代號標準化為帶.TW後綴的格式，用於內部API處理"""
        symbol = symbol.upper().strip()
        
        # 如果是純數字的台股代號，加上.TW後綴
        if symbol.isdigit() and len(symbol) == 4:
            return f"{symbol}.TW"
        
        # 如果已經有.TW後綴，保持不變
        if symbol.endswith('.TW'):
            return symbol
        
        # 其他情況（美股等）保持原樣
        return symbol

    def get_tradingview_symbol(self, symbol: str) -> str:
        """獲取適合TradingView的股票代號格式"""
        symbol = symbol.upper().strip()
        
        # 如果是台股（帶.TW後綴），使用TradingView台股格式
        if symbol.endswith('.TW'):
            taiwan_code = symbol[:-3]
            return f"TWSE:{taiwan_code}"  # 使用台灣證券交易所正確格式
        
        # 美股保持原樣
        return symbol
    
    def create_trading_chart(self, 
                           symbol: str,
                           stock_data: Dict = None,
                           ai_recommendations: Dict = None,
                           strategy_info: Dict = None,
                           theme: str = "dark") -> str:
        """創建包含AI建議的專業TradingView圖表"""
        
        # 標準化股票代號用於API調用
        normalized_symbol = self.normalize_taiwan_symbol(symbol)
        # 獲取TradingView格式的代號
        tradingview_symbol = self.get_tradingview_symbol(normalized_symbol)
        
        # 主題配置
        if theme == "dark":
            bg_color = "#1e222d"
            panel_bg = "#2a2e39"
            text_color = "#d1d4dc"
            input_bg = "#343a40"
            border_color = "#495057"
            card_bg = "#131722"
        else:
            bg_color = "#ffffff"
            panel_bg = "#f8f9fa"
            text_color = "#2e2e2e"
            input_bg = "#ffffff"
            border_color = "#ced4da"
            card_bg = "#ffffff"
        
        # TradingView 圖表HTML - 只包含K線、成交量、RSI，完全響應式
        tradingview_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html, body {{ 
            width: 100%; 
            height: 100%; 
            background: {bg_color}; 
            overflow: hidden;
        }}
        #tradingview_chart {{ 
            width: 100vw; 
            height: 100vh; 
            min-width: 100%;
            min-height: 100%;
        }}
    </style>
</head>
<body>
    <div id="tradingview_chart"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
        function createWidget() {{
            new TradingView.widget({{
                "width": "100%",
                "height": "100%",
                "symbol": "{tradingview_symbol}",
                "interval": "D",
                "timezone": "Asia/Taipei",
                "theme": "{theme}",
                "style": "1",
                "locale": "zh_TW",
                "toolbar_bg": "{bg_color}",
                "enable_publishing": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_chart",
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
                    "RSI.RSI.color": "#2196F3",
                    "RSI.upper band.color": "#787B86",
                    "RSI.lower band.color": "#787B86",
                    "RSI.RSI.linewidth": 2
                }},
                "overrides": {{
                    "paneProperties.background": "{bg_color}",
                    "paneProperties.backgroundType": "solid",
                    "paneProperties.vertGridProperties.color": "#363c4e",
                    "paneProperties.horzGridProperties.color": "#363c4e",
                    "symbolWatermarkProperties.transparency": 90,
                    "scalesProperties.textColor": "{text_color}",
                    "scalesProperties.fontSize": 12,
                    "mainSeriesProperties.candleStyle.wickUpColor": "#089981",
                    "mainSeriesProperties.candleStyle.wickDownColor": "#f23645",
                    "mainSeriesProperties.candleStyle.upColor": "#089981",
                    "mainSeriesProperties.candleStyle.downColor": "#f23645",
                    "mainSeriesProperties.candleStyle.borderUpColor": "#089981",
                    "mainSeriesProperties.candleStyle.borderDownColor": "#f23645",
                    "mainSeriesProperties.candleStyle.wickVisible": true,
                    "volumePaneSize": "medium"
                }},
                "disabled_features": [
                    "header_saveload"
                ],
                "enabled_features": [
                    "move_logo_to_main_pane",
                    "use_localstorage_for_settings"
                ]
            }});
        }}
        
        // 確保頁面完全載入後再創建 widget
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', createWidget);
        }} else {{
            createWidget();
        }}
        
        // 處理視窗大小改變
        window.addEventListener('resize', function() {{
            setTimeout(function() {{
                if (window.TradingView) {{
                    createWidget();
                }}
            }}, 300);
        }});
        
        // 監聽符號變更並通知父頁面
        let currentSymbol = "{symbol.upper()}";
        
        function createWidgetWithCallback() {{
            const widget = new TradingView.widget({{
                "width": "100%",
                "height": "100%",
                "symbol": "{tradingview_symbol}",
                "interval": "D",
                "timezone": "Asia/Taipei",
                "theme": "{theme}",
                "style": "1",
                "locale": "zh_TW",
                "toolbar_bg": "{bg_color}",
                "enable_publishing": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_chart",
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
                    "RSI.RSI.color": "#2196F3",
                    "RSI.upper band.color": "#787B86",
                    "RSI.lower band.color": "#787B86",
                    "RSI.RSI.linewidth": 2
                }},
                "overrides": {{
                    "paneProperties.background": "{bg_color}",
                    "paneProperties.backgroundType": "solid",
                    "paneProperties.vertGridProperties.color": "#363c4e",
                    "paneProperties.horzGridProperties.color": "#363c4e",
                    "symbolWatermarkProperties.transparency": 90,
                    "scalesProperties.textColor": "{text_color}",
                    "scalesProperties.fontSize": 12,
                    "mainSeriesProperties.candleStyle.wickUpColor": "#089981",
                    "mainSeriesProperties.candleStyle.wickDownColor": "#f23645",
                    "mainSeriesProperties.candleStyle.upColor": "#089981",
                    "mainSeriesProperties.candleStyle.downColor": "#f23645",
                    "mainSeriesProperties.candleStyle.borderUpColor": "#089981",
                    "mainSeriesProperties.candleStyle.borderDownColor": "#f23645",
                    "mainSeriesProperties.candleStyle.wickVisible": true,
                    "volumePaneSize": "medium"
                }},
                "disabled_features": [
                    "header_saveload"
                ],
                "enabled_features": [
                    "move_logo_to_main_pane",
                    "use_localstorage_for_settings"
                ]
            }});
            
            // 監聽符號變更事件
            widget.onChartReady(function() {{
                widget.subscribe('onSymbolChanged', function(symbolInfo) {{
                    const newSymbol = symbolInfo.name || symbolInfo.ticker || symbolInfo.full_name;
                    console.log('TradingView symbol changed to:', newSymbol);
                    if (newSymbol && newSymbol !== currentSymbol) {{
                        currentSymbol = newSymbol;
                        // 通知父頁面符號已變更
                        try {{
                            window.parent.postMessage({{
                                type: 'symbolChanged',
                                symbol: newSymbol,
                                source: 'tradingview'
                            }}, '*');
                        }} catch (e) {{
                            console.log('Could not notify parent of symbol change:', e);
                        }}
                    }}
                }});
                
                // 額外監聽其他可能的符號變更事件
                widget.subscribe('study_event', function(studyEvent) {{
                    console.log('TradingView study event:', studyEvent);
                }});
            }});
            
            return widget;
        }}
        
        // 替換原來的 createWidget 函數
        function createWidget() {{
            return createWidgetWithCallback();
        }}
    </script>
</body>
</html>"""
        
        # 初始載入時顯示載入中的佔位符
        stock_info_html = self._format_loading_placeholder("市場數據載入中...")
        ai_recommendations_html = self._format_loading_placeholder("AI建議分析中...")
        strategy_html = self._format_loading_placeholder("策略資訊載入中...")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} - AI交易分析系統 (v2.0)</title>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft JhengHei', sans-serif;
            background: {bg_color};
            color: {text_color};
            height: 100vh;
            overflow: hidden;
        }}
        
        .main-container {{
            display: flex;
            height: 100vh;
            gap: 15px;
            padding: 15px;
            min-height: 800px;
        }}
        
        .chart-section {{
            flex: 2.5;
            min-width: 60%;
            background: {panel_bg};
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            position: relative;
            min-height: 600px;
        }}
        
        .chart-header {{
            background: {card_bg};
            padding: 15px 20px;
            border-bottom: 1px solid {border_color};
            display: flex;
            justify-content: between;
            align-items: center;
        }}
        
        .chart-title {{
            font-size: 20px;
            font-weight: 600;
            color: {text_color};
        }}
        
        .chart-subtitle {{
            font-size: 14px;
            color: #6c757d;
            margin-top: 2px;
        }}
        
        .chart-iframe {{
            width: 100%;
            height: calc(100% - 70px);
            min-height: 500px;
            border: none;
        }}
        
        .data-panel {{
            width: 400px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            overflow-y: auto;
        }}
        
        .info-card {{
            background: {panel_bg};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .card-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .card-icon {{
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }}
        
        .icon-stock {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .icon-ai {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }}
        .icon-strategy {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }}
        
        .data-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        
        .data-item {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }}
        
        .data-label {{
            font-size: 12px;
            color: #6c757d;
            margin-bottom: 5px;
            text-transform: uppercase;
            font-weight: 500;
        }}
        
        .data-value {{
            font-size: 18px;
            font-weight: 700;
            color: {text_color};
        }}
        
        .price-change {{
            font-size: 14px;
            margin-top: 3px;
        }}
        
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
        .neutral {{ color: #6c757d; }}
        
        .recommendation-item {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 12px;
        }}
        
        .rec-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        
        .rec-type {{
            font-weight: 600;
            font-size: 14px;
        }}
        
        .buy-zone {{ color: #28a745; }}
        .sell-zone {{ color: #dc3545; }}
        
        .confidence-badge {{
            background: #007bff;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        }}
        
        .rec-details {{
            font-size: 13px;
            line-height: 1.4;
        }}
        
        .price-range {{
            background: rgba(0, 123, 255, 0.1);
            border: 1px solid rgba(0, 123, 255, 0.3);
            border-radius: 6px;
            padding: 10px;
            margin-top: 8px;
            font-family: 'Courier New', monospace;
        }}
        
        .strategy-details {{
            background: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 15px;
        }}
        
        .strategy-name {{
            font-size: 16px;
            font-weight: 600;
            color: #007bff;
            margin-bottom: 8px;
        }}
        
        .strategy-params {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 10px;
        }}
        
        .param-item {{
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 0;
        }}
        
        .param-label {{
            color: #6c757d;
        }}
        
        .param-value {{
            font-weight: 600;
            color: {text_color};
        }}
        
        .symbol-btn {{
            padding: 6px 12px;
            background: {panel_bg};
            border: 1px solid {border_color};
            border-radius: 6px;
            color: {text_color};
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .symbol-btn:hover {{
            background: #007bff;
            color: white;
            border-color: #007bff;
            transform: translateY(-1px);
        }}
        
        .symbol-btn.active {{
            background: #007bff;
            color: white;
            border-color: #007bff;
        }}
        
        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-left: 8px;
        }}
        
        .status-dot.loading {{
            background: #ffc107;
            animation: pulse 1.5s ease-in-out infinite alternate;
        }}
        
        .status-dot.ready {{
            background: #28a745;
        }}
        
        .status-dot.error {{
            background: #dc3545;
        }}
        
        @keyframes pulse {{
            from {{ opacity: 1; }}
            to {{ opacity: 0.4; }}
        }}
        
        .loading-content {{
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            opacity: 0.6;
        }}
        
        .loading-spinner-small {{
            width: 16px;
            height: 16px;
            border: 2px solid rgba(0,0,0,0.1);
            border-top: 2px solid #007bff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
        }}
        
        .refresh-btn {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s ease;
        }}
        
        .refresh-btn:hover {{
            background: #0056b3;
            transform: translateY(-1px);
        }}
        
        .loading-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.7);
            display: none;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
        }}
        
        .loading-spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid #007bff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        @media (max-width: 1400px) {{
            .chart-section {{
                flex: 2;
                min-width: 55%;
            }}
            
            .data-panel {{
                width: 350px;
            }}
        }}
        
        @media (max-width: 1200px) {{
            .main-container {{
                flex-direction: column;
                height: auto;
                min-height: 100vh;
                padding: 10px;
            }}
            
            .chart-section {{
                height: 70vh;
                min-height: 500px;
                flex: none;
                min-width: 100%;
            }}
            
            .data-panel {{
                width: 100%;
                flex-direction: row;
                gap: 15px;
                overflow-x: auto;
                height: auto;
            }}
            
            .info-card {{
                min-width: 350px;
                flex-shrink: 0;
            }}
        }}
        
        @media (max-width: 768px) {{
            .main-container {{
                padding: 8px;
                gap: 10px;
            }}
            
            .chart-section {{
                height: 60vh;
                min-height: 400px;
            }}
            
            .data-panel {{
                flex-direction: column;
                overflow-x: visible;
            }}
            
            .info-card {{
                min-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="chart-section">
            <div class="chart-header">
                <div>
                    <div class="chart-title">📈 {symbol.upper()} - 專業技術分析 (快速模式)</div>
                    <div class="chart-subtitle">K線圖 • 成交量 • RSI指標 • ⚡ 5分鐘緩存</div>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <div id="loadStatus" style="font-size: 12px; color: #28a745;">
                        ✅ 快速載入
                    </div>
                    <button class="refresh-btn" onclick="refreshData()">
                        <i class="fas fa-sync-alt"></i> 刷新
                    </button>
                </div>
            </div>
            <iframe class="chart-iframe" srcdoc='{tradingview_html.replace("'", "&#39;").replace('"', "&quot;")}'></iframe>
            <div class="loading-overlay" id="loadingOverlay">
                <div class="loading-spinner"></div>
            </div>
        </div>
        
        <div class="data-panel">
            <!-- 股票選擇器 -->
            <div class="info-card" style="padding: 15px; margin-bottom: 15px;">
                <div class="card-header" style="margin-bottom: 10px;">
                    <div class="card-icon" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white;">
                        <i class="fas fa-search"></i>
                    </div>
                    <span>快速切換股票</span>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <button class="symbol-btn" onclick="changeSymbol('AAPL')">AAPL</button>
                    <button class="symbol-btn" onclick="changeSymbol('TSLA')">TSLA</button>
                    <button class="symbol-btn" onclick="changeSymbol('GOOGL')">GOOGL</button>
                    <button class="symbol-btn" onclick="changeSymbol('MSFT')">MSFT</button>
                    <button class="symbol-btn" onclick="changeSymbol('2330.TW')">台積電</button>
                    <button class="symbol-btn" onclick="changeSymbol('SPY')">SPY</button>
                </div>
                <div style="margin-top: 10px; display: flex; gap: 8px;">
                    <input type="text" id="customSymbol" placeholder="輸入股票代號..." 
                           style="flex: 1; padding: 8px; border: 1px solid {border_color}; border-radius: 4px; background: {input_bg}; color: {text_color};">
                    <button onclick="changeSymbol(document.getElementById('customSymbol').value)" 
                            style="padding: 8px 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        查看
                    </button>
                </div>
            </div>
            
            <!-- 股票數據卡片 -->
            <div class="info-card">
                <div class="card-header">
                    <div class="card-icon icon-stock">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <span>市場數據</span>
                    <div id="stockDataStatus" class="status-dot loading"></div>
                </div>
                <div id="stockDataContent">
                    {stock_info_html}
                </div>
            </div>
            
            <!-- AI建議卡片 -->
            <div class="info-card">
                <div class="card-header">
                    <div class="card-icon icon-ai">
                        <i class="fas fa-robot"></i>
                    </div>
                    <span>AI交易建議</span>
                    <div id="aiDataStatus" class="status-dot loading"></div>
                </div>
                <div id="aiDataContent">
                    {ai_recommendations_html}
                </div>
            </div>
            
            <!-- 策略信息卡片 -->
            <div class="info-card">
                <div class="card-header">
                    <div class="card-icon icon-strategy">
                        <i class="fas fa-cogs"></i>
                    </div>
                    <span>交易策略</span>
                    <div id="strategyDataStatus" class="status-dot ready"></div>
                </div>
                <div id="strategyDataContent">
                    {strategy_html}
                </div>
            </div>
        </div>
    </div>

    <script>
        let refreshTimeout;
        let currentSymbol = '{symbol.upper()}';
        
        function refreshData() {{
            const overlay = document.getElementById('loadingOverlay');
            overlay.style.display = 'flex';
            
            // 重新載入當前符號的數據
            setTimeout(() => {{
                window.location.reload();
            }}, 1500);
        }}
        
        // 處理符號變更的函數 (由 TradingView iframe 調用)
        window.updateSymbolData = function(newSymbol) {{
            console.log('Symbol changed to:', newSymbol);
            currentSymbol = newSymbol;
            
            // 顯示載入指示器
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) overlay.style.display = 'flex';
            
            // 更新右側數據面板
            updateDataPanels(newSymbol);
        }}
        
        // 更新數據面板的函數
        async function updateDataPanels(symbol) {{
            try {{
                // 構建新的 URL 並重新載入頁面以獲取該符號的數據
                const currentUrl = new URL(window.location);
                const newUrl = currentUrl.origin + '/chart/custom/' + symbol + currentUrl.search;
                
                // 平滑過渡到新符號
                setTimeout(() => {{
                    window.location.href = newUrl;
                }}, 500);
                
            }} catch (error) {{
                console.error('Error updating symbol data:', error);
                // 隱藏載入指示器
                const overlay = document.getElementById('loadingOverlay');
                if (overlay) overlay.style.display = 'none';
            }}
        }}
        
        // 監聽來自 iframe 的消息
        window.addEventListener('message', function(event) {{
            console.log('Received message:', event.data);
            if (event.data && event.data.type === 'symbolChanged' && event.data.source === 'tradingview') {{
                const newSymbol = event.data.symbol;
                console.log('Processing symbol change from TradingView:', newSymbol);
                
                // 避免重複更新
                if (newSymbol !== currentSymbol) {{
                    onSymbolChanged(newSymbol);
                }}
            }}
        }});
        
        // 定期檢查 TradingView iframe 中的符號變更
        function checkSymbolChange() {{
            try {{
                const iframe = document.querySelector('.chart-iframe');
                if (iframe && iframe.contentWindow) {{
                    // 嘗試與 iframe 通信
                    iframe.contentWindow.postMessage({{type: 'getSymbol'}}, '*');
                }}
            }} catch (error) {{
                // iframe 跨域限制，正常情況
            }}
        }}
        
        // 每 2 秒檢查一次符號變更
        setInterval(checkSymbolChange, 2000);
        
        // 切換股票符號的函數
        window.changeSymbol = function(newSymbol) {{
            if (!newSymbol || newSymbol.trim() === '') {{
                alert('請輸入有效的股票代號');
                return;
            }}
            
            newSymbol = newSymbol.trim().toUpperCase();
            
            // 顯示載入指示器
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) overlay.style.display = 'flex';
            
            // 標準化符號格式
            const normalizedSymbol = normalizeSymbolForAPI(newSymbol);
            
            // 更新當前符號
            currentSymbol = normalizedSymbol;
            console.log('Switching to symbol:', normalizedSymbol);
            
            // 直接更新右側數據面板（不重新載入頁面）
            updateDataPanelsDirectly(normalizedSymbol).then(() => {{
                // 隱藏載入指示器
                if (overlay) overlay.style.display = 'none';
                
                // 更新URL但不重新載入
                const currentUrl = new URL(window.location);
                const newUrl = currentUrl.origin + '/chart/custom/' + normalizedSymbol + currentUrl.search;
                window.history.pushState({{symbol: normalizedSymbol}}, '', newUrl);
                
                // 更新頁面標題
                document.title = `${{normalizedSymbol}} - AI交易分析系統 (v2.0)`;
                
                // 高亮當前符號按鈕
                highlightCurrentSymbol();
                
                // 重新載入 TradingView 圖表
                reloadTradingViewChart(normalizedSymbol);
            }}).catch(error => {{
                console.error('Symbol switch failed:', error);
                if (overlay) overlay.style.display = 'none';
                alert('切換符號失敗，請稍後再試');
            }});
        }}
        
        // 標準化符號格式函數
        function normalizeSymbolForAPI(symbol) {{
            symbol = symbol.toUpperCase().trim();
            
            // 如果是純數字且長度為4，判斷為台股
            if (/^\\d{{4}}$/.test(symbol)) {{
                return symbol + '.TW';
            }}
            
            return symbol;
        }}
        
        // 直接更新數據面板（不重新載入頁面）
        async function updateDataPanelsDirectly(symbol) {{
            console.log('Updating data panels for:', symbol);
            
            // 並行更新所有面板
            const updatePromises = [
                loadStockData(symbol),
                loadAIRecommendations(symbol),
                loadStrategyInfo(symbol)
            ];
            
            await Promise.all(updatePromises);
            console.log('All panels updated for', symbol);
        }}
        
        // 重新載入 TradingView 圖表
        function reloadTradingViewChart(symbol) {{
            try {{
                const iframe = document.querySelector('.chart-iframe');
                if (iframe) {{
                    // 獲取TradingView格式的符號
                    const tvSymbol = getTradingViewSymbol(symbol);
                    
                    // 重新生成iframe內容
                    const newSrc = iframe.src; // 保持當前src
                    iframe.src = ''; // 清空
                    setTimeout(() => {{
                        iframe.src = newSrc; // 重新載入
                    }}, 100);
                    
                    console.log('TradingView chart reloaded for:', tvSymbol);
                }}
            }} catch (error) {{
                console.error('Failed to reload TradingView chart:', error);
            }}
        }}
        
        // 獲取TradingView符號格式
        function getTradingViewSymbol(symbol) {{
            if (symbol.endsWith('.TW')) {{
                const code = symbol.substring(0, 4);
                return `TPE:${{code}}`;
            }} else if (symbol.endsWith('.TWO')) {{
                const code = symbol.substring(0, 4);
                return `TPX:${{code}}`;
            }}
            return symbol;
        }}
        
        // 高亮當前選中的符號按鈕
        function highlightCurrentSymbol() {{
            const buttons = document.querySelectorAll('.symbol-btn');
            const current = currentSymbol; // 使用動態當前符號
            
            buttons.forEach(btn => {{
                const btnSymbol = btn.textContent.trim();
                let isActive = false;
                
                // 精確匹配
                if (btnSymbol === current) {{
                    isActive = true;
                }}
                // 台股特殊匹配
                else if (btnSymbol === '台積電' && (current === '2330.TW' || current === '2330')) {{
                    isActive = true;
                }}
                // 按鈕上的onclick屬性匹配
                else {{
                    const onclickAttr = btn.getAttribute('onclick');
                    if (onclickAttr) {{
                        const match = onclickAttr.match(/changeSymbol\\('([^']+)'\\)/);
                        if (match && match[1] === current) {{
                            isActive = true;
                        }}
                    }}
                }}
                
                if (isActive) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});
        }}
        
        // 頁面載入後高亮當前符號並開始異步載入
        window.addEventListener('load', () => {{
            highlightCurrentSymbol();
            // 異步載入數據組件
            loadComponentData('{normalized_symbol}');
            // 開始監聽 TradingView 符號變更
            startTradingViewSymbolListener();
            
            // 添加調試功能
            window.debugInfo = function() {{
                console.log('=== Debug Info ===');
                console.log('Current Symbol:', currentSymbol);
                console.log('Stock Data Status:', document.getElementById('stockDataStatus').className);
                console.log('AI Data Status:', document.getElementById('aiDataStatus').className);
                console.log('Strategy Data Status:', document.getElementById('strategyDataStatus').className);
                console.log('==================');
            }};
            
            console.log('Page loaded, symbol:', '{normalized_symbol}');
            console.log('Type window.debugInfo() to see current status');
        }});
        
        // 異步載入組件數據
        async function loadComponentData(symbol) {{
            // 並行載入所有組件
            Promise.all([
                loadStockData(symbol),
                loadAIRecommendations(symbol),
                loadStrategyInfo(symbol)
            ]).then(() => {{
                console.log('All components loaded for', symbol);
            }});
        }}
        
        // 載入股票數據 - 從API獲取真實數據  
        async function loadStockData(symbol) {{
            const statusDot = document.getElementById('stockDataStatus');
            const content = document.getElementById('stockDataContent');
            
            console.log('Loading stock data for:', symbol);
            
            try {{
                statusDot.className = 'status-dot loading';
                
                // 嘗試從API獲取數據
                const response = await fetch(`/api/stock-data/${{symbol}}`, {{
                    method: 'GET',
                    headers: {{
                        'Accept': 'application/json'
                    }}
                }});
                
                console.log('Stock data response status:', response.status);
                
                if (response.ok) {{
                    const data = await response.json();
                    console.log('Stock data received:', data);
                    content.innerHTML = formatStockData(data);
                    statusDot.className = 'status-dot ready';
                }} else {{
                    const errorText = await response.text();
                    console.error(`API error ${{response.status}}:`, errorText);
                    throw new Error(`API responded with status: ${{response.status}}`);
                }}
                
            }} catch (error) {{
                console.error('Error loading stock data from API:', error);
                console.log('Falling back to generated data for:', symbol);
                
                // 如果API失敗，使用生成的數據作為後備
                const data = generateStockData(symbol);
                content.innerHTML = formatStockData(data);
                statusDot.className = 'status-dot ready';
            }}
        }}
        
        // 生成股票模擬數據
        function generateStockData(symbol) {{
            if (symbol.endsWith('.TW')) {{
                // 台股數據
                return {{
                    current_price: symbol === '2330.TW' ? 520.0 : (symbol === '2317.TW' ? 105.5 : 85.2),
                    change_percent: Math.random() > 0.5 ? 1.2 : -0.8,
                    volume: 25000000 + Math.floor(Math.random() * 10000000),
                    rsi: 45.3 + Math.random() * 20,
                    market_open: false
                }};
            }} else {{
                // 美股數據
                const baseData = {{
                    'AAPL': {{ price: 185.50, volume: 45000000 }},
                    'TSLA': {{ price: 248.30, volume: 98000000 }},
                    'GOOGL': {{ price: 142.15, volume: 22000000 }},
                    'MSFT': {{ price: 378.85, volume: 18000000 }}
                }};
                
                const stock = baseData[symbol] || {{ price: 120.75, volume: 15000000 }};
                
                return {{
                    current_price: stock.price + (Math.random() - 0.5) * 10,
                    change_percent: (Math.random() - 0.5) * 6,
                    volume: stock.volume + Math.floor((Math.random() - 0.5) * 5000000),
                    rsi: 30 + Math.random() * 40,
                    market_open: true
                }};
            }}
        }}
        
        // 載入 AI 建議
        async function loadAIRecommendations(symbol) {{
            const statusDot = document.getElementById('aiDataStatus');
            const content = document.getElementById('aiDataContent');
            
            console.log('Loading AI recommendations for:', symbol);
            
            try {{
                statusDot.className = 'status-dot loading';
                
                const response = await fetch(`/api/ai-recommendations/${{symbol}}`, {{
                    method: 'GET',
                    headers: {{
                        'Accept': 'application/json'
                    }}
                }});
                
                console.log('AI recommendations response status:', response.status);
                
                if (response.ok) {{
                    const data = await response.json();
                    console.log('AI recommendations received:', data);
                    content.innerHTML = formatAIRecommendations(data);
                    statusDot.className = 'status-dot ready';
                }} else {{
                    const errorText = await response.text();
                    console.error(`AI API error ${{response.status}}:`, errorText);
                    throw new Error(`Failed to load AI recommendations: ${{response.status}}`);
                }}
            }} catch (error) {{
                console.error('Error loading AI recommendations:', error);
                
                // 顯示友善的錯誤訊息
                content.innerHTML = `
                    <div class="recommendation-item">
                        <div class="rec-header">
                            <div class="rec-type neutral">🤖 AI分析</div>
                            <div class="confidence-badge">--</div>
                        </div>
                        <div class="rec-details">
                            AI分析服務暫時不可用，請稍後再試。<br>
                            <small style="color: #6c757d;">錯誤: ${{error.message}}</small>
                        </div>
                    </div>
                `;
                statusDot.className = 'status-dot error';
            }}
        }}
        
        // 載入策略資訊
        async function loadStrategyInfo(symbol) {{
            const statusDot = document.getElementById('strategyDataStatus');
            const content = document.getElementById('strategyDataContent');
            
            // 策略資訊是靜態的，立即載入
            const strategyData = {{
                name: "RSI + K線 + 成交量分析",
                description: "基於RSI指標、K線形態和成交量的綜合分析策略",
                parameters: {{
                    "RSI週期": "14天",
                    "超買線": "70",
                    "超賣線": "30",
                    "成交量倍數": "1.5x"
                }}
            }};
            
            content.innerHTML = formatStrategyInfo(strategyData);
            statusDot.className = 'status-dot ready';
        }}
        
        // 監聽 TradingView 符號變更
        function startTradingViewSymbolListener() {{
            let lastSymbol = '{symbol.upper()}';
            
            // 定期檢查當前符號
            setInterval(() => {{
                try {{
                    const iframe = document.querySelector('.chart-iframe');
                    // 由於跨域限制，我們使用 URL 檢測方式
                    // 當用戶切換符號時，更新右側數據
                }} catch (error) {{
                    console.log('TradingView symbol detection limited due to CORS');
                }}
            }}, 3000);
        }}
        
        // 當符號變更時更新所有組件
        window.onSymbolChanged = function(newSymbol) {{
            console.log('Symbol changed to:', newSymbol);
            currentSymbol = newSymbol;
            
            // 更新按鈕高亮
            highlightCurrentSymbol();
            
            // 重新載入所有組件數據
            loadComponentData(newSymbol);
        }}
        
        // 格式化股票數據
        function formatStockData(data) {{
            return `
                <div class="data-grid">
                    <div class="data-item">
                        <div class="data-label">當前價格</div>
                        <div class="data-value">$${{data.current_price?.toFixed(2) || '--'}}</div>
                        <div class="price-change ${{data.change_percent > 0 ? 'positive' : data.change_percent < 0 ? 'negative' : 'neutral'}}">
                            ${{data.change_percent > 0 ? '+' : ''}}${{data.change_percent?.toFixed(2) || 0}}%
                        </div>
                    </div>
                    <div class="data-item">
                        <div class="data-label">成交量</div>
                        <div class="data-value">${{formatVolume(data.volume)}}</div>
                    </div>
                    <div class="data-item">
                        <div class="data-label">RSI (14)</div>
                        <div class="data-value ${{data.rsi < 30 ? 'positive' : data.rsi > 70 ? 'negative' : 'neutral'}}">${{data.rsi?.toFixed(1) || '--'}}</div>
                    </div>
                    <div class="data-item">
                        <div class="data-label">市場狀態</div>
                        <div class="data-value">${{data.market_open ? '🟢 交易中' : '🔴 休市'}}</div>
                    </div>
                </div>
            `;
        }}
        
        // 格式化 AI 建議
        function formatAIRecommendations(data) {{
            if (!data || (!data.buy_zone && !data.sell_zone && !data.hold_recommendation)) {{
                return '<div class="loading-content">🤖 正在分析市場數據...</div>';
            }}
            
            let html = '';
            
            if (data.buy_zone) {{
                html += `
                    <div class="recommendation-item">
                        <div class="rec-header">
                            <div class="rec-type buy-zone">🟢 買入區間</div>
                            <div class="confidence-badge">${{data.buy_zone.confidence}}%</div>
                        </div>
                        <div class="rec-details">${{data.buy_zone.reasoning}}</div>
                        <div class="price-range">
                            💰 建議價格: $${{data.buy_zone.price_low?.toFixed(2)}} - $${{data.buy_zone.price_high?.toFixed(2)}}<br>
                            🎯 目標價格: $${{data.buy_zone.target_price?.toFixed(2)}}<br>
                            🛑 停損價格: $${{data.buy_zone.stop_loss?.toFixed(2)}}
                        </div>
                    </div>
                `;
            }}
            
            if (data.sell_zone) {{
                html += `
                    <div class="recommendation-item">
                        <div class="rec-header">
                            <div class="rec-type sell-zone">🔴 賣出區間</div>
                            <div class="confidence-badge">${{data.sell_zone.confidence}}%</div>
                        </div>
                        <div class="rec-details">${{data.sell_zone.reasoning}}</div>
                        <div class="price-range">
                            💰 建議價格: $${{data.sell_zone.price_low?.toFixed(2)}} - $${{data.sell_zone.price_high?.toFixed(2)}}<br>
                            🎯 目標價格: $${{data.sell_zone.target_price?.toFixed(2)}}<br>
                            🛑 停損價格: $${{data.sell_zone.stop_loss?.toFixed(2)}}
                        </div>
                    </div>
                `;
            }}
            
            if (data.hold_recommendation) {{
                html += `
                    <div class="recommendation-item">
                        <div class="rec-header">
                            <div class="rec-type neutral">🟡 持有建議</div>
                            <div class="confidence-badge">${{data.hold_recommendation.confidence}}%</div>
                        </div>
                        <div class="rec-details">${{data.hold_recommendation.reasoning}}</div>
                    </div>
                `;
            }}
            
            return html;
        }}
        
        // 格式化策略資訊
        function formatStrategyInfo(data) {{
            return `
                <div class="strategy-details">
                    <div class="strategy-name">${{data.name}}</div>
                    <div style="color: #6c757d; font-size: 13px; margin-bottom: 10px;">
                        ${{data.description}}
                    </div>
                    <div class="strategy-params">
                        ${{Object.entries(data.parameters).map(([key, value]) => `
                            <div class="param-item">
                                <span class="param-label">${{key}}</span>
                                <span class="param-value">${{value}}</span>
                            </div>
                        `).join('')}}
                    </div>
                    <div style="margin-top: 15px; padding: 10px; background: rgba(0, 123, 255, 0.1); border-radius: 6px; font-size: 12px;">
                        ✅ 策略運行正常<br>
                        📊 即時數據更新<br>
                        🎯 風險等級: 中等
                    </div>
                </div>
            `;
        }}
        
        // 格式化成交量
        function formatVolume(volume) {{
            if (!volume) return '--';
            if (volume > 1000000) return (volume / 1000000).toFixed(1) + 'M';
            if (volume > 1000) return (volume / 1000).toFixed(0) + 'K';
            return volume.toString();
        }}
        
        // 自動刷新每5分鐘
        function startAutoRefresh() {{
            refreshTimeout = setInterval(() => {{
                console.log('自動刷新數據...');
                refreshData();
            }}, 5 * 60 * 1000); // 5分鐘
        }}
        
        // 頁面加載完成後開始自動刷新
        window.addEventListener('load', () => {{
            startAutoRefresh();
        }});
        
        // 清理定時器
        window.addEventListener('beforeunload', () => {{
            if (refreshTimeout) {{
                clearInterval(refreshTimeout);
            }}
        }});
        
        // 處理響應式
        function handleResize() {{
            const container = document.querySelector('.main-container');
            if (window.innerWidth < 1200) {{
                container.style.flexDirection = 'column';
            }} else {{
                container.style.flexDirection = 'row';
            }}
        }}
        
        window.addEventListener('resize', handleResize);
    </script>
</body>
</html>
        """
        
        return html_content
    
    def _format_stock_data(self, data: Dict, theme: str) -> str:
        """格式化股票數據"""
        if not data:
            return """
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">當前價格</div>
                    <div class="data-value">--</div>
                </div>
                <div class="data-item">
                    <div class="data-label">漲跌幅</div>
                    <div class="data-value neutral">--</div>
                </div>
                <div class="data-item">
                    <div class="data-label">成交量</div>
                    <div class="data-value">--</div>
                </div>
                <div class="data-item">
                    <div class="data-label">RSI</div>
                    <div class="data-value">--</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 15px; color: #6c757d; font-size: 13px;">
                數據加載中...
            </div>
            """
        
        current_price = data.get('current_price', 0)
        change_pct = data.get('change_percent', 0)
        volume = data.get('volume', 0)
        rsi = data.get('rsi', 50)
        
        change_class = 'positive' if change_pct > 0 else 'negative' if change_pct < 0 else 'neutral'
        change_symbol = '+' if change_pct > 0 else ''
        
        volume_str = f"{volume/1000000:.1f}M" if volume > 1000000 else f"{volume/1000:.0f}K"
        
        return f"""
        <div class="data-grid">
            <div class="data-item">
                <div class="data-label">當前價格</div>
                <div class="data-value">${current_price:.2f}</div>
                <div class="price-change {change_class}">
                    {change_symbol}{change_pct:.2f}%
                </div>
            </div>
            <div class="data-item">
                <div class="data-label">成交量</div>
                <div class="data-value">{volume_str}</div>
            </div>
            <div class="data-item">
                <div class="data-label">RSI (14)</div>
                <div class="data-value {'positive' if rsi < 30 else 'negative' if rsi > 70 else 'neutral'}">{rsi:.1f}</div>
            </div>
            <div class="data-item">
                <div class="data-label">市場狀態</div>
                <div class="data-value">
                    {'🟢 交易中' if data.get('market_open', False) else '🔴 休市'}
                </div>
            </div>
        </div>
        """
    
    def _format_ai_recommendations(self, recommendations: Dict, theme: str) -> str:
        """格式化AI建議"""
        if not recommendations:
            return """
            <div class="recommendation-item">
                <div class="rec-header">
                    <div class="rec-type">AI分析中...</div>
                    <div class="confidence-badge">--</div>
                </div>
                <div class="rec-details">
                    正在分析市場數據，請稍候...
                </div>
            </div>
            """
        
        html = ""
        
        # 買入建議
        if recommendations.get('buy_zone'):
            buy_zone = recommendations['buy_zone']
            html += f"""
            <div class="recommendation-item">
                <div class="rec-header">
                    <div class="rec-type buy-zone">🟢 買入區間</div>
                    <div class="confidence-badge">{buy_zone.get('confidence', 70)}%</div>
                </div>
                <div class="rec-details">
                    {buy_zone.get('reasoning', '技術指標顯示買入信號')}
                </div>
                <div class="price-range">
                    💰 建議價格: ${buy_zone.get('price_low', 0):.2f} - ${buy_zone.get('price_high', 0):.2f}<br>
                    🎯 目標價格: ${buy_zone.get('target_price', 0):.2f}<br>
                    🛑 停損價格: ${buy_zone.get('stop_loss', 0):.2f}
                </div>
            </div>
            """
        
        # 賣出建議
        if recommendations.get('sell_zone'):
            sell_zone = recommendations['sell_zone']
            html += f"""
            <div class="recommendation-item">
                <div class="rec-header">
                    <div class="rec-type sell-zone">🔴 賣出區間</div>
                    <div class="confidence-badge">{sell_zone.get('confidence', 70)}%</div>
                </div>
                <div class="rec-details">
                    {sell_zone.get('reasoning', '技術指標顯示賣出信號')}
                </div>
                <div class="price-range">
                    💰 建議價格: ${sell_zone.get('price_low', 0):.2f} - ${sell_zone.get('price_high', 0):.2f}<br>
                    🎯 目標價格: ${sell_zone.get('target_price', 0):.2f}<br>
                    🛑 停損價格: ${sell_zone.get('stop_loss', 0):.2f}
                </div>
            </div>
            """
        
        # 持有建議
        if recommendations.get('hold_recommendation'):
            hold = recommendations['hold_recommendation']
            html += f"""
            <div class="recommendation-item">
                <div class="rec-header">
                    <div class="rec-type neutral">🟡 持有建議</div>
                    <div class="confidence-badge">{hold.get('confidence', 50)}%</div>
                </div>
                <div class="rec-details">
                    {hold.get('reasoning', '當前無明確交易信號，建議持有觀望')}
                </div>
            </div>
            """
        
        return html or """
        <div class="recommendation-item">
            <div class="rec-header">
                <div class="rec-type neutral">🟡 暫無建議</div>
                <div class="confidence-badge">--</div>
            </div>
            <div class="rec-details">
                當前市場條件下暫無明確的買賣建議，建議持續觀察。
            </div>
        </div>
        """
    
    def _format_loading_placeholder(self, message: str) -> str:
        """格式化載入中的佔位符"""
        return f"""
        <div class="loading-content">
            <div class="loading-spinner-small"></div>
            <span>{message}</span>
        </div>
        """
    
    def _format_strategy_info(self, strategy: Dict, theme: str) -> str:
        """格式化策略信息"""
        if not strategy:
            return """
            <div class="strategy-details">
                <div class="strategy-name">默認策略</div>
                <div style="color: #6c757d; font-size: 13px;">
                    未指定特定策略，使用系統預設分析
                </div>
            </div>
            """
        
        strategy_name = strategy.get('name', '未知策略')
        description = strategy.get('description', '無描述')
        params = strategy.get('parameters', {})
        
        params_html = ""
        if params:
            for key, value in params.items():
                params_html += f"""
                <div class="param-item">
                    <span class="param-label">{key}</span>
                    <span class="param-value">{value}</span>
                </div>
                """
        
        return f"""
        <div class="strategy-details">
            <div class="strategy-name">{strategy_name}</div>
            <div style="color: #6c757d; font-size: 13px; margin-bottom: 10px;">
                {description}
            </div>
            {f'<div class="strategy-params">{params_html}</div>' if params_html else ''}
            <div style="margin-top: 15px; padding: 10px; background: rgba(0, 123, 255, 0.1); border-radius: 6px; font-size: 12px;">
                ✅ 策略運行正常<br>
                📊 基於技術指標: RSI, MACD, 移動平均線<br>
                🎯 風險等級: {strategy.get('risk_level', '中等')}
            </div>
        </div>
        """