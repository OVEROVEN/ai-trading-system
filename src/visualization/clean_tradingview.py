#!/usr/bin/env python3
"""
Clean TradingView implementation with isolated widget and working chatroom
Uses iframe to prevent JavaScript conflicts
"""

from typing import Dict, List, Any, Optional
import json

class CleanTradingViewChart:
    """Clean TradingView圖表與AI聊天室，解決JavaScript衝突"""
    
    def create_chart_with_chat(self, 
                              symbol: str,
                              analysis_data: Dict = None,
                              theme: str = "dark") -> str:
        """創建隔離的TradingView圖表與AI聊天室"""
        
        # 處理分析數據
        patterns_html = ""
        if analysis_data and analysis_data.get('patterns'):
            patterns = analysis_data['patterns']
            patterns_html = self._format_patterns(patterns, theme)
        
        # 主題顏色
        if theme == "dark":
            bg_color = "#1e222d"
            panel_bg = "#2a2e39"
            text_color = "#d1d4dc"
            input_bg = "#343a40"
            border_color = "#495057"
        else:
            bg_color = "#ffffff"
            panel_bg = "#f8f9fa"
            text_color = "#2e2e2e"
            input_bg = "#ffffff"
            border_color = "#ced4da"
        
        # 創建獨立的TradingView iframe HTML
        tradingview_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; padding: 0; background: {bg_color}; }}
    </style>
</head>
<body>
    <div id="tradingview_chart" style="width:100%;height:100%;"></div>
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
            "toolbar_bg": "{bg_color}",
            "enable_publishing": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_chart",
            "autosize": true,
            "studies": ["RSI@tv-basicstudies", "MACD@tv-basicstudies"],
            "hide_side_toolbar": false,
            "withdateranges": true,
            "hide_legend": false,
            "save_image": false
        }});
    </script>
