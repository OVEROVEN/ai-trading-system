#!/usr/bin/env python3
"""
簡化版混合 TradingView 架構測試
避免 Unicode 編碼問題
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.visualization.hybrid_tradingview import get_hybrid_chart
from src.data_fetcher.twse_tpex_datafeed import get_taiwan_datafeed

def test_symbol_detection():
    """測試符號檢測功能"""
    print("\n[TEST] 符號檢測測試")
    print("=" * 50)
    
    chart = get_hybrid_chart()
    
    test_cases = [
        ("AAPL", False, "美股 Apple"),
        ("GOOGL", False, "美股 Google"),
        ("2330.TW", True, "台積電 TWSE"),
        ("2317.TW", True, "鴻海 TWSE"),
        ("3481.TWO", True, "群創 TPEx"),
        ("2330", True, "純數字台股代號"),
        ("SPY", False, "美股 ETF"),
        ("0050.TW", True, "元大台灣50 ETF")
    ]
    
    all_passed = True
    
    for symbol, expected_tw, description in test_cases:
        is_taiwan = chart.is_taiwan_stock(symbol)
        passed = is_taiwan == expected_tw
        all_passed &= passed
        
        status = "[PASS]" if passed else "[FAIL]"
        market_type = "台股" if is_taiwan else "美股"
        print(f"{status} {symbol} ({description}) -> {market_type}")
    
    return all_passed

def test_symbol_normalization():
    """測試符號標準化"""
    print("\n[TEST] 符號標準化測試")
    print("=" * 50)
    
    chart = get_hybrid_chart()
    
    test_cases = [
        ("2330", "2330.TW"),
        ("2330.TW", "2330.TW"),
        ("3481.TWO", "3481.TWO"),
        ("AAPL", "AAPL"),
        ("aapl", "AAPL")
    ]
    
    all_passed = True
    
    for input_symbol, expected_output in test_cases:
        normalized = chart.normalize_symbol(input_symbol)
        passed = normalized == expected_output
        all_passed &= passed
        
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {input_symbol} -> {normalized} (預期: {expected_output})")
    
    return all_passed

async def test_taiwan_datafeed():
    """測試台股數據源"""
    print("\n[TEST] 台股數據源測試")
    print("=" * 50)
    
    datafeed = get_taiwan_datafeed()
    test_symbols = ["2330.TW", "2317.TW"]
    all_passed = True
    
    for symbol in test_symbols:
        try:
            # 測試符號資訊
            symbol_info = await datafeed.get_symbol_info(symbol)
            
            if symbol_info:
                print(f"[PASS] {symbol} 符號資訊: {symbol_info.name} ({symbol_info.exchange})")
                
                # 測試歷史數據
                end_time = int(datetime.now().timestamp())
                start_time = end_time - (7 * 24 * 60 * 60)  # 7天前
                
                bars = await datafeed.get_bars(symbol, start_time, end_time)
                
                if bars:
                    print(f"[PASS] {symbol} 歷史數據: {len(bars)} 根K線")
                else:
                    print(f"[FAIL] {symbol} 歷史數據: 無數據")
                    all_passed = False
            else:
                print(f"[FAIL] {symbol} 無法獲取符號資訊")
                all_passed = False
                
        except Exception as e:
            print(f"[FAIL] {symbol} 錯誤: {str(e)}")
            all_passed = False
            
        await asyncio.sleep(0.5)
    
    return all_passed

def test_chart_generation():
    """測試圖表生成"""
    print("\n[TEST] 圖表生成測試")
    print("=" * 50)
    
    chart = get_hybrid_chart()
    
    test_symbols = [
        ("AAPL", "美股", "Widget"),
        ("2330.TW", "台股", "Charting Library")
    ]
    
    all_passed = True
    
    for symbol, market, expected_method in test_symbols:
        try:
            html_content = chart.create_hybrid_chart(symbol, theme="dark")
            
            # 檢查是否包含預期的組件
            if expected_method == "Widget":
                has_expected = "TradingView.widget" in html_content
            else:  # Charting Library
                has_expected = "tv_chart_container" in html_content
            
            status = "[PASS]" if has_expected else "[FAIL]"
            print(f"{status} {symbol} ({market}) -> {expected_method}")
            print(f"       HTML 長度: {len(html_content):,} 字符")
            
            all_passed &= has_expected
            
        except Exception as e:
            print(f"[FAIL] {symbol} 錯誤: {str(e)}")
            all_passed = False
    
    return all_passed

async def main():
    """主測試函數"""
    print("混合 TradingView 架構測試")
    print("=" * 60)
    print("本測試將驗證美股 Widget 和台股 Charting Library 的整合功能")
    
    # 執行測試
    test_results = {
        "符號檢測": test_symbol_detection(),
        "符號標準化": test_symbol_normalization(), 
        "台股數據源": await test_taiwan_datafeed(),
        "圖表生成": test_chart_generation()
    }
    
    # 打印總結
    print("\n[SUMMARY] 測試總結")
    print("=" * 50)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print(f"總測試項目: {total_tests}")
    print(f"通過項目: {passed_tests}")
    print(f"失敗項目: {total_tests - passed_tests}")
    print(f"通過率: {passed_tests/total_tests*100:.1f}%")
    
    print(f"\n詳細結果:")
    for test_name, result in test_results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"   {status} {test_name}")
    
    if passed_tests == total_tests:
        print(f"\n所有測試通過！混合 TradingView 架構已準備就緒。")
        print("\n下一步:")
        print("   1. 啟動服務器: python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
        print("   2. 訪問混合圖表: http://localhost:8000/chart/hybrid/AAPL")
        print("   3. 測試台股圖表: http://localhost:8000/chart/hybrid/2330.TW")
    else:
        print(f"\n有 {total_tests - passed_tests} 項測試失敗，請檢查相關配置。")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)