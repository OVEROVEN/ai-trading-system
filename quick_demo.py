#!/usr/bin/env python3
"""
簡單的操作示範腳本
使用方法: python quick_demo.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def main():
    print("=== 自動交易系統操作示範 ===\n")
    
    # 1. 查看可用策略
    print("1. 查看可用策略:")
    response = requests.get(f"{BASE_URL}/backtest/strategies")
    data = response.json()
    print(f"   可用策略: {data['available_strategies']}")
    
    # 2. 分析 AAPL 的形態
    print("\n2. 分析 AAPL 形態:")
    response = requests.post(f"{BASE_URL}/patterns/advanced/AAPL?period=3mo")
    data = response.json()
    print(f"   檢測到形態: {data['pattern_summary']['total_patterns']} 個")
    print(f"   高信心度形態: {data['pattern_summary']['high_confidence_patterns']} 個")
    
    # 3. 與 AI 討論策略
    print("\n3. 與 AI 討論 AAPL 策略:")
    ai_request = {
        "symbol": "AAPL",
        "period": "3mo",
        "current_strategy": "pattern_trading",
        "user_question": "基於當前形態，建議使用什麼策略？",
        "include_patterns": True
    }
    response = requests.post(f"{BASE_URL}/ai/discuss-strategy", json=ai_request)
    if response.status_code == 200:
        data = response.json()
        ai_analysis = data['ai_discussion']
        print(f"   AI 建議策略: {ai_analysis['strategy_name']}")
        print(f"   信心評分: {ai_analysis['confidence_score']:.1f}/10")
        print(f"   市場分析: {ai_analysis['market_analysis'][:100]}...")
    else:
        print(f"   AI 討論失敗 (需要 OpenAI API Key)")
    
    # 4. 回測形態策略
    print("\n4. 回測形態策略:")
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    backtest_request = {
        "symbol": "AAPL",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "strategy_name": "pattern_trading",
        "strategy_params": {
            "pattern_confidence_threshold": 0.6,
            "enable_flags": True,
            "enable_wedges": True,
            "enable_triangles": True,
            "risk_reward_ratio": 2.0
        },
        "initial_capital": 100000
    }
    
    response = requests.post(f"{BASE_URL}/backtest", json=backtest_request)
    if response.status_code == 200:
        data = response.json()
        perf = data['performance_metrics']
        trades = data['trade_statistics']
        print(f"   總報酬率: {perf['total_return_pct']:.2f}%")
        print(f"   夏普比率: {perf['sharpe_ratio']:.2f}")
        print(f"   總交易: {trades['total_trades']} 次")
        print(f"   勝率: {trades['win_rate']:.1f}%")
    else:
        print(f"   回測失敗: {response.status_code}")
    
    print("\n=== 操作完成 ===")
    print("\n下一步:")
    print("1. 打開瀏覽器: http://localhost:8000/docs")
    print("2. 測試不同的策略參數")
    print("3. 分析其他股票代號")

if __name__ == "__main__":
    main()