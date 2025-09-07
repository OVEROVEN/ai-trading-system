#!/usr/bin/env python3
"""
直接整合TradingView圖表組件
使用TradingView官方widget，無需自己生成圖表
"""

from typing import Dict, List, Any, Optional
import json

class TradingViewWidget:
    """TradingView官方圖表組件整合"""
    
    def create_tradingview_chart(self, 
                                symbol: str,
                                theme: str = "dark",
                                interval: str = "D",
                                width: int = 1200,
                                height: int = 800) -> str:
        """
        創建TradingView圖表
        
        Args:
            symbol: 股票代號
            theme: 主題 (dark/light)
            interval: 時間間隔 (1, 5, 15, 30, 60, 240, D, W, M)
            width: 寬度
            height: 高度
        """
        
        # TradingView配置
        widget_config = {
            "width": width,
            "height": height,
            "symbol": symbol.upper(),
            "interval": interval,
            "timezone": "Asia/Taipei",
            "theme": theme,
            "style": "1",  # 0=bars, 1=candles, 2=line, 3=area, 4=heiken-ashi
            "locale": "zh_TW",
            "toolbar_bg": "#f1f3f6" if theme == "light" else "#1e222d",
            "enable_publishing": False,
            "allow_symbol_change": True,
            "container_id": "tradingview_chart"
        }
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{symbol} - TradingView專業圖表</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 10px;
            background-color: {'#ffffff' if theme == 'light' else '#1e222d'};
            font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;
        }}
        .header {{
            color: {'#2e2e2e' if theme == 'light' else '#d1d4dc'};
            text-align: center;
            margin-bottom: 10px;
            font-size: 18px;
            font-weight: 600;
        }}
        .info {{
            color: {'#666' if theme == 'light' else '#888'};
            text-align: center;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        #tradingview_chart {{
            margin: 0 auto;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            padding: 20px;
            color: {'#666' if theme == 'light' else '#888'};
            font-size: 12px;
        }}
        .features {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px auto;
            max-width: 1000px;
            padding: 0 20px;
        }}
        .feature {{
            background: {'#f8f9fa' if theme == 'light' else '#2a2e39'};
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            color: {'#2e2e2e' if theme == 'light' else '#d1d4dc'};
        }}
        .feature-icon {{
            font-size: 24px;
            margin-bottom: 8px;
        }}
        .feature-title {{
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .feature-desc {{
            font-size: 12px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="header">
        📊 {symbol} • TradingView專業圖表
    </div>
    <div class="info">
        真正的TradingView圖表 • 即時數據 • 專業分析工具
    </div>
    
    <div id="tradingview_chart"></div>
    
    <div class="features">
        <div class="feature">
            <div class="feature-icon">📈</div>
            <div class="feature-title">專業級圖表</div>
            <div class="feature-desc">TradingView官方圖表引擎</div>
        </div>
        <div class="feature">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">即時數據</div>
            <div class="feature-desc">實時更新的市場數據</div>
        </div>
        <div class="feature">
            <div class="feature-icon">🛠️</div>
            <div class="feature-title">分析工具</div>
            <div class="feature-desc">完整的技術分析工具</div>
        </div>
        <div class="feature">
            <div class="feature-icon">🎨</div>
            <div class="feature-title">自訂介面</div>
            <div class="feature-desc">可自訂的圖表風格</div>
        </div>
    </div>
    
    <div class="footer">
        <p>由 TradingView 提供專業圖表服務</p>
        <p>本系統提供形態分析、AI策略討論、自動回測等功能</p>
    </div>

    <!-- TradingView Widget BEGIN -->
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
        new TradingView.widget({json.dumps(widget_config, indent=8)});
    </script>
    <!-- TradingView Widget END -->
</body>
</html>
        """
        
        return html_template
    
    def create_mini_chart(self, symbol: str, theme: str = "dark") -> str:
        """創建迷你TradingView圖表"""
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{symbol} - 迷你圖表</title>
    <meta charset="utf-8">
    <style>
        body {{
            margin: 0;
            padding: 10px;
            background-color: {'#ffffff' if theme == 'light' else '#1e222d'};
            font-family: Arial, sans-serif;
        }}
    </style>
</head>
<body>
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
        <div id="tradingview_mini_chart"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
            new TradingView.MediumWidget({{
                "symbols": [["{symbol.upper()}", "{symbol.upper()}"]],
                "chartOnly": false,
                "width": "100%",
                "height": 400,
                "locale": "zh_TW",
                "colorTheme": "{theme}",
                "autosize": true,
                "showVolume": true,
                "hideDateRanges": false,
                "scalePosition": "right",
                "scaleMode": "Normal",
                "fontFamily": "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
                "noTimeScale": false,
                "chartType": "candlesticks",
                "container_id": "tradingview_mini_chart"
            }});
        </script>
    </div>
    <!-- TradingView Widget END -->
</body>
</html>
        """
        
        return html_template
    
    def create_advanced_chart_with_data(self, 
                                       symbol: str, 
                                       analysis_data: Dict = None,
                                       theme: str = "dark") -> str:
        """創建帶有我們分析數據和AI聊天室的TradingView圖表"""
        
        # 將我們的分析數據格式化
        analysis_html = ""
        if analysis_data:
            patterns = analysis_data.get('patterns', [])
            signals = analysis_data.get('signals', [])
            
            if patterns or signals:
                analysis_html = f"""
        <div class="analysis-section">
            <h3>📊 AI分析結果</h3>
            """
                
                if patterns:
                    analysis_html += "<h4>🎯 檢測到的形態：</h4>"
                    for i, pattern in enumerate(patterns[:5], 1):  # 顯示前5個
                        confidence = pattern.get('confidence', 0)
                        direction = pattern.get('direction', 'Unknown')
                        target_price = pattern.get('target_price', 0)
                        start_date = pattern.get('start_date', '')
                        end_date = pattern.get('end_date', '')
                        current_price = pattern.get('current_price', 0)
                        buy_point = pattern.get('buy_point', 0)
                        stop_loss = pattern.get('stop_loss', 0)
                        risk_reward_ratio = pattern.get('risk_reward_ratio', 0)
                        
                        direction_icon = "📈" if direction == "bullish" else "📉" if direction == "bearish" else "➡️"
                        profit_potential = ((target_price - current_price) / current_price * 100) if current_price > 0 else 0
                        
                        analysis_html += f"""
            <div class="pattern-item">
                <div class="pattern-header">
                    <span class="pattern-number">{i}</span>
                    <strong>{pattern.get('pattern_name', 'Unknown')}</strong>
                    {direction_icon}
                </div>
                <div class="pattern-details">
                    <div>📊 信心度: <span class="confidence">{confidence:.1%}</span></div>
                    <div>💰 現價: <span class="current-price">${current_price:.2f}</span></div>
                    <div>🔵 買入點: <span class="buy-point">${buy_point:.2f}</span></div>
                    <div>🎯 目標價: <span class="target-price">${target_price:.2f}</span> ({profit_potential:+.1f}%)</div>
                    <div>🛑 停損: <span class="stop-loss">${stop_loss:.2f}</span></div>
                    <div>⚖️ 風險報酬比: <span class="risk-reward">1:{risk_reward_ratio:.1f}</span></div>
                    <div>📅 形成期間: {start_date} ~ {end_date}</div>
                    <div style="margin-top: 8px; padding: 6px; background: {'rgba(40,167,69,0.1)' if direction == 'bullish' else 'rgba(220,53,69,0.1)'}; border-radius: 4px; font-size: 12px;">
                        💡 <strong>交易計劃:</strong><br>
                        {'看漲' if direction == 'bullish' else '看跌'}形態，建議在 ${buy_point:.2f} 附近{'買入' if direction == 'bullish' else '做空'}
                    </div>
                </div>
            </div>
                        """
                    
                if signals:
                    analysis_html += "<h4>📡 交易訊號：</h4>"
                    for signal in signals[:3]:  # 顯示前3個
                        signal_type = signal.get('type', 'Unknown')
                        signal_icon = "🟢" if signal_type == "BUY" else "🔴" if signal_type == "SELL" else "🟡"
                        analysis_html += f"""
            <div class="signal-item">
                {signal_icon} <strong>{signal_type}</strong> - {signal.get('description', '')}
            </div>
                        """
                
                analysis_html += "</div>"
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{symbol} - AI交易分析平台</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: {'#ffffff' if theme == 'light' else '#1e222d'};
            font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;
            color: {'#2e2e2e' if theme == 'light' else '#d1d4dc'};
        }}
        .container {{
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 15px;
            padding: 15px;
            height: 100vh;
            box-sizing: border-box;
        }}
        .chart-container {{
            background: {'#f8f9fa' if theme == 'light' else '#2a2e39'};
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .right-panel {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        .analysis-section {{
            background: {'#f8f9fa' if theme == 'light' else '#2a2e39'};
            border-radius: 12px;
            padding: 20px;
            max-height: 40vh;
            overflow-y: auto;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .chat-section {{
            background: {'#f8f9fa' if theme == 'light' else '#2a2e39'};
            border-radius: 12px;
            padding: 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .pattern-item {{
            border: 1px solid {'#dee2e6' if theme == 'light' else '#3a3e49'};
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            background: {'#ffffff' if theme == 'light' else '#1e222d'};
        }}
        .pattern-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }}
        .pattern-number {{
            background: {'#007bff' if theme == 'light' else '#0d6efd'};
            color: white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }}
        .pattern-details {{
            font-size: 13px;
            line-height: 1.4;
        }}
        .pattern-details > div {{
            margin-bottom: 4px;
        }}
        .confidence {{
            font-weight: bold;
            color: {'#28a745' if theme == 'light' else '#20c997'};
        }}
        .target-price {{
            font-weight: bold;
            color: {'#007bff' if theme == 'light' else '#0dcaf0'};
        }}
        .current-price {{
            font-weight: bold;
            color: {'#6c757d' if theme == 'light' else '#adb5bd'};
        }}
        .buy-point {{
            font-weight: bold;
            color: {'#28a745' if theme == 'light' else '#20c997'};
        }}
        .stop-loss {{
            font-weight: bold;
            color: {'#dc3545' if theme == 'light' else '#fd7e7e'};
        }}
        .risk-reward {{
            font-weight: bold;
            color: {'#ffc107' if theme == 'light' else '#ffda6a'};
        }}
        .direction-bullish {{
            color: {'#28a745' if theme == 'light' else '#20c997'};
            font-weight: bold;
        }}
        .direction-bearish {{
            color: {'#dc3545' if theme == 'light' else '#fd7e7e'};
            font-weight: bold;
        }}
        .signal-item {{
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 8px;
            background: {'#e9ecef' if theme == 'light' else '#343a40'};
            font-size: 14px;
        }}
        .chat-messages {{
            flex: 1;
            overflow-y: auto;
            margin-bottom: 15px;
            padding: 10px;
            background: {'#ffffff' if theme == 'light' else '#1e222d'};
            border-radius: 8px;
            min-height: 200px;
            max-height: 300px;
        }}
        .chat-input-area {{
            display: flex;
            gap: 10px;
        }}
        .chat-input {{
            flex: 1;
            padding: 10px;
            border: 1px solid {'#ced4da' if theme == 'light' else '#495057'};
            border-radius: 6px;
            background: {'#ffffff' if theme == 'light' else '#343a40'};
            color: {'#495057' if theme == 'light' else '#f8f9fa'};
            font-size: 14px;
        }}
        .chat-send-btn {{
            padding: 10px 20px;
            background: {'#007bff' if theme == 'light' else '#0d6efd'};
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }}
        .chat-send-btn:hover {{
            background: {'#0056b3' if theme == 'light' else '#0b5ed7'};
        }}
        .message {{
            margin-bottom: 12px;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.4;
        }}
        .user-message {{
            background: {'#007bff' if theme == 'light' else '#0d6efd'};
            color: white;
            margin-left: 20px;
        }}
        .ai-message {{
            background: {'#e9ecef' if theme == 'light' else '#343a40'};
            color: {'#495057' if theme == 'light' else '#f8f9fa'};
            margin-right: 20px;
        }}
        .quick-questions {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }}
        .quick-question {{
            padding: 6px 12px;
            background: {'#6c757d' if theme == 'light' else '#495057'};
            color: white;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            font-size: 12px;
        }}
        .quick-question:hover {{
            background: {'#545b62' if theme == 'light' else '#6c757d'};
        }}
        @media (max-width: 768px) {{
            .container {{
                grid-template-columns: 1fr;
                height: auto;
            }}
            .right-panel {{
                order: -1;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="chart-container">
            <div id="tradingview_advanced_chart"></div>
        </div>
        <div class="right-panel">
            <div class="analysis-section">
                <h3>📊 {symbol} AI分析</h3>
                {analysis_html}
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid {'#dee2e6' if theme == 'light' else '#495057'};">
                    <div style="font-size: 13px; opacity: 0.8;">
                        💡 圖表支援所有TradingView功能<br>
                        🎯 形態標記顯示開始/買入/目標點<br>
                        📈 即時數據自動更新
                    </div>
                </div>
            </div>
            
            <div class="chat-section">
                <h3 style="margin-top: 0;">🤖 AI策略顧問</h3>
                <div class="quick-questions">
                    <button class="quick-question" onclick="askQuestion('這檔股票的趨勢如何？')">趨勢分析</button>
                    <button class="quick-question" onclick="askQuestion('建議的交易策略是什麼？')">交易策略</button>
                    <button class="quick-question" onclick="askQuestion('風險評估如何？')">風險評估</button>
                    <button class="quick-question" onclick="askQuestion('回測這個策略')">策略回測</button>
                </div>
                <div class="chat-messages" id="chat-messages">
                    <div class="ai-message">
                        🤖 您好！我是AI策略顧問。您可以問我關於 {symbol} 的任何問題：<br><br>
                        • 技術分析和形態解讀<br>
                        • 交易策略建議<br>
                        • 風險管理<br>
                        • 回測結果分析<br><br>
                        請直接輸入您的問題！
                    </div>
                </div>
                <div class="chat-input-area">
                    <input type="text" class="chat-input" id="chat-input" placeholder="詢問關於 {symbol} 的策略問題..." onkeypress="handleKeyPress(event)">
                    <button class="chat-send-btn" onclick="sendMessage()">發送</button>
                </div>
            </div>
        </div>
    </div>

    <!-- TradingView Widget BEGIN -->
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
        new TradingView.widget({{
            "width": "100%",
            "height": "100%",
            "symbol": "{symbol.upper()}",
            "interval": "D",
            "timezone": "Asia/Taipei",
            "theme": "{theme}",
            "style": "1",
            "locale": "zh_TW",
            "toolbar_bg": "{'#f1f3f6' if theme == 'light' else '#1e222d'}",
            "enable_publishing": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_advanced_chart",
            "autosize": true,
            "studies": ["RSI@tv-basicstudies", "MACD@tv-basicstudies", "BB@tv-basicstudies"]
        }});
        
        // AI聊天室功能
        let chatMessages = document.getElementById('chat-messages');
        let chatInput = document.getElementById('chat-input');
        
        function scrollToBottom() {{
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }}
        
        function addMessage(content, isUser = false) {{
            const messageDiv = document.createElement('div');
            messageDiv.className = isUser ? 'message user-message' : 'message ai-message';
            messageDiv.innerHTML = content;
            chatMessages.appendChild(messageDiv);
            scrollToBottom();
        }}
        
        function showTyping() {{
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message ai-message';
            typingDiv.id = 'typing-indicator';
            typingDiv.innerHTML = '🤖 AI正在思考中...';
            chatMessages.appendChild(typingDiv);
            scrollToBottom();
        }}
        
        function hideTyping() {{
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) {{
                typingIndicator.remove();
            }}
        }}
        
        async function sendMessage() {{
            const message = chatInput.value.trim();
            if (!message) return;
            
            // 顯示用戶消息
            addMessage(message, true);
            chatInput.value = '';
            
            // 顯示正在輸入指示器
            showTyping();
            
            try {{
                // 發送到AI端點
                const response = await fetch('/ai/discuss-strategy', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        symbol: '{symbol}',
                        period: '3mo',
                        user_question: message,
                        include_patterns: true
                    }})
                }});
                
                hideTyping();
                
                if (response.ok) {{
                    const data = await response.json();
                    let aiResponse = '🤖 ' + data.discussion_content;
                    
                    // 如果有建議，添加到回應中
                    if (data.recommendations && data.recommendations.length > 0) {{
                        aiResponse += '<br><br><strong>💡 建議：</strong><br>';
                        data.recommendations.forEach((rec, index) => {{
                            aiResponse += `${{index + 1}}. ${{rec}}<br>`;
                        }});
                    }}
                    
                    addMessage(aiResponse);
                }} else {{
                    addMessage('🤖 抱歉，AI服務暫時無法使用。請檢查API設定或稍後再試。');
                }}
            }} catch (error) {{
                hideTyping();
                addMessage('🤖 連接錯誤：' + error.message);
            }}
        }}
        
        function askQuestion(question) {{
            chatInput.value = question;
            sendMessage();
        }}
        
        function handleKeyPress(event) {{
            if (event.key === 'Enter') {{
                sendMessage();
            }}
        }}
        
        // 自動聚焦輸入框
        chatInput.focus();
    </script>
    <!-- TradingView Widget END -->
</body>
</html>
        """
        
        return html_template