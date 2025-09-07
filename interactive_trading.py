#!/usr/bin/env python3
"""
互動式交易系統操作介面
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def show_menu():
    print("\n" + "="*50)
    print("🚀 自動交易系統 - 互動式操作介面")
    print("="*50)
    print("1. 查看可用策略")
    print("2. 分析股票形態")
    print("3. 與 AI 討論策略")
    print("4. 執行回測")
    print("5. 比較策略表現")
    print("6. AI 問答")
    print("0. 退出")
    print("-"*50)

def get_strategies():
    """獲取可用策略"""
    response = requests.get(f"{BASE_URL}/backtest/strategies")
    if response.status_code == 200:
        data = response.json()
        print("\n可用策略:")
        for i, strategy in enumerate(data['available_strategies'], 1):
            detail = data['strategy_details'].get(strategy, {})
            print(f"{i}. {strategy}")
            print(f"   名稱: {detail.get('name', 'N/A')}")
            print(f"   描述: {detail.get('description', 'N/A')}")
        return data['available_strategies']
    else:
        print("獲取策略失敗")
        return []

def analyze_patterns():
    """分析股票形態"""
    symbol = input("\n請輸入股票代號 (例如 AAPL): ").upper().strip()
    if not symbol:
        symbol = "AAPL"
    
    period = input("請選擇分析期間 (1mo/3mo/6mo，預設 3mo): ").strip()
    if not period:
        period = "3mo"
    
    print(f"\n正在分析 {symbol} 的形態...")
    response = requests.post(f"{BASE_URL}/patterns/advanced/{symbol}?period={period}")
    
    if response.status_code == 200:
        data = response.json()
        summary = data['pattern_summary']
        
        print(f"\n📊 {symbol} 形態分析結果:")
        print(f"   總形態數: {summary['total_patterns']}")
        print(f"   高信心度: {summary['high_confidence_patterns']}")
        print(f"   看漲形態: {summary['bullish_patterns']}")
        print(f"   看跌形態: {summary['bearish_patterns']}")
        
        # 顯示交易訊號
        signals = data['trading_signals']
        if signals:
            print(f"\n📡 交易訊號 ({len(signals)} 個):")
            for signal in signals[:3]:
                print(f"   - {signal['type']}: {signal['description']}")
        
        return True
    else:
        print(f"分析失敗: {response.status_code}")
        return False

def ai_discussion():
    """AI 策略討論"""
    symbol = input("\n請輸入股票代號: ").upper().strip()
    if not symbol:
        symbol = "AAPL"
    
    question = input("請輸入您的問題 (按 Enter 使用預設問題): ").strip()
    if not question:
        question = "基於當前市況，建議使用什麼策略？"
    
    request_data = {
        "symbol": symbol,
        "period": "3mo",
        "current_strategy": "pattern_trading",
        "user_question": question,
        "include_patterns": True
    }
    
    print(f"\n🤖 AI 正在分析 {symbol}...")
    response = requests.post(f"{BASE_URL}/ai/discuss-strategy", json=request_data)
    
    if response.status_code == 200:
        data = response.json()
        ai_analysis = data['ai_discussion']
        
        print(f"\n🧠 AI 分析結果:")
        print(f"   建議策略: {ai_analysis['strategy_name']}")
        print(f"   信心評分: {ai_analysis['confidence_score']:.1f}/10")
        print(f"   市場分析: {ai_analysis['market_analysis'][:200]}...")
        print(f"   策略建議: {ai_analysis['strategy_recommendation'][:200]}...")
        
        return True
    elif response.status_code == 503:
        print("AI 服務不可用，需要設定 OpenAI API Key")
        return False
    else:
        print(f"AI 討論失敗: {response.status_code}")
        return False

def run_backtest():
    """執行回測"""
    symbol = input("\n請輸入股票代號: ").upper().strip()
    if not symbol:
        symbol = "AAPL"
    
    print("\n可用策略:")
    print("1. rsi_macd (RSI + MACD 策略)")
    print("2. ma_crossover (均線交叉策略)")
    print("3. pattern_trading (形態交易策略)")
    
    choice = input("請選擇策略 (1-3，預設 3): ").strip()
    strategy_map = {"1": "rsi_macd", "2": "ma_crossover", "3": "pattern_trading"}
    strategy = strategy_map.get(choice, "pattern_trading")
    
    days = input("請輸入回測天數 (預設 90): ").strip()
    try:
        days = int(days) if days else 90
    except:
        days = 90
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    backtest_request = {
        "symbol": symbol,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "strategy_name": strategy,
        "strategy_params": {},
        "initial_capital": 100000
    }
    
    if strategy == "pattern_trading":
        backtest_request["strategy_params"] = {
            "pattern_confidence_threshold": 0.6,
            "risk_reward_ratio": 2.0
        }
    
    print(f"\n🔄 正在回測 {symbol} ({strategy})...")
    response = requests.post(f"{BASE_URL}/backtest", json=backtest_request)
    
    if response.status_code == 200:
        data = response.json()
        perf = data['performance_metrics']
        trades = data['trade_statistics']
        
        print(f"\n📈 {symbol} 回測結果:")
        print(f"   策略: {strategy}")
        print(f"   期間: {days} 天")
        print(f"   總報酬率: {perf['total_return_pct']:.2f}%")
        print(f"   夏普比率: {perf['sharpe_ratio']:.2f}")
        print(f"   最大回撤: {perf['max_drawdown_pct']:.2f}%")
        print(f"   總交易: {trades['total_trades']} 次")
        print(f"   勝率: {trades['win_rate']:.1f}%")
        
        return True
    else:
        print(f"回測失敗: {response.status_code}")
        return False

def ai_qa():
    """AI 問答"""
    question = input("\n請輸入您的交易問題: ").strip()
    if not question:
        print("請輸入問題")
        return False
    
    request_data = {"question": question}
    
    print("\n🤖 AI 正在思考...")
    response = requests.post(f"{BASE_URL}/ai/ask", json=request_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n💡 AI 回答:")
        print(f"   {data['ai_answer']}")
        return True
    elif response.status_code == 503:
        print("AI 服務不可用，需要設定 OpenAI API Key")
        return False
    else:
        print(f"AI 問答失敗: {response.status_code}")
        return False

def main():
    """主程式"""
    print("正在檢查 API 連接...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("無法連接到交易系統 API，請確保伺服器運行中")
            return
    except:
        print("無法連接到交易系統，請確保伺服器運行中")
        print("啟動命令: python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    while True:
        show_menu()
        choice = input("請選擇功能 (0-6): ").strip()
        
        if choice == "0":
            print("感謝使用！")
            break
        elif choice == "1":
            get_strategies()
        elif choice == "2":
            analyze_patterns()
        elif choice == "3":
            ai_discussion()
        elif choice == "4":
            run_backtest()
        elif choice == "5":
            print("策略比較功能開發中...")
        elif choice == "6":
            ai_qa()
        else:
            print("無效選擇，請重新輸入")
        
        input("\n按 Enter 繼續...")

if __name__ == "__main__":
    main()