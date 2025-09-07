#!/usr/bin/env python3
"""
K線圖查看器 - 具有圖形化介面的股票分析工具
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import requests
from datetime import datetime, timedelta
import threading

BASE_URL = "http://localhost:8000"

class ChartViewerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("股票K線圖分析器")
        self.root.geometry("800x600")
        
        # 檢查API連接
        self.check_api_connection()
        
        # 創建介面
        self.create_widgets()
    
    def check_api_connection(self):
        """檢查API連接"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=3)
            if response.status_code != 200:
                messagebox.showerror("連接錯誤", 
                                   "無法連接到交易系統！\n請確保 API 伺服器運行中")
                return False
        except:
            messagebox.showerror("連接錯誤", 
                               "無法連接到交易系統！\n\n請先啟動 API 伺服器:\n"
                               "python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
            return False
        return True
    
    def create_widgets(self):
        """創建GUI元件"""
        
        # 標題
        title_label = tk.Label(self.root, text="📊 股票K線圖分析器", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 主要框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 控制面板
        control_frame = ttk.LabelFrame(main_frame, text="分析設定", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 第一行：股票選擇
        row1_frame = ttk.Frame(control_frame)
        row1_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1_frame, text="股票代號:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.symbol_var = tk.StringVar(value="AAPL")
        symbol_combo = ttk.Combobox(row1_frame, textvariable=self.symbol_var, width=15)
        symbol_combo['values'] = [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", 
            "META", "NVDA", "NFLX", "BABA", "AMD",
            "SPY", "QQQ", "2330.TW", "2317.TW"
        ]
        symbol_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(row1_frame, text="時間週期:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.period_var = tk.StringVar(value="3mo")
        period_combo = ttk.Combobox(row1_frame, textvariable=self.period_var, 
                                   values=["1mo", "3mo", "6mo"], width=10, state="readonly")
        period_combo.pack(side=tk.LEFT)
        
        # 第二行：分析選項
        row2_frame = ttk.Frame(control_frame)
        row2_frame.pack(fill=tk.X, pady=5)
        
        self.include_patterns = tk.BooleanVar(value=True)
        patterns_cb = ttk.Checkbutton(row2_frame, text="顯示形態標記", 
                                     variable=self.include_patterns)
        patterns_cb.pack(side=tk.LEFT, padx=(0, 20))
        
        self.include_indicators = tk.BooleanVar(value=True)
        indicators_cb = ttk.Checkbutton(row2_frame, text="顯示技術指標", 
                                       variable=self.include_indicators)
        indicators_cb.pack(side=tk.LEFT, padx=(0, 20))
        
        self.chart_type_var = tk.StringVar(value="tradingview")
        chart_combo = ttk.Combobox(row2_frame, textvariable=self.chart_type_var,
                                  values=["tradingview", "professional", "plotly", "mplfinance"], width=12, state="readonly")
        chart_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(row2_frame, text="主題:").pack(side=tk.LEFT, padx=(0, 5))
        self.theme_var = tk.StringVar(value="dark")
        theme_combo = ttk.Combobox(row2_frame, textvariable=self.theme_var,
                                  values=["dark", "light"], width=8, state="readonly")
        theme_combo.pack(side=tk.LEFT)
        
        # 第三行：按鈕
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # K線圖按鈕
        chart_btn = ttk.Button(button_frame, text="📊 生成K線圖", 
                              command=self.show_chart, style="Accent.TButton")
        chart_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 績效圖按鈕
        perf_btn = ttk.Button(button_frame, text="📈 策略績效圖", 
                             command=self.show_performance_chart)
        perf_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 形態分析按鈕
        pattern_btn = ttk.Button(button_frame, text="🎯 形態分析", 
                                command=self.analyze_patterns)
        pattern_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 資訊顯示區域
        info_frame = ttk.LabelFrame(main_frame, text="分析資訊", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # 創建文字區域和滾動條
        text_frame = ttk.Frame(info_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(text_frame, wrap=tk.WORD, height=20)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初始資訊
        self.info_text.insert(tk.END, 
            "📊 K線圖分析器使用說明：\n\n"
            "1. 選擇股票代號和時間週期\n"
            "2. 選擇是否顯示形態標記和技術指標\n"
            "3. 點擊「生成K線圖」查看圖表\n"
            "4. 點擊「形態分析」查看詳細分析\n"
            "5. 點擊「策略績效圖」查看回測結果\n\n"
            "💡 提示：\n"
            "- Plotly 圖表支援互動縮放\n"
            "- 形態標記會顯示在圖表上\n"
            "- 技術指標包含RSI、MACD、移動平均線等\n"
        )
        
        # 狀態列
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(status_frame, text="就緒")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
    
    def show_chart(self):
        """顯示K線圖"""
        symbol = self.symbol_var.get().upper().strip()
        if not symbol:
            messagebox.showwarning("警告", "請輸入股票代號")
            return
        
        period = self.period_var.get()
        chart_type = self.chart_type_var.get()
        theme = self.theme_var.get()
        include_patterns = self.include_patterns.get()
        include_indicators = self.include_indicators.get()
        
        self.status_label.config(text=f"正在生成 {symbol} K線圖...")
        self.root.update()
        
        def generate_chart():
            try:
                # 構建URL - 根據圖表類型選擇端點
                if chart_type == "tradingview":
                    url = f"{BASE_URL}/chart/tradingview/{symbol}"
                    params = {
                        "theme": theme,
                        "chart_type": "advanced",
                        "include_analysis": True
                    }
                elif chart_type == "professional":
                    url = f"{BASE_URL}/chart/professional/{symbol}"
                    params = {
                        "period": period,
                        "theme": theme,
                        "include_patterns": include_patterns,
                        "include_indicators": include_indicators
                    }
                else:
                    url = f"{BASE_URL}/chart/{symbol}"
                    params = {
                        "period": period,
                        "chart_type": chart_type,
                        "include_patterns": include_patterns,
                        "include_indicators": include_indicators
                    }
                
                # 打開瀏覽器顯示圖表
                full_url = f"{url}?" + "&".join([f"{k}={v}".lower() for k, v in params.items()])
                webbrowser.open(full_url)
                
                # 更新資訊區域
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, f"📊 {symbol} K線圖已在瀏覽器中打開\n\n")
                self.info_text.insert(tk.END, f"設定參數：\n")
                self.info_text.insert(tk.END, f"• 時間週期：{period}\n")
                self.info_text.insert(tk.END, f"• 圖表類型：{chart_type}\n")
                if chart_type == "professional":
                    self.info_text.insert(tk.END, f"• 主題：{theme}\n")
                self.info_text.insert(tk.END, f"• 形態標記：{'是' if include_patterns else '否'}\n")
                self.info_text.insert(tk.END, f"• 技術指標：{'是' if include_indicators else '否'}\n\n")
                self.info_text.insert(tk.END, f"🌐 圖表網址：{full_url}\n\n")
                self.info_text.insert(tk.END, "💡 提示：圖表支援互動操作，可以縮放和查看詳細數據\n")
                
                self.status_label.config(text="K線圖已生成")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"生成圖表失敗：{str(e)}")
                self.status_label.config(text="生成失敗")
        
        # 在背景執行
        threading.Thread(target=generate_chart, daemon=True).start()
    
    def show_performance_chart(self):
        """顯示策略績效圖"""
        symbol = self.symbol_var.get().upper().strip()
        if not symbol:
            messagebox.showwarning("警告", "請輸入股票代號")
            return
        
        self.status_label.config(text=f"正在生成 {symbol} 績效圖...")
        self.root.update()
        
        def generate_perf_chart():
            try:
                # 構建URL
                url = f"{BASE_URL}/chart/performance/{symbol}?strategy=pattern_trading&days=90"
                
                # 打開瀏覽器顯示圖表
                webbrowser.open(url)
                
                # 更新資訊區域
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, f"📈 {symbol} 策略績效圖已在瀏覽器中打開\n\n")
                self.info_text.insert(tk.END, "📊 績效圖表說明：\n")
                self.info_text.insert(tk.END, "• 藍線：形態交易策略績效\n")
                self.info_text.insert(tk.END, "• 灰線：買入持有基準績效\n")
                self.info_text.insert(tk.END, "• 回測期間：90天\n")
                self.info_text.insert(tk.END, "• 初始資金：$100,000\n\n")
                self.info_text.insert(tk.END, f"🌐 圖表網址：{url}\n")
                
                self.status_label.config(text="績效圖已生成")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"生成績效圖失敗：{str(e)}")
                self.status_label.config(text="生成失敗")
        
        threading.Thread(target=generate_perf_chart, daemon=True).start()
    
    def analyze_patterns(self):
        """執行形態分析"""
        symbol = self.symbol_var.get().upper().strip()
        if not symbol:
            messagebox.showwarning("警告", "請輸入股票代號")
            return
        
        period = self.period_var.get()
        self.status_label.config(text=f"正在分析 {symbol} 形態...")
        self.root.update()
        
        def run_analysis():
            try:
                # 調用形態分析API
                response = requests.post(f"{BASE_URL}/patterns/advanced/{symbol}?period={period}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 更新資訊區域
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.insert(tk.END, f"🎯 {symbol} 形態分析結果 ({period})\n")
                    self.info_text.insert(tk.END, "="*50 + "\n\n")
                    
                    summary = data['pattern_summary']
                    self.info_text.insert(tk.END, f"📊 摘要統計：\n")
                    self.info_text.insert(tk.END, f"• 總形態數：{summary['total_patterns']}\n")
                    self.info_text.insert(tk.END, f"• 高信心度形態：{summary['high_confidence_patterns']}\n")
                    self.info_text.insert(tk.END, f"• 看漲形態：{summary['bullish_patterns']}\n")
                    self.info_text.insert(tk.END, f"• 看跌形態：{summary['bearish_patterns']}\n\n")
                    
                    # 顯示檢測到的形態
                    patterns = data['advanced_patterns']
                    for pattern_type, pattern_list in patterns.items():
                        if pattern_list:
                            self.info_text.insert(tk.END, f"🎯 {pattern_type.upper()}：\n")
                            for i, pattern in enumerate(pattern_list[:3], 1):
                                self.info_text.insert(tk.END, f"  {i}. {pattern['pattern_name']} ({pattern['direction']})\n")
                                self.info_text.insert(tk.END, f"     信心度：{pattern['confidence']:.2f}\n")
                                self.info_text.insert(tk.END, f"     目標價：${pattern['target_price']:.2f}\n")
                                self.info_text.insert(tk.END, f"     停損：${pattern['stop_loss']:.2f}\n\n")
                    
                    # 顯示交易訊號
                    signals = data['trading_signals']
                    if signals:
                        self.info_text.insert(tk.END, f"📡 交易訊號（{len(signals)}個）：\n")
                        for signal in signals:
                            self.info_text.insert(tk.END, f"• {signal['type']}：{signal['description']}\n")
                            self.info_text.insert(tk.END, f"  信心度：{signal['confidence']:.2f}\n\n")
                    
                    self.status_label.config(text="形態分析完成")
                    
                else:
                    error_msg = f"分析失敗（HTTP {response.status_code}）"
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.insert(tk.END, error_msg)
                    self.status_label.config(text="分析失敗")
                    
            except Exception as e:
                error_msg = f"分析錯誤：{str(e)}"
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, error_msg)
                self.status_label.config(text="分析失敗")
        
        threading.Thread(target=run_analysis, daemon=True).start()

def main():
    """主程式"""
    root = tk.Tk()
    app = ChartViewerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()