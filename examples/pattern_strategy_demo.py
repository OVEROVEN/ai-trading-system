#!/usr/bin/env python3
"""
形態學策略和 AI 討論功能完整範例
"""

import requests
import json
import asyncio
from datetime import datetime, timedelta
import pandas as pd

# API 基礎 URL
BASE_URL = "http://localhost:8000"

def test_api_health():
    """測試 API 健康狀態"""
    print("[HEALTH] 檢查 API 健康狀態...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("[OK] API 健康狀態良好")
            print(f"   - AI 分析: {'可用' if data['services']['ai_analysis'] else '不可用'}")
            return True
        else:
            print("[FAIL] API 健康檢查失敗")
            return False
    except Exception as e:
        print(f"[ERROR] 無法連接到 API: {str(e)}")
        return False

def test_available_strategies():
    """測試可用策略"""
    print("\n[STRATEGY] 獲取可用策略...")
    try:
        response = requests.get(f"{BASE_URL}/backtest/strategies")
        if response.status_code == 200:
            data = response.json()
            print("[OK] 策略清單獲取成功")
            print(f"   可用策略: {', '.join(data['available_strategies'])}")
            
            # 顯示形態策略詳情
            if 'pattern_trading' in data.get('strategy_details', {}):
                pattern_info = data['strategy_details']['pattern_trading']
                print(f"\n[PATTERN] 形態交易策略:")
                print(f"   名稱: {pattern_info['name']}")
                print(f"   描述: {pattern_info['description']}")
                print(f"   主要參數: {list(pattern_info['parameters'].keys())}")
            
            return True
        else:
            print("[FAIL] 獲取策略失敗")
            return False
    except Exception as e:
        print(f"[ERROR] 錯誤: {str(e)}")
        return False

def test_advanced_patterns(symbol="AAPL", period="3mo"):
    """測試進階形態分析"""
    print(f"\n[ANALYSIS] 測試進階形態分析 ({symbol})...")
    try:
        response = requests.post(
            f"{BASE_URL}/patterns/advanced/{symbol}",
            params={"period": period}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] 進階形態分析成功")
            
            summary = data['pattern_summary']
            print(f"   [SUMMARY] 形態摘要:")
            print(f"   - 總形態數: {summary['total_patterns']}")
            print(f"   - 高信心度: {summary['high_confidence_patterns']}")
            print(f"   - 看漲形態: {summary['bullish_patterns']}")
            print(f"   - 看跌形態: {summary['bearish_patterns']}")
            
            # 顯示檢測到的形態
            patterns = data['advanced_patterns']
            for pattern_type, pattern_list in patterns.items():
                if pattern_list:
                    print(f"\n   [PATTERN] {pattern_type.upper()}:")
                    for i, pattern in enumerate(pattern_list[:2], 1):
                        print(f"      {i}. {pattern['pattern_name']} ({pattern['direction']})")
                        print(f"         信心度: {pattern['confidence']:.2f}")
                        print(f"         目標價: ${pattern['target_price']:.2f}")
            
            # 顯示交易訊號
            signals = data['trading_signals']
            if signals:
                print(f"\n   [SIGNAL] 交易訊號 ({len(signals)} 個):")
                for signal in signals[:3]:
                    print(f"      {signal['type']}: {signal['source']}")
                    print(f"         {signal['description']}")
            
            return data
        else:
            print(f"[FAIL] 進階形態分析失敗: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"[ERROR] 錯誤: {str(e)}")
        return None

def test_ai_strategy_discussion(symbol="AAPL", user_question=None):
    """測試 AI 策略討論"""
    print(f"\n[AI] 測試 AI 策略討論 ({symbol})...")
    
    request_data = {
        "symbol": symbol,
        "period": "3mo",
        "current_strategy": "pattern_trading",
        "user_question": user_question or "基於當前市況，應該使用什麼策略？",
        "include_patterns": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ai/discuss-strategy",
            json=request_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] AI 策略討論成功")
            
            market = data['market_summary']
            print(f"   [MARKET] 市場摘要:")
            print(f"   - 當前價格: ${market['current_price']:.2f}")
            print(f"   - 檢測形態: {market['patterns_detected']} 個")
            
            ai_discussion = data['ai_discussion']
            print(f"\n   [AI] AI 分析:")
            print(f"   - 建議策略: {ai_discussion['strategy_name']}")
            print(f"   - 信心評分: {ai_discussion['confidence_score']:.1f}/10")
            print(f"   - 市場分析: {ai_discussion['market_analysis'][:200]}...")
            print(f"   - 策略建議: {ai_discussion['strategy_recommendation'][:200]}...")
            
            return data
        else:
            print(f"[FAIL] AI 策略討論失敗: {response.status_code}")
            if response.status_code == 503:
                print("   [INFO] 提示: 需要設定 OpenAI API Key")
            else:
                print(response.text)
            return None
            
    except Exception as e:
        print(f"[ERROR] 錯誤: {str(e)}")
        return None

def test_pattern_strategy_backtest(symbol="AAPL"):
    """測試形態策略回測"""
    print(f"\n[BACKTEST] 測試形態策略回測 ({symbol})...")
    
    # 計算日期範圍 (最近3個月)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    backtest_request = {
        "symbol": symbol,
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
        "initial_capital": 100000,
        "commission": 0.001,
        "stop_loss_pct": 0.02,
        "take_profit_pct": 0.06
    }
    
    try:
        response = requests.post(f"{BASE_URL}/backtest", json=backtest_request)
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] 形態策略回測成功")
            
            perf = data['performance_metrics']
            trades = data['trade_statistics']
            
            print(f"   [PERF] 績效表現:")
            print(f"   - 總報酬率: {perf['total_return_pct']:.2f}%")
            print(f"   - 夏普比率: {perf['sharpe_ratio']:.2f}")
            print(f"   - 最大回撤: {perf['max_drawdown_pct']:.2f}%")
            
            print(f"\n   [TRADE] 交易統計:")
            print(f"   - 總交易: {trades['total_trades']} 次")
            print(f"   - 勝率: {trades['win_rate']:.1f}%")
            print(f"   - 獲利因子: {trades['profit_factor']:.2f}")
            
            return data
        else:
            print(f"[FAIL] 形態策略回測失敗: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"[ERROR] 錯誤: {str(e)}")
        return None

def test_ai_ask_question():
    """測試 AI 問答功能"""
    print(f"\n[QA] 測試 AI 問答功能...")
    
    questions = [
        "形態學交易中，旗型和三角旗有什麼區別？",
        "如何判斷楔型突破的有效性？",
        "在震盪市場中應該使用什麼策略？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n   Q{i}: {question}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/ai/ask",
                json={"question": question}
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data['ai_answer']
                print(f"   A{i}: {answer[:300]}...")
            else:
                print(f"   A{i}: AI 回答失敗 ({response.status_code})")
                
        except Exception as e:
            print(f"   A{i}: 錯誤 - {str(e)}")

def compare_strategies(symbol="AAPL"):
    """比較不同策略的表現"""
    print(f"\n[COMPARE] 策略比較 ({symbol})...")
    
    strategies_to_test = [
        ("rsi_macd", {"rsi_oversold": 30, "rsi_overbought": 70}),
        ("ma_crossover", {"fast_period": 20, "slow_period": 50}),
        ("pattern_trading", {"pattern_confidence_threshold": 0.6, "risk_reward_ratio": 2.0})
    ]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    results = {}
    
    for strategy_name, params in strategies_to_test:
        print(f"\n   [TEST] 測試 {strategy_name}...")
        
        backtest_request = {
            "symbol": symbol,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "strategy_name": strategy_name,
            "strategy_params": params,
            "initial_capital": 100000,
            "commission": 0.001
        }
        
        try:
            response = requests.post(f"{BASE_URL}/backtest", json=backtest_request)
            if response.status_code == 200:
                data = response.json()
                perf = data['performance_metrics']
                trades = data['trade_statistics']
                
                results[strategy_name] = {
                    'return': perf['total_return_pct'],
                    'sharpe': perf['sharpe_ratio'],
                    'trades': trades['total_trades'],
                    'win_rate': trades['win_rate']
                }
                
                print(f"      報酬率: {perf['total_return_pct']:.2f}%")
                print(f"      夏普比率: {perf['sharpe_ratio']:.2f}")
                print(f"      交易次數: {trades['total_trades']}")
            else:
                print(f"      測試失敗: {response.status_code}")
                
        except Exception as e:
            print(f"      錯誤: {str(e)}")
    
    # 顯示比較結果
    if results:
        print(f"\n   [RESULT] 策略比較結果:")
        best_return = max(results.keys(), key=lambda k: results[k]['return'])
        best_sharpe = max(results.keys(), key=lambda k: results[k]['sharpe'])
        
        print(f"   - 最佳報酬: {best_return} ({results[best_return]['return']:.2f}%)")
        print(f"   - 最佳風險調整報酬: {best_sharpe} ({results[best_sharpe]['sharpe']:.2f})")

def main():
    """主程式"""
    print("[START] 形態學策略和 AI 討論功能完整測試")
    print("=" * 60)
    
    # 1. 檢查 API 狀態
    if not test_api_health():
        return
    
    # 2. 測試可用策略
    test_available_strategies()
    
    # 3. 測試進階形態分析
    pattern_data = test_advanced_patterns("AAPL")
    
    # 4. 測試 AI 策略討論
    ai_discussion = test_ai_strategy_discussion("AAPL", "根據檢測到的形態，建議使用什麼策略參數？")
    
    # 5. 測試形態策略回測
    backtest_results = test_pattern_strategy_backtest("AAPL")
    
    # 6. 測試 AI 問答
    test_ai_ask_question()
    
    # 7. 策略比較
    compare_strategies("AAPL")
    
    print("\n" + "=" * 60)
    print("[COMPLETE] 完整測試完成！")
    
    # 總結
    print("\n[SUMMARY] 功能總結:")
    print("[OK] 進階形態識別 (旗型、楔型、三角形等)")
    print("[OK] 形態學交易策略")
    print("[OK] AI 策略討論和建議")
    print("[OK] 回測和策略比較")
    print("[OK] AI 問答功能")
    
    if ai_discussion:
        print("\n[AI-SUMMARY] AI 建議摘要:")
        ai_info = ai_discussion['ai_discussion']
        print(f"   推薦策略: {ai_info['strategy_name']}")
        print(f"   信心評分: {ai_info['confidence_score']:.1f}/10")

if __name__ == "__main__":
    main()