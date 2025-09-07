#!/usr/bin/env python3
"""
圖形化交易系統介面 - 使用 tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
from datetime import datetime, timedelta
import threading

BASE_URL = "http://localhost:8000"

class TradingSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("自動交易系統 - 圖形化介面")
        self.root.geometry("1000x700")
        
        # 檢查 API 連接
        self.check_api_connection()
        
        # 創建介面
        self.create_widgets()
        
        # 載入初始數據
        self.load_strategies()
        self.load_symbols()
    
    def check_api_connection(self):
        """檢查 API 連接"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=3)
            if response.status_code == 200:
                return True
        except:
            messagebox.showerror("連接錯誤", 
                               "無法連接到交易系統！\n\n請確保 API 伺服器運行中:\n"
                               "python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
            return False
    
    def create_widgets(self):
        """創建 GUI 元件"""
        
        # 主要筆記本標籤頁
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 標籤頁 1: 形態分析
        self.create_pattern_analysis_tab(notebook)
        
        # 標籤頁 2: 策略回測
        self.create_backtest_tab(notebook)
        
        # 標籤頁 3: AI 討論
        self.create_ai_tab(notebook)
        
        # 標籤頁 4: 策略比較
        self.create_comparison_tab(notebook)
    
    def create_pattern_analysis_tab(self, notebook):
        """創建形態分析標籤頁"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📊 形態分析")
        
        # 上半部：設定區域
        settings_frame = ttk.LabelFrame(frame, text="分析設定", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 股票選擇
        ttk.Label(settings_frame, text="股票代號:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.symbol_var = tk.StringVar(value="AAPL")
        self.symbol_combo = ttk.Combobox(settings_frame, textvariable=self.symbol_var, width=15)
        self.symbol_combo.grid(row=0, column=1, padx=5)
        
        # 分析期間
        ttk.Label(settings_frame, text="分析期間:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.period_var = tk.StringVar(value="3mo")
        period_combo = ttk.Combobox(settings_frame, textvariable=self.period_var, 
                                   values=["1mo", "3mo", "6mo"], width=10, state="readonly")
        period_combo.grid(row=0, column=3, padx=5)
        
        # 分析按鈕
        analyze_btn = ttk.Button(settings_frame, text="🔍 開始分析", 
                                command=self.analyze_patterns)
        analyze_btn.grid(row=0, column=4, padx=10)
        
        # 下半部：結果顯示
        results_frame = ttk.LabelFrame(frame, text="分析結果", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 結果文字區域
        self.pattern_result = scrolledtext.ScrolledText(results_frame, height=20)
        self.pattern_result.pack(fill=tk.BOTH, expand=True)
    
    def create_backtest_tab(self, notebook):
        """創建回測標籤頁"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📈 策略回測")
        
        # 設定區域
        settings_frame = ttk.LabelFrame(frame, text="回測設定", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 第一行：股票和策略
        ttk.Label(settings_frame, text="股票代號:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.backtest_symbol_var = tk.StringVar(value="AAPL")
        backtest_symbol_combo = ttk.Combobox(settings_frame, textvariable=self.backtest_symbol_var, width=15)
        backtest_symbol_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(settings_frame, text="交易策略:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.strategy_var = tk.StringVar()
        self.strategy_combo = ttk.Combobox(settings_frame, textvariable=self.strategy_var, 
                                          width=20, state="readonly")
        self.strategy_combo.grid(row=0, column=3, padx=5)
        
        # 第二行：時間設定
        ttk.Label(settings_frame, text="回測天數:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.days_var = tk.StringVar(value="90")
        days_combo = ttk.Combobox(settings_frame, textvariable=self.days_var,
                                 values=["30", "60", "90", "180", "365"], width=10, state="readonly")
        days_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(settings_frame, text="初始資金:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.capital_var = tk.StringVar(value="100000")
        capital_combo = ttk.Combobox(settings_frame, textvariable=self.capital_var,
                                    values=["50000", "100000", "500000", "1000000"], width=15, state="readonly")
        capital_combo.grid(row=1, column=3, padx=5, pady=5)
        
        # 回測按鈕
        backtest_btn = ttk.Button(settings_frame, text="🚀 開始回測", 
                                 command=self.run_backtest)
        backtest_btn.grid(row=0, column=4, rowspan=2, padx=10)
        
        # 結果顯示
        results_frame = ttk.LabelFrame(frame, text="回測結果", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.backtest_result = scrolledtext.ScrolledText(results_frame, height=18)
        self.backtest_result.pack(fill=tk.BOTH, expand=True)
    
    def create_ai_tab(self, notebook):
        """創建 AI 討論標籤頁"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🤖 AI 討論")
        
        # 設定區域
        settings_frame = ttk.LabelFrame(frame, text="AI 諮詢設定", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 第一行：股票選擇
        ttk.Label(settings_frame, text="股票代號:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.ai_symbol_var = tk.StringVar(value="AAPL")
        ai_symbol_combo = ttk.Combobox(settings_frame, textvariable=self.ai_symbol_var, width=15)
        ai_symbol_combo.grid(row=0, column=1, padx=5)
        
        # 問題類型選擇
        ttk.Label(settings_frame, text="問題類型:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.question_type_var = tk.StringVar()
        question_combo = ttk.Combobox(settings_frame, textvariable=self.question_type_var,
                                     values=[
                                         "基於當前市況，建議使用什麼策略？",
                                         "這檔股票適合長期投資嗎？",
                                         "目前的技術指標顯示什麼訊號？",
                                         "形態分析顯示什麼趨勢？",
                                         "風險評估和建議停損點？",
                                         "自訂問題"
                                     ], width=40, state="readonly")
        question_combo.grid(row=0, column=3, padx=5)
        question_combo.set("基於當前市況，建議使用什麼策略？")
        
        # 自訂問題輸入
        ttk.Label(settings_frame, text="自訂問題:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.custom_question = tk.Text(settings_frame, height=3, width=60)
        self.custom_question.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        
        # AI 討論按鈕
        ai_btn = ttk.Button(settings_frame, text="🧠 諮詢 AI", 
                           command=self.ai_discussion)
        ai_btn.grid(row=1, column=3, padx=10, pady=5)
        
        # AI 回應顯示
        ai_frame = ttk.LabelFrame(frame, text="AI 回應", padding=10)
        ai_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.ai_result = scrolledtext.ScrolledText(ai_frame, height=18)
        self.ai_result.pack(fill=tk.BOTH, expand=True)
    
    def create_comparison_tab(self, notebook):
        """創建策略比較標籤頁"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="⚖️ 策略比較")
        
        # 設定區域
        settings_frame = ttk.LabelFrame(frame, text="比較設定", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 股票選擇
        ttk.Label(settings_frame, text="股票代號:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.comp_symbol_var = tk.StringVar(value="AAPL")
        comp_symbol_combo = ttk.Combobox(settings_frame, textvariable=self.comp_symbol_var, width=15)
        comp_symbol_combo.grid(row=0, column=1, padx=5)
        
        # 策略選擇（多選）
        ttk.Label(settings_frame, text="選擇策略:").grid(row=1, column=0, sticky=tk.NW, padx=5, pady=5)
        
        self.strategy_vars = {}
        strategies_frame = ttk.Frame(settings_frame)
        strategies_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # 比較按鈕
        compare_btn = ttk.Button(settings_frame, text="📊 開始比較", 
                                command=self.compare_strategies)
        compare_btn.grid(row=0, column=2, padx=10)
        
        # 結果顯示
        results_frame = ttk.LabelFrame(frame, text="比較結果", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.comparison_result = scrolledtext.ScrolledText(results_frame, height=18)
        self.comparison_result.pack(fill=tk.BOTH, expand=True)
    
    def load_strategies(self):
        """載入可用策略"""
        try:
            response = requests.get(f"{BASE_URL}/backtest/strategies")
            if response.status_code == 200:
                data = response.json()
                strategies = data['available_strategies']
                
                # 更新策略下拉選單
                self.strategy_combo['values'] = strategies
                if strategies:
                    self.strategy_combo.set(strategies[0])
                
                # 更新比較頁面的策略核取方塊
                self.update_strategy_checkboxes(strategies)
                
        except Exception as e:
            messagebox.showerror("錯誤", f"無法載入策略列表: {str(e)}")
    
    def update_strategy_checkboxes(self, strategies):
        """更新策略比較的核取方塊"""
        # 清除現有的核取方塊
        for widget in self.root.nametowidget("!notebook.!frame4.!labelframe.!frame").winfo_children():
            widget.destroy()
        
        strategies_frame = self.root.nametowidget("!notebook.!frame4.!labelframe.!frame")
        
        self.strategy_vars = {}
        for i, strategy in enumerate(strategies):
            var = tk.BooleanVar()
            self.strategy_vars[strategy] = var
            cb = ttk.Checkbutton(strategies_frame, text=strategy, variable=var)
            cb.grid(row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2)
    
    def load_symbols(self):
        """載入常用股票代號"""
        # 常用美股代號
        common_symbols = [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", 
            "META", "NVDA", "NFLX", "BABA", "AMD",
            "SPY", "QQQ", "IWM", "GLD", "TLT"
        ]
        
        # 更新所有股票代號下拉選單
        self.symbol_combo['values'] = common_symbols
        
        # 同步到其他標籤頁
        for combo_var, combo_widget in [
            (self.backtest_symbol_var, None),
            (self.ai_symbol_var, None),
            (self.comp_symbol_var, None)
        ]:
            try:
                # 找到對應的 combobox 並更新
                pass  # 簡化版本，直接在創建時設定
            except:
                pass
    
    def analyze_patterns(self):
        """執行形態分析"""
        symbol = self.symbol_var.get().upper()
        period = self.period_var.get()
        
        if not symbol:
            messagebox.showwarning("警告", "請輸入股票代號")
            return
        
        self.pattern_result.delete(1.0, tk.END)
        self.pattern_result.insert(tk.END, f"正在分析 {symbol} 的形態...\n\n")
        self.root.update()
        
        def analyze():
            try:
                response = requests.post(f"{BASE_URL}/patterns/advanced/{symbol}?period={period}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 格式化結果
                    result_text = f"📊 {symbol} 形態分析結果 ({period})\n"
                    result_text += "="*50 + "\n\n"
                    
                    summary = data['pattern_summary']
                    result_text += f"📈 摘要統計:\n"
                    result_text += f"   總形態數: {summary['total_patterns']}\n"
                    result_text += f"   高信心度形態: {summary['high_confidence_patterns']}\n"
                    result_text += f"   看漲形態: {summary['bullish_patterns']}\n"
                    result_text += f"   看跌形態: {summary['bearish_patterns']}\n\n"
                    
                    # 顯示檢測到的形態
                    patterns = data['advanced_patterns']
                    for pattern_type, pattern_list in patterns.items():
                        if pattern_list:
                            result_text += f"🎯 {pattern_type.upper()}:\n"
                            for i, pattern in enumerate(pattern_list[:3], 1):
                                result_text += f"   {i}. {pattern['pattern_name']} ({pattern['direction']})\n"
                                result_text += f"      信心度: {pattern['confidence']:.2f}\n"
                                result_text += f"      目標價: ${pattern['target_price']:.2f}\n"
                                result_text += f"      停損: ${pattern['stop_loss']:.2f}\n\n"
                    
                    # 顯示交易訊號
                    signals = data['trading_signals']
                    if signals:
                        result_text += f"📡 交易訊號 ({len(signals)} 個):\n"
                        for signal in signals:
                            result_text += f"   {signal['type']}: {signal['description']}\n"
                            result_text += f"   信心度: {signal['confidence']:.2f}\n\n"
                    
                    # 更新 GUI
                    self.pattern_result.delete(1.0, tk.END)
                    self.pattern_result.insert(tk.END, result_text)
                    
                else:
                    error_msg = f"分析失敗 (HTTP {response.status_code})\n"
                    if response.status_code == 404:
                        error_msg += "找不到該股票數據，請檢查股票代號是否正確"
                    self.pattern_result.delete(1.0, tk.END)
                    self.pattern_result.insert(tk.END, error_msg)
                    
            except Exception as e:
                error_msg = f"連接錯誤: {str(e)}\n請確保 API 伺服器運行中"
                self.pattern_result.delete(1.0, tk.END)
                self.pattern_result.insert(tk.END, error_msg)
        
        # 在背景執行分析
        threading.Thread(target=analyze, daemon=True).start()
    
    def run_backtest(self):
        """執行策略回測"""
        symbol = self.backtest_symbol_var.get().upper()
        strategy = self.strategy_var.get()
        days = int(self.days_var.get())
        capital = float(self.capital_var.get())
        
        if not symbol or not strategy:
            messagebox.showwarning("警告", "請選擇股票代號和策略")
            return
        
        self.backtest_result.delete(1.0, tk.END)
        self.backtest_result.insert(tk.END, f"正在回測 {symbol} ({strategy})...\n\n")
        self.root.update()
        
        def backtest():
            try:
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
                
                # 為形態策略設定參數
                if "pattern" in strategy:
                    request_data["strategy_params"] = {
                        "pattern_confidence_threshold": 0.6,
                        "risk_reward_ratio": 2.0
                    }
                
                response = requests.post(f"{BASE_URL}/backtest", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 格式化結果
                    result_text = f"📈 {symbol} 回測結果\n"
                    result_text += "="*50 + "\n\n"
                    
                    result_text += f"🎯 基本資訊:\n"
                    result_text += f"   股票: {symbol}\n"
                    result_text += f"   策略: {strategy}\n"
                    result_text += f"   期間: {days} 天\n"
                    result_text += f"   初始資金: ${capital:,.0f}\n\n"
                    
                    perf = data['performance_metrics']
                    result_text += f"📊 績效指標:\n"
                    result_text += f"   總報酬率: {perf['total_return_pct']:.2f}%\n"
                    result_text += f"   夏普比率: {perf['sharpe_ratio']:.2f}\n"
                    result_text += f"   最大回撤: {perf['max_drawdown_pct']:.2f}%\n"
                    result_text += f"   波動率: {perf['volatility']:.2f}%\n\n"
                    
                    trades = data['trade_statistics']
                    result_text += f"📈 交易統計:\n"
                    result_text += f"   總交易次數: {trades['total_trades']}\n"
                    result_text += f"   勝率: {trades['win_rate']:.1f}%\n"
                    result_text += f"   獲利因子: {trades['profit_factor']:.2f}\n"
                    result_text += f"   平均獲利: ${trades['avg_profit']:.2f}\n"
                    result_text += f"   平均虧損: ${trades['avg_loss']:.2f}\n\n"
                    
                    # 顯示最終資金
                    final_value = capital + perf['total_return']
                    result_text += f"💰 最終結果:\n"
                    result_text += f"   最終資金: ${final_value:,.0f}\n"
                    result_text += f"   總獲利: ${perf['total_return']:,.0f}\n"
                    
                    self.backtest_result.delete(1.0, tk.END)
                    self.backtest_result.insert(tk.END, result_text)
                    
                else:
                    error_msg = f"回測失敗 (HTTP {response.status_code})"
                    self.backtest_result.delete(1.0, tk.END)
                    self.backtest_result.insert(tk.END, error_msg)
                    
            except Exception as e:
                error_msg = f"回測錯誤: {str(e)}"
                self.backtest_result.delete(1.0, tk.END)
                self.backtest_result.insert(tk.END, error_msg)
        
        threading.Thread(target=backtest, daemon=True).start()
    
    def ai_discussion(self):
        """AI 策略討論"""
        symbol = self.ai_symbol_var.get().upper()
        question_type = self.question_type_var.get()
        
        if not symbol:
            messagebox.showwarning("警告", "請輸入股票代號")
            return
        
        # 決定使用的問題
        if question_type == "自訂問題":
            question = self.custom_question.get(1.0, tk.END).strip()
            if not question:
                messagebox.showwarning("警告", "請輸入自訂問題")
                return
        else:
            question = question_type
        
        self.ai_result.delete(1.0, tk.END)
        self.ai_result.insert(tk.END, f"🤖 AI 正在分析 {symbol}...\n\n")
        self.root.update()
        
        def ai_analyze():
            try:
                request_data = {
                    "symbol": symbol,
                    "period": "3mo",
                    "current_strategy": "pattern_trading",
                    "user_question": question,
                    "include_patterns": True
                }
                
                response = requests.post(f"{BASE_URL}/ai/discuss-strategy", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    result_text = f"🤖 AI 策略分析 - {symbol}\n"
                    result_text += "="*50 + "\n\n"
                    
                    result_text += f"❓ 您的問題:\n{question}\n\n"
                    
                    market = data['market_summary']
                    result_text += f"📊 市場摘要:\n"
                    result_text += f"   當前價格: ${market['current_price']:.2f}\n"
                    result_text += f"   檢測形態: {market['patterns_detected']} 個\n\n"
                    
                    ai_analysis = data['ai_discussion']
                    result_text += f"🧠 AI 分析:\n"
                    result_text += f"   建議策略: {ai_analysis['strategy_name']}\n"
                    result_text += f"   信心評分: {ai_analysis['confidence_score']:.1f}/10\n\n"
                    
                    result_text += f"📈 市場分析:\n{ai_analysis['market_analysis']}\n\n"
                    result_text += f"💡 策略建議:\n{ai_analysis['strategy_recommendation']}\n\n"
                    result_text += f"⚠️ 風險評估:\n{ai_analysis['risk_assessment']}\n\n"
                    
                    if ai_analysis['optimization_suggestions']:
                        result_text += f"🔧 優化建議:\n"
                        for suggestion in ai_analysis['optimization_suggestions']:
                            result_text += f"   • {suggestion}\n"
                    
                    self.ai_result.delete(1.0, tk.END)
                    self.ai_result.insert(tk.END, result_text)
                    
                elif response.status_code == 503:
                    error_msg = "AI 服務不可用\n\n需要設定 OpenAI API Key 才能使用 AI 功能"
                    self.ai_result.delete(1.0, tk.END)
                    self.ai_result.insert(tk.END, error_msg)
                else:
                    error_msg = f"AI 討論失敗 (HTTP {response.status_code})"
                    self.ai_result.delete(1.0, tk.END)
                    self.ai_result.insert(tk.END, error_msg)
                    
            except Exception as e:
                error_msg = f"AI 討論錯誤: {str(e)}"
                self.ai_result.delete(1.0, tk.END)
                self.ai_result.insert(tk.END, error_msg)
        
        threading.Thread(target=ai_analyze, daemon=True).start()
    
    def compare_strategies(self):
        """比較策略"""
        symbol = self.comp_symbol_var.get().upper()
        selected_strategies = [strategy for strategy, var in self.strategy_vars.items() if var.get()]
        
        if not symbol:
            messagebox.showwarning("警告", "請輸入股票代號")
            return
        
        if len(selected_strategies) < 2:
            messagebox.showwarning("警告", "請至少選擇兩個策略進行比較")
            return
        
        self.comparison_result.delete(1.0, tk.END)
        self.comparison_result.insert(tk.END, f"正在比較 {symbol} 的策略表現...\n\n")
        self.root.update()
        
        def compare():
            try:
                results = {}
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)
                
                for strategy in selected_strategies:
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
                        data = response.json()
                        results[strategy] = data
                
                # 格式化比較結果
                result_text = f"⚖️ {symbol} 策略比較結果\n"
                result_text += "="*60 + "\n\n"
                
                # 表格標題
                result_text += f"{'策略名稱':<20} {'報酬率':<10} {'夏普比率':<10} {'最大回撤':<10} {'勝率':<8}\n"
                result_text += "-"*60 + "\n"
                
                # 每個策略的結果
                for strategy, data in results.items():
                    perf = data['performance_metrics']
                    trades = data['trade_statistics']
                    
                    result_text += f"{strategy:<20} "
                    result_text += f"{perf['total_return_pct']:>8.2f}% "
                    result_text += f"{perf['sharpe_ratio']:>9.2f} "
                    result_text += f"{perf['max_drawdown_pct']:>8.2f}% "
                    result_text += f"{trades['win_rate']:>6.1f}%\n"
                
                # 找出最佳策略
                if results:
                    best_return = max(results.keys(), 
                                    key=lambda k: results[k]['performance_metrics']['total_return_pct'])
                    best_sharpe = max(results.keys(), 
                                    key=lambda k: results[k]['performance_metrics']['sharpe_ratio'])
                    
                    result_text += "\n🏆 最佳表現:\n"
                    result_text += f"   最高報酬: {best_return} "
                    result_text += f"({results[best_return]['performance_metrics']['total_return_pct']:.2f}%)\n"
                    result_text += f"   最佳夏普: {best_sharpe} "
                    result_text += f"({results[best_sharpe]['performance_metrics']['sharpe_ratio']:.2f})\n"
                
                self.comparison_result.delete(1.0, tk.END)
                self.comparison_result.insert(tk.END, result_text)
                
            except Exception as e:
                error_msg = f"策略比較錯誤: {str(e)}"
                self.comparison_result.delete(1.0, tk.END)
                self.comparison_result.insert(tk.END, error_msg)
        
        threading.Thread(target=compare, daemon=True).start()

def main():
    """主程式"""
    root = tk.Tk()
    app = TradingSystemGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()