</body>
</html>"""
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} - AI交易分析平台</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: {bg_color};
            color: {text_color};
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
            flex: 1;
            background: {panel_bg};
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            position: relative;
        }}
        
        .chart-iframe {{
            width: 100%;
            height: 100%;
            border: none;
            border-radius: 12px;
        }}
        
        .sidebar {{
            width: 400px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        .analysis-panel {{
            background: {panel_bg};
            border-radius: 12px;
            padding: 20px;
            max-height: 45vh;
            overflow-y: auto;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .chat-panel {{
            background: {panel_bg};
            border-radius: 12px;
            padding: 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            min-height: 400px;
        }}
        
        .panel-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
            color: {text_color};
        }}
        
        .pattern-item {{
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 12px;
            background: {bg_color};
            transition: transform 0.2s ease;
        }}
        
        .pattern-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        .pattern-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        
        .pattern-number {{
            background: #007bff;
            color: white;
            border-radius: 50%;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: bold;
        }}
        
        .pattern-name {{
            font-weight: 600;
            font-size: 16px;
        }}
        
        .pattern-direction {{
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .bullish {{
            background: rgba(40, 167, 69, 0.2);
            color: #28a745;
        }}
        
        .bearish {{
            background: rgba(220, 53, 69, 0.2);
            color: #dc3545;
        }}
        
        .pattern-details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            font-size: 14px;
        }}
        
        .detail-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .detail-label {{
            opacity: 0.8;
        }}
        
        .detail-value {{
            font-weight: 600;
        }}
        
        .price-current {{ color: #6c757d; }}
        .price-buy {{ color: #28a745; }}
        .price-target {{ color: #007bff; }}
        .price-stop {{ color: #dc3545; }}
        .risk-reward {{ color: #ffc107; }}
        
        .trading-plan {{
            margin-top: 12px;
            padding: 10px;
            background: rgba(0, 123, 255, 0.1);
            border-radius: 6px;
            font-size: 13px;
            line-height: 1.4;
        }}
        
        .chat-messages {{
            flex: 1;
            overflow-y: auto;
            margin-bottom: 15px;
            padding: 15px;
            background: {bg_color};
            border-radius: 8px;
            border: 1px solid {border_color};
            max-height: 300px;
        }}
        
        .message {{
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 12px;
            line-height: 1.5;
            font-size: 14px;
            word-wrap: break-word;
        }}
        
        .user-message {{
            background: #007bff;
            color: white;
            margin-left: 20px;
            border-bottom-right-radius: 4px;
        }}
        
        .ai-message {{
            background: {'rgba(52, 58, 64, 0.8)' if theme == 'dark' else 'rgba(233, 236, 239, 0.8)'};
            margin-right: 20px;
            border-bottom-left-radius: 4px;
        }}
        
        .quick-actions {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }}
        
        .quick-btn {{
            padding: 8px 12px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.2s ease;
        }}
        
        .quick-btn:hover {{
            background: #545b62;
        }}
        
        .chat-input-area {{
            display: flex;
            gap: 10px;
        }}
        
        .chat-input {{
            flex: 1;
            padding: 12px 16px;
            border: 1px solid {border_color};
            border-radius: 8px;
            background: {input_bg};
            color: {text_color};
            font-size: 14px;
            outline: none;
        }}
        
        .chat-input:focus {{
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }}
        
        .send-btn {{
            padding: 12px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: background 0.2s ease;
        }}
        
        .send-btn:hover {{
            background: #0056b3;
        }}
        
        .send-btn:disabled {{
            background: #6c757d;
            cursor: not-allowed;
        }}
        
        .status-indicator {{
            display: none;
            align-items: center;
            gap: 8px;
            color: #6c757d;
            font-style: italic;
            padding: 8px;
        }}
        
        .loading {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border: 2px solid #6c757d;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        
        .error-message {{
            color: #dc3545;
            background: rgba(220, 53, 69, 0.1);
            padding: 10px;
            border-radius: 6px;
            margin-top: 10px;
            font-size: 13px;
        }}
        
        @media (max-width: 1200px) {{
            .main-container {{
                flex-direction: column;
                height: auto;
                min-height: 100vh;
            }}
            
            .sidebar {{
                width: 100%;
                order: -1;
            }}
            
            .chart-container {{
                height: 60vh;
            }}
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="chart-container">
            <iframe class="chart-iframe" srcdoc='{tradingview_html.replace("'", "&#39;").replace('"', "&quot;")}'></iframe>
        </div>
        
        <div class="sidebar">
            <div class="analysis-panel">
                <div class="panel-title">
                    📊 {symbol} 形態分析
                </div>
                {patterns_html}
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid {border_color}; font-size: 13px; opacity: 0.7;">
                    💡 專業TradingView圖表<br>
                    🎯 詳細交易計劃與進出場點<br>
                    📈 即時數據與技術指標
                </div>
            </div>
            
            <div class="chat-panel">
                <div class="panel-title">
                    🤖 AI策略顧問
                </div>
                
                <div class="quick-actions">
                    <button class="quick-btn" onclick="askQuickQuestion('分析{symbol}的當前趨勢')">趨勢分析</button>
                    <button class="quick-btn" onclick="askQuickQuestion('推薦{symbol}的交易策略')">交易策略</button>
                    <button class="quick-btn" onclick="askQuickQuestion('評估{symbol}的投資風險')">風險評估</button>
                    <button class="quick-btn" onclick="askQuickQuestion('這個形態成功率如何')">成功率</button>
                </div>
                
                <div class="chat-messages" id="chatMessages">
                    <div class="message ai-message">
                        🤖 您好！我是AI交易顧問，專門分析 <strong>{symbol}</strong>。<br><br>
                        我可以幫您：<br>
                        • 解析當前技術形態<br>
                        • 制定交易策略<br>
                        • 評估風險與報酬<br>
                        • 優化進出場時機<br><br>
                        請使用上方快速按鈕或直接輸入問題！
                    </div>
                </div>
                
                <div class="status-indicator" id="statusIndicator">
                    <div class="loading"></div>
                    <span>AI思考中...</span>
                </div>
                
                <div class="chat-input-area">
                    <input 
                        type="text" 
                        class="chat-input" 
                        id="chatInput" 
                        placeholder="請輸入您關於{symbol}的問題..."
                        onkeypress="handleEnterKey(event)"
                        maxlength="500"
                    >
                    <button class="send-btn" id="sendBtn" onclick="sendMessage()">
                        發送
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 聊天室功能 - 完全獨立於TradingView
        const chatMessages = document.getElementById('chatMessages');
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');
        const statusIndicator = document.getElementById('statusIndicator');
        
        function scrollToBottom() {{
            setTimeout(() => {{
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }}, 100);
        }}
        
        function addMessage(content, isUser = false) {{
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{isUser ? 'user-message' : 'ai-message'}}`;
            messageDiv.innerHTML = content;
            chatMessages.appendChild(messageDiv);
            scrollToBottom();
        }}
        
        function showStatus() {{
            statusIndicator.style.display = 'flex';
        }}
        
        function hideStatus() {{
            statusIndicator.style.display = 'none';
        }}
        
        async function sendMessage() {{
            const message = chatInput.value.trim();
            if (!message || sendBtn.disabled) return;
            
            // 顯示用戶消息
            addMessage(message, true);
            chatInput.value = '';
            sendBtn.disabled = true;
            
            // 顯示狀態指示器
            showStatus();
            
            try {{
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
                
                hideStatus();
                
                if (response.ok) {{
                    const data = await response.json();
                    let aiResponse = '🤖 ' + data.discussion_content;
                    
                    if (data.recommendations && data.recommendations.length > 0) {{
                        aiResponse += '<br><br><strong>💡 建議：</strong><br>';
                        data.recommendations.forEach((rec, index) => {{
                            aiResponse += `${{index + 1}}. ${{rec}}<br>`;
                        }});
                    }}
                    
                    addMessage(aiResponse);
                }} else if (response.status === 503) {{
                    addMessage('🤖 AI服務暫時無法使用。<br><br>可能原因：<br>• OpenAI API未設定<br>• 網路連接問題<br><br>您仍可以使用TradingView圖表的所有分析功能。');
                }} else {{
                    addMessage('🤖 處理請求時發生問題，請稍後再試。');
                }}
            }} catch (error) {{
                hideStatus();
                console.error('聊天錯誤:', error);
                addMessage('🤖 連接失敗。請確認：<br>• API服務正在運行<br>• 網路連接正常<br>• 防火牆設定允許連接');
            }} finally {{
                sendBtn.disabled = false;
                chatInput.focus();
            }}
        }}
        
        function askQuickQuestion(question) {{
            chatInput.value = question;
            sendMessage();
        }}
        
        function handleEnterKey(event) {{
            if (event.key === 'Enter' && !sendBtn.disabled) {{
                sendMessage();
            }}
        }}
        
        // 自動聚焦
        window.addEventListener('load', () => {{
            setTimeout(() => {{
                chatInput.focus();
            }}, 500);
        }});
        
        // 防止頁面離開時的警告
        window.addEventListener('beforeunload', (e) => {{
            e.preventDefault();
            e.returnValue = '';
        }});
    </script>
</body>
</html>
        """
        
        return html_content
    
    def _format_patterns(self, patterns: List[Dict], theme: str) -> str:
        """格式化形態分析數據"""
        if not patterns:
            return "<div style='text-align: center; opacity: 0.6; padding: 20px;'>暫無檢測到明顯形態</div>"
        
        html = ""
        for i, pattern in enumerate(patterns[:3], 1):  # 只顯示前3個最重要的
            confidence = pattern.get('confidence', 0)
            direction = pattern.get('direction', 'Unknown')
            current_price = pattern.get('current_price', 0)
            buy_point = pattern.get('buy_point', 0)
            target_price = pattern.get('target_price', 0)
            stop_loss = pattern.get('stop_loss', 0)
            risk_reward = pattern.get('risk_reward_ratio', 0)
            
            direction_class = 'bullish' if direction == 'bullish' else 'bearish'
            direction_text = '看漲' if direction == 'bullish' else '看跌'
            profit_pct = ((target_price - current_price) / current_price * 100) if current_price > 0 else 0
            
            html += f"""
            <div class="pattern-item">
                <div class="pattern-header">
                    <div class="pattern-number">{i}</div>
                    <div class="pattern-name">{pattern.get('pattern_name', 'Unknown')}</div>
                    <div class="pattern-direction {direction_class}">{direction_text}</div>
                </div>
                <div class="pattern-details">
                    <div class="detail-item">
                        <span class="detail-label">信心度</span>
                        <span class="detail-value">{confidence:.1%}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">現價</span>
                        <span class="detail-value price-current">${current_price:.2f}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">買入點</span>
                        <span class="detail-value price-buy">${buy_point:.2f}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">目標價</span>
                        <span class="detail-value price-target">${target_price:.2f}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">停損</span>
                        <span class="detail-value price-stop">${stop_loss:.2f}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">風險報酬</span>
                        <span class="detail-value risk-reward">1:{risk_reward:.1f}</span>
                    </div>
                </div>
                <div class="trading-plan">
                    💡 <strong>交易計劃:</strong> {direction_text}形態，建議在 ${buy_point:.2f} 附近{'買入' if direction == 'bullish' else '做空'}，
                    目標 ${target_price:.2f} ({profit_pct:+.1f}%)，停損 ${stop_loss:.2f}
                </div>
            </div>
            """
        
        return html