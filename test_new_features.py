#!/usr/bin/env python3
"""
快速測試新增的形態學和 AI 功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def quick_test():
    """快速測試新功能"""
    
    print("=== 快速功能測試 ===")
    
    # 1. 測試可用策略
    print("\n1. 檢查可用策略...")
    try:
        response = requests.get(f"{BASE_URL}/backtest/strategies")
        if response.status_code == 200:
            strategies = response.json()['available_strategies']
            print(f"   可用策略: {strategies}")
            if 'pattern_trading' in strategies:
                print("   [OK] 形態交易策略已註冊")
            else:
                print("   [FAIL] 形態交易策略未找到")
        else:
            print(f"   [FAIL] 獲取策略失敗: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] 錯誤: {str(e)}")
    
    # 2. 測試進階形態分析
    print("\n2. 測試進階形態分析...")
    try:
        response = requests.post(f"{BASE_URL}/patterns/advanced/AAPL?period=3mo")
        if response.status_code == 200:
            data = response.json()
            summary = data['pattern_summary']
            print(f"   [OK] 檢測到 {summary['total_patterns']} 個形態")
            print(f"   - 高信心度: {summary['high_confidence_patterns']}")
            print(f"   - 交易訊號: {len(data['trading_signals'])} 個")
        else:
            print(f"   [FAIL] 形態分析失敗: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] 錯誤: {str(e)}")
    
    # 3. 測試 AI 問答 (如果可用)
    print("\n3. 測試 AI 問答功能...")
    try:
        response = requests.post(f"{BASE_URL}/ai/ask", json={
            "question": "形態學交易的優勢是什麼？"
        })
        if response.status_code == 200:
            data = response.json()
            answer = data['ai_answer']
            print(f"   [OK] AI 回答: {answer[:100]}...")
        elif response.status_code == 503:
            print("   [WARNING] AI 服務不可用 (需要 OpenAI API Key)")
        else:
            print(f"   [FAIL] AI 問答失敗: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] 錯誤: {str(e)}")
    
    print("\n=== 測試完成 ===")

if __name__ == "__main__":
    quick_test()