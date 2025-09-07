#!/usr/bin/env python3
"""
簡單的 Web 介面 - 使用 Flask 創建更直觀的操作界面
"""

from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime, timedelta

app = Flask(__name__)
BASE_URL = "http://localhost:8000"

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>自動交易系統 - Web 介面</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .tabs { display: flex; margin-bottom: 20px; }
        .tab { padding: 10px 20px; background: #ddd; margin-right: 5px; cursor: pointer; border-radius: 5px 5px 0 0; }
        .tab.active { background: #007bff; color: white; }
        .tab-content { display: none; padding: 20px; border: 1px solid #ddd; border-radius: 0 5px 5px 5px; }
        .tab-content.active { display: block; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: inline-block; width: 120px; font-weight: bold; }
        .form-group select, .form-group input { padding: 8px; margin-left: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .result-area { background: #f8f9fa; padding: 15px; border-radius: 4px; max-height: 400px; overflow-y: auto; white-space: pre-wrap; font-family: monospace; font-size: 14px; }
        .loading { color: #007bff; font-style: italic; }
        .error { color: #dc3545; }
        .success { color: #28a745; }
        .grid { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; }
        .status { padding: 10px; margin-bottom: 10px; border-radius: 4px; }
        .status.connected { background: #d4edda; color: #155724; }
        .status.disconnected { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 自動交易系統</h1>
            <div id="status" class="status">正在檢查連接...</div>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="switchTab('patterns')">📊 形態分析</div>
            <div class="tab" onclick="switchTab('backtest')">📈 策略回測</div>
            <div class="tab" onclick="switchTab('ai')">🤖 AI 討論</div>
            <div class="tab" onclick="switchTab('compare')">⚖️ 策略比較</div>
        </div>

        <!-- 形態分析標籤頁 -->
        <div id="patterns" class="tab-content active">
            <h3>📊 形態分析</h3>
            <div class="grid">
                <div>
                    <div class="form-group">
                        <label>股票代號:</label>
                        <select id="patternSymbol">
                            <option value="AAPL">AAPL - Apple</option>
                            <option value="GOOGL">GOOGL - Google</option>
                            <option value="MSFT">MSFT - Microsoft</option>
                            <option value="AMZN">AMZN - Amazon</option>
                            <option value="TSLA">TSLA - Tesla</option>
                            <option value="META">META - Meta</option>
                            <option value="NVDA">NVDA - Nvidia</option>
                            <option value="SPY">SPY - S&P 500 ETF</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>分析期間:</label>
                        <select id="patternPeriod">
                            <option value="1mo">1個月</option>
                            <option value="3mo" selected>3個月</option>
                            <option value="6mo">6個月</option>
                        </select>
                    </div>
                    <button class="btn" onclick="analyzePatterns()">🔍 開始分析</button>
                </div>
                <div>
                    <div id="patternResult" class="result-area">點擊「開始分析」查看形態分析結果...</div>
                </div>
            </div>
        </div>

        <!-- 策略回測標籤頁 -->
        <div id="backtest" class="tab-content">
            <h3>📈 策略回測</h3>
            <div class="grid">
                <div>
                    <div class="form-group">
                        <label>股票代號:</label>
                        <select id="backtestSymbol">
                            <option value="AAPL">AAPL - Apple</option>
                            <option value="GOOGL">GOOGL - Google</option>
                            <option value="MSFT">MSFT - Microsoft</option>
                            <option value="AMZN">AMZN - Amazon</option>
                            <option value="TSLA">TSLA - Tesla</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>交易策略:</label>
                        <select id="backtestStrategy">
                            <option value="">載入中...</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>回測天數:</label>
                        <select id="backtestDays">
                            <option value="30">30天</option>
                            <option value="60">60天</option>
                            <option value="90" selected>90天</option>
                            <option value="180">180天</option>
                            <option value="365">365天</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>初始資金:</label>
                        <select id="backtestCapital">
                            <option value="50000">$50,000</option>
                            <option value="100000" selected>$100,000</option>
                            <option value="500000">$500,000</option>
                            <option value="1000000">$1,000,000</option>
                        </select>
                    </div>
                    <button class="btn" onclick="runBacktest()">🚀 開始回測</button>
                </div>
                <div>
                    <div id="backtestResult" class="result-area">選擇參數後點擊「開始回測」...</div>
                </div>
            </div>
        </div>

        <!-- AI 討論標籤頁 -->
        <div id="ai" class="tab-content">
            <h3>🤖 AI 討論</h3>
            <div class="grid">
                <div>
                    <div class="form-group">
                        <label>股票代號:</label>
                        <select id="aiSymbol">
                            <option value="AAPL">AAPL - Apple</option>
                            <option value="GOOGL">GOOGL - Google</option>
                            <option value="MSFT">MSFT - Microsoft</option>
                            <option value="TSLA">TSLA - Tesla</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>問題類型:</label>
                        <select id="aiQuestionType">
                            <option value="基於當前市況，建議使用什麼策略？">策略建議</option>
                            <option value="這檔股票適合長期投資嗎？">投資適性</option>
                            <option value="目前的技術指標顯示什麼訊號？">技術分析</option>
                            <option value="形態分析顯示什麼趨勢？">形態趨勢</option>
                            <option value="風險評估和建議停損點？">風險評估</option>
                        </select>
                    </div>
                    <button class="btn" onclick="askAI()">🧠 諮詢 AI</button>
                </div>
                <div>
                    <div id="aiResult" class="result-area">選擇股票和問題類型後點擊「諮詢 AI」...</div>
                </div>
            </div>
        </div>

        <!-- 策略比較標籤頁 -->
        <div id="compare" class="tab-content">
            <h3>⚖️ 策略比較</h3>
            <div class="grid">
                <div>
                    <div class="form-group">
                        <label>股票代號:</label>
                        <select id="compareSymbol">
                            <option value="AAPL">AAPL - Apple</option>
                            <option value="GOOGL">GOOGL - Google</option>
                            <option value="MSFT">MSFT - Microsoft</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>選擇策略:</label><br>
                        <div id="strategyCheckboxes" style="margin-top: 10px;">
                            載入中...
                        </div>
                    </div>
                    <button class="btn" onclick="compareStrategies()">📊 開始比較</button>
                </div>
                <div>
                    <div id="compareResult" class="result-area">選擇至少兩個策略進行比較...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 檢查 API 連接狀態
        async function checkConnection() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                const statusDiv = document.getElementById('status');
                if (data.status === 'healthy') {
                    statusDiv.className = 'status connected';
                    statusDiv.textContent = '✅ 系統連接正常';
                } else {
                    throw new Error('API 未就緒');
                }
            } catch (error) {
                const statusDiv = document.getElementById('status');
                statusDiv.className = 'status disconnected';
                statusDiv.textContent = '❌ 無法連接到交易系統 API';
            }
        }

        // 載入可用策略
        async function loadStrategies() {
            try {
                const response = await fetch('/api/strategies');
                const data = await response.json();
                
                // 更新回測策略下拉選單
                const backtestSelect = document.getElementById('backtestStrategy');
                backtestSelect.innerHTML = '';
                data.strategies.forEach(strategy => {
                    const option = document.createElement('option');
                    option.value = strategy;
                    option.textContent = data.details[strategy]?.name || strategy;
                    backtestSelect.appendChild(option);
                });

                // 更新比較頁面的核取方塊
                const checkboxDiv = document.getElementById('strategyCheckboxes');
                checkboxDiv.innerHTML = '';
                data.strategies.forEach(strategy => {
                    const label = document.createElement('label');
                    label.style.display = 'block';
                    label.style.marginBottom = '5px';
                    label.innerHTML = `
                        <input type="checkbox" value="${strategy}" style="margin-right: 8px;">
                        ${data.details[strategy]?.name || strategy}
                    `;
                    checkboxDiv.appendChild(label);
                });
            } catch (error) {
                console.error('載入策略失敗:', error);
            }
        }

        // 切換標籤頁
        function switchTab(tabName) {
            // 隱藏所有標籤內容
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });

            // 顯示選中的標籤
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

        // 形態分析
        async function analyzePatterns() {
            const symbol = document.getElementById('patternSymbol').value;
            const period = document.getElementById('patternPeriod').value;
            const resultDiv = document.getElementById('patternResult');

            resultDiv.textContent = `正在分析 ${symbol} 的形態...`;
            resultDiv.className = 'result-area loading';

            try {
                const response = await fetch('/api/patterns', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol, period })
                });

                const data = await response.json();
                if (response.ok) {
                    resultDiv.className = 'result-area success';
                    resultDiv.textContent = data.result;
                } else {
                    resultDiv.className = 'result-area error';
                    resultDiv.textContent = `分析失敗: ${data.error}`;
                }
            } catch (error) {
                resultDiv.className = 'result-area error';
                resultDiv.textContent = `連接錯誤: ${error.message}`;
            }
        }

        // 策略回測
        async function runBacktest() {
            const symbol = document.getElementById('backtestSymbol').value;
            const strategy = document.getElementById('backtestStrategy').value;
            const days = document.getElementById('backtestDays').value;
            const capital = document.getElementById('backtestCapital').value;
            const resultDiv = document.getElementById('backtestResult');

            if (!strategy) {
                alert('請選擇交易策略');
                return;
            }

            resultDiv.textContent = `正在回測 ${symbol} (${strategy})...`;
            resultDiv.className = 'result-area loading';

            try {
                const response = await fetch('/api/backtest', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol, strategy, days: parseInt(days), capital: parseFloat(capital) })
                });

                const data = await response.json();
                if (response.ok) {
                    resultDiv.className = 'result-area success';
                    resultDiv.textContent = data.result;
                } else {
                    resultDiv.className = 'result-area error';
                    resultDiv.textContent = `回測失敗: ${data.error}`;
                }
            } catch (error) {
                resultDiv.className = 'result-area error';
                resultDiv.textContent = `連接錯誤: ${error.message}`;
            }
        }

        // AI 討論
        async function askAI() {
            const symbol = document.getElementById('aiSymbol').value;
            const question = document.getElementById('aiQuestionType').value;
            const resultDiv = document.getElementById('aiResult');

            resultDiv.textContent = `🤖 AI 正在分析 ${symbol}...`;
            resultDiv.className = 'result-area loading';

            try {
                const response = await fetch('/api/ai-discuss', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol, question })
                });

                const data = await response.json();
                if (response.ok) {
                    resultDiv.className = 'result-area success';
                    resultDiv.textContent = data.result;
                } else {
                    resultDiv.className = 'result-area error';
                    resultDiv.textContent = `AI 討論失敗: ${data.error}`;
                }
            } catch (error) {
                resultDiv.className = 'result-area error';
                resultDiv.textContent = `連接錯誤: ${error.message}`;
            }
        }

        // 策略比較
        async function compareStrategies() {
            const symbol = document.getElementById('compareSymbol').value;
            const checkboxes = document.querySelectorAll('#strategyCheckboxes input[type="checkbox"]:checked');
            const strategies = Array.from(checkboxes).map(cb => cb.value);
            const resultDiv = document.getElementById('compareResult');

            if (strategies.length < 2) {
                alert('請至少選擇兩個策略進行比較');
                return;
            }

            resultDiv.textContent = `正在比較 ${symbol} 的策略表現...`;
            resultDiv.className = 'result-area loading';

            try {
                const response = await fetch('/api/compare', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ symbol, strategies })
                });

                const data = await response.json();
                if (response.ok) {
                    resultDiv.className = 'result-area success';
                    resultDiv.textContent = data.result;
                } else {
                    resultDiv.className = 'result-area error';
                    resultDiv.textContent = `比較失敗: ${data.error}`;
                }
            } catch (error) {
                resultDiv.className = 'result-area error';
                resultDiv.textContent = `連接錯誤: ${error.message}`;
            }
        }

        // 頁面載入時執行
        window.addEventListener('load', () => {
            checkConnection();
            loadStrategies();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """主頁面"""
    return HTML_TEMPLATE

@app.route('/api/health')
def api_health():
    """檢查 API 健康狀態"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        if response.status_code == 200:
            return jsonify({"status": "healthy"})
        else:
            return jsonify({"status": "error"}), 500
    except:
        return jsonify({"status": "error"}), 500

@app.route('/api/strategies')
def api_strategies():
    """獲取可用策略"""
    try:
        response = requests.get(f"{BASE_URL}/backtest/strategies")
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "strategies": data['available_strategies'],
                "details": data['strategy_details']
            })
        else:
            return jsonify({"error": "無法獲取策略"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/patterns', methods=['POST'])
def api_patterns():
    """形態分析"""
    try:
        data = request.json
        symbol = data['symbol']
        period = data['period']
        
        response = requests.post(f"{BASE_URL}/patterns/advanced/{symbol}?period={period}")
        
        if response.status_code == 200:
            result_data = response.json()
            
            # 格式化結果
            result_text = f"📊 {symbol} 形態分析結果 ({period})\\n"
            result_text += "="*50 + "\\n\\n"
            
            summary = result_data['pattern_summary']
            result_text += f"📈 摘要統計:\\n"
            result_text += f"   總形態數: {summary['total_patterns']}\\n"
            result_text += f"   高信心度形態: {summary['high_confidence_patterns']}\\n"
            result_text += f"   看漲形態: {summary['bullish_patterns']}\\n"
            result_text += f"   看跌形態: {summary['bearish_patterns']}\\n\\n"
            
            # 顯示檢測到的形態
            patterns = result_data['advanced_patterns']
            for pattern_type, pattern_list in patterns.items():
                if pattern_list:
                    result_text += f"🎯 {pattern_type.upper()}:\\n"
                    for i, pattern in enumerate(pattern_list[:3], 1):
                        result_text += f"   {i}. {pattern['pattern_name']} ({pattern['direction']})\\n"
                        result_text += f"      信心度: {pattern['confidence']:.2f}\\n"
                        result_text += f"      目標價: ${pattern['target_price']:.2f}\\n\\n"
            
            # 顯示交易訊號
            signals = result_data['trading_signals']
            if signals:
                result_text += f"📡 交易訊號 ({len(signals)} 個):\\n"
                for signal in signals:
                    result_text += f"   {signal['type']}: {signal['description']}\\n"
            
            return jsonify({"result": result_text})
        else:
            return jsonify({"error": "分析失敗"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/backtest', methods=['POST'])
def api_backtest():
    """策略回測"""
    try:
        data = request.json
        symbol = data['symbol']
        strategy = data['strategy']
        days = data['days']
        capital = data['capital']
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        request_data = {
            "symbol": symbol,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "strategy_name": strategy,
            "strategy_params": {},
            "initial_capital": capital
        }
        
        if "pattern" in strategy:
            request_data["strategy_params"] = {
                "pattern_confidence_threshold": 0.6,
                "risk_reward_ratio": 2.0
            }
        
        response = requests.post(f"{BASE_URL}/backtest", json=request_data)
        
        if response.status_code == 200:
            result_data = response.json()
            
            # 格式化結果
            result_text = f"📈 {symbol} 回測結果\\n"
            result_text += "="*50 + "\\n\\n"
            
            result_text += f"🎯 基本資訊:\\n"
            result_text += f"   股票: {symbol}\\n"
            result_text += f"   策略: {strategy}\\n"
            result_text += f"   期間: {days} 天\\n"
            result_text += f"   初始資金: ${capital:,.0f}\\n\\n"
            
            perf = result_data['performance_metrics']
            result_text += f"📊 績效指標:\\n"
            result_text += f"   總報酬率: {perf['total_return_pct']:.2f}%\\n"
            result_text += f"   夏普比率: {perf['sharpe_ratio']:.2f}\\n"
            result_text += f"   最大回撤: {perf['max_drawdown_pct']:.2f}%\\n"
            result_text += f"   波動率: {perf['volatility']:.2f}%\\n\\n"
            
            trades = result_data['trade_statistics']
            result_text += f"📈 交易統計:\\n"
            result_text += f"   總交易次數: {trades['total_trades']}\\n"
            result_text += f"   勝率: {trades['win_rate']:.1f}%\\n"
            result_text += f"   獲利因子: {trades['profit_factor']:.2f}\\n\\n"
            
            final_value = capital + perf['total_return']
            result_text += f"💰 最終結果:\\n"
            result_text += f"   最終資金: ${final_value:,.0f}\\n"
            result_text += f"   總獲利: ${perf['total_return']:,.0f}"
            
            return jsonify({"result": result_text})
        else:
            return jsonify({"error": "回測失敗"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai-discuss', methods=['POST'])
def api_ai_discuss():
    """AI 策略討論"""
    try:
        data = request.json
        symbol = data['symbol']
        question = data['question']
        
        request_data = {
            "symbol": symbol,
            "period": "3mo",
            "current_strategy": "pattern_trading",
            "user_question": question,
            "include_patterns": True
        }
        
        response = requests.post(f"{BASE_URL}/ai/discuss-strategy", json=request_data)
        
        if response.status_code == 200:
            result_data = response.json()
            
            result_text = f"🤖 AI 策略分析 - {symbol}\\n"
            result_text += "="*50 + "\\n\\n"
            
            result_text += f"❓ 您的問題:\\n{question}\\n\\n"
            
            market = result_data['market_summary']
            result_text += f"📊 市場摘要:\\n"
            result_text += f"   當前價格: ${market['current_price']:.2f}\\n"
            result_text += f"   檢測形態: {market['patterns_detected']} 個\\n\\n"
            
            ai_analysis = result_data['ai_discussion']
            result_text += f"🧠 AI 分析:\\n"
            result_text += f"   建議策略: {ai_analysis['strategy_name']}\\n"
            result_text += f"   信心評分: {ai_analysis['confidence_score']:.1f}/10\\n\\n"
            
            result_text += f"📈 市場分析:\\n{ai_analysis['market_analysis']}\\n\\n"
            result_text += f"💡 策略建議:\\n{ai_analysis['strategy_recommendation']}"
            
            return jsonify({"result": result_text})
        elif response.status_code == 503:
            return jsonify({"error": "AI 服務不可用，需要設定 OpenAI API Key"}), 503
        else:
            return jsonify({"error": "AI 討論失敗"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def api_compare():
    """策略比較"""
    try:
        data = request.json
        symbol = data['symbol']
        strategies = data['strategies']
        
        results = {}
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        for strategy in strategies:
            request_data = {
                "symbol": symbol,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "strategy_name": strategy,
                "strategy_params": {},
                "initial_capital": 100000
            }
            
            if "pattern" in strategy:
                request_data["strategy_params"] = {
                    "pattern_confidence_threshold": 0.6,
                    "risk_reward_ratio": 2.0
                }
            
            response = requests.post(f"{BASE_URL}/backtest", json=request_data)
            if response.status_code == 200:
                results[strategy] = response.json()
        
        # 格式化比較結果
        result_text = f"⚖️ {symbol} 策略比較結果\\n"
        result_text += "="*60 + "\\n\\n"
        
        # 表格標題
        result_text += f"{'策略名稱':<20} {'報酬率':<10} {'夏普比率':<10} {'最大回撤':<10} {'勝率':<8}\\n"
        result_text += "-"*60 + "\\n"
        
        # 每個策略的結果
        for strategy, strategy_data in results.items():
            perf = strategy_data['performance_metrics']
            trades = strategy_data['trade_statistics']
            
            result_text += f"{strategy:<20} "
            result_text += f"{perf['total_return_pct']:>8.2f}% "
            result_text += f"{perf['sharpe_ratio']:>9.2f} "
            result_text += f"{perf['max_drawdown_pct']:>8.2f}% "
            result_text += f"{trades['win_rate']:>6.1f}%\\n"
        
        # 找出最佳策略
        if results:
            best_return = max(results.keys(), 
                            key=lambda k: results[k]['performance_metrics']['total_return_pct'])
            best_sharpe = max(results.keys(), 
                            key=lambda k: results[k]['performance_metrics']['sharpe_ratio'])
            
            result_text += "\\n🏆 最佳表現:\\n"
            result_text += f"   最高報酬: {best_return} "
            result_text += f"({results[best_return]['performance_metrics']['total_return_pct']:.2f}%)\\n"
            result_text += f"   最佳夏普: {best_sharpe} "
            result_text += f"({results[best_sharpe]['performance_metrics']['sharpe_ratio']:.2f})"
        
        return jsonify({"result": result_text})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("啟動 Web 介面...")
    print("請在瀏覽器中打開: http://localhost:5000")
    print("確保交易系統 API 在 http://localhost:8000 運行中")
    app.run(host='0.0.0.0', port=5000, debug=True)