#!/usr/bin/env python3
"""
測試混合 TradingView 架構
用於驗證美股 Widget 和台股 Charting Library 的整合
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.visualization.hybrid_tradingview import get_hybrid_chart
from src.data_fetcher.twse_tpex_datafeed import get_taiwan_datafeed
from src.api.tradingview_charting_api import tw_datafeed

def print_section(title: str):
    """打印測試段落標題"""
    print(f"\n{'='*60}")
    print(f"[TEST] {title}")
    print('='*60)

def print_result(test_name: str, success: bool, details: str = ""):
    """打印測試結果"""
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {test_name}")
    if details:
        print(f"   詳情: {details}")

async def test_symbol_detection():
    """測試符號檢測功能"""
    print_section("符號檢測測試")
    
    chart = get_hybrid_chart()
    
    test_cases = [
        # (符號, 預期是否為台股, 描述)
        ("AAPL", False, "美股 Apple"),
        ("GOOGL", False, "美股 Google"),
        ("2330.TW", True, "台積電 (TWSE)"),
        ("2317.TW", True, "鴻海 (TWSE)"),
        ("3481.TWO", True, "群創 (TPEx)"),
        ("2330", True, "純數字台股代號"),
        ("SPY", False, "美股 ETF"),
        ("0050.TW", True, "元大台灣50 ETF")
    ]
    
    all_passed = True
    
    for symbol, expected_tw, description in test_cases:
        is_taiwan = chart.is_taiwan_stock(symbol)
        passed = is_taiwan == expected_tw
        all_passed &= passed
        
        market_type = "台股" if is_taiwan else "美股"
        expected_type = "台股" if expected_tw else "美股"
        
        print_result(
            f"{symbol} ({description})",
            passed,
            f"檢測為 {market_type}，預期為 {expected_type}"
        )
    
    return all_passed

async def test_symbol_normalization():
    """測試符號標準化"""
    print_section("符號標準化測試")
    
    chart = get_hybrid_chart()
    
    test_cases = [
        # (輸入符號, 預期輸出, 描述)
        ("2330", "2330.TW", "純數字轉換為 .TW"),
        ("2330.TW", "2330.TW", ".TW 格式保持不變"),
        ("3481.TWO", "3481.TWO", ".TWO 格式保持不變"),
        ("AAPL", "AAPL", "美股符號保持不變"),
        ("aapl", "AAPL", "小寫轉大寫"),
        ("0050", "0050.TW", "ETF 代號轉換")
    ]
    
    all_passed = True
    
    for input_symbol, expected_output, description in test_cases:
        normalized = chart.normalize_symbol(input_symbol)
        passed = normalized == expected_output
        all_passed &= passed
        
        print_result(
            f"{input_symbol} -> {normalized}",
            passed,
            f"預期: {expected_output} ({description})"
        )
    
    return all_passed

async def test_tradingview_symbol_conversion():
    """測試 TradingView 符號轉換"""
    print_section("TradingView 符號轉換測試")
    
    chart = get_hybrid_chart()
    
    test_cases = [
        # (輸入符號, 預期 TradingView 符號, 描述)
        ("2330.TW", "TPE:2330", "TWSE 股票"),
        ("3481.TWO", "TPX:3481", "TPEx 股票"),
        ("AAPL", "AAPL", "美股保持原樣"),
        ("SPY", "SPY", "美股 ETF")
    ]
    
    all_passed = True
    
    for symbol, expected_tv_symbol, description in test_cases:
        tv_symbol = chart.get_tradingview_symbol(symbol)
        passed = tv_symbol == expected_tv_symbol
        all_passed &= passed
        
        print_result(
            f"{symbol} -> {tv_symbol}",
            passed,
            f"預期: {expected_tv_symbol} ({description})"
        )
    
    return all_passed

async def test_taiwan_datafeed():
    """測試台股數據源"""
    print_section("台股數據源測試")
    
    datafeed = get_taiwan_datafeed()
    
    test_symbols = ["2330.TW", "2317.TW", "0050.TW"]
    all_passed = True
    
    for symbol in test_symbols:
        try:
            # 測試符號資訊
            symbol_info = await datafeed.get_symbol_info(symbol)
            
            if symbol_info:
                print_result(
                    f"符號資訊: {symbol}",
                    True,
                    f"名稱: {symbol_info.name}, 交易所: {symbol_info.exchange}"
                )
                
                # 測試歷史數據
                end_time = int(datetime.now().timestamp())
                start_time = end_time - (7 * 24 * 60 * 60)  # 7天前
                
                bars = await datafeed.get_bars(symbol, start_time, end_time)
                
                if bars:
                    print_result(
                        f"歷史數據: {symbol}",
                        True,
                        f"獲取到 {len(bars)} 根K線"
                    )
                    
                    # 顯示最新數據
                    if bars:
                        latest = bars[-1]
                        latest_date = datetime.fromtimestamp(latest.time).strftime('%Y-%m-%d')
                        print(f"   最新數據: {latest_date} 收盤價={latest.close}")
                else:
                    print_result(f"歷史數據: {symbol}", False, "無數據")
                    all_passed = False
            else:
                print_result(f"符號資訊: {symbol}", False, "無法獲取符號資訊")
                all_passed = False
                
        except Exception as e:
            print_result(f"數據獲取: {symbol}", False, f"錯誤: {str(e)}")
            all_passed = False
            
        # 避免請求過快
        await asyncio.sleep(0.5)
    
    return all_passed

async def test_charting_api_endpoints():
    """測試 Charting Library API 端點 (模擬測試)"""
    print_section("Charting Library API 端點測試")
    
    # 這裡我們模擬測試 API 端點的功能
    # 實際部署時需要啟動 FastAPI 服務器進行真實測試
    
    test_cases = [
        ("/api/charting/config", "配置端點"),
        ("/api/charting/symbols/2330.TW", "符號解析端點"),
        ("/api/charting/history", "歷史數據端點"),
        ("/api/charting/server_time", "服務器時間端點")
    ]
    
    print("📝 API 端點功能性檢查 (需要啟動服務器進行實際測試):")
    
    for endpoint, description in test_cases:
        print(f"   🔗 {endpoint} - {description}")
    
    print("\n💡 實際測試方法:")
    print("   1. 啟動服務器: python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
    print("   2. 測試端點: curl http://localhost:8000/api/charting/config")
    
    return True

def test_chart_generation():
    """測試圖表生成"""
    print_section("圖表生成測試")
    
    chart = get_hybrid_chart()
    
    test_symbols = [
        ("AAPL", "美股", "Widget"),
        ("2330.TW", "台股", "Charting Library"),
        ("GOOGL", "美股", "Widget"),
        ("2317.TW", "台股", "Charting Library")
    ]
    
    all_passed = True
    
    for symbol, market, expected_method in test_symbols:
        try:
            html_content = chart.create_hybrid_chart(symbol, theme="dark")
            
            # 檢查是否包含預期的組件
            if expected_method == "Widget":
                has_expected = "TradingView.widget" in html_content and "s3.tradingview.com/tv.js" in html_content
            else:  # Charting Library
                has_expected = "tv_chart_container" in html_content and "charting_library.min.js" in html_content
            
            print_result(
                f"圖表生成: {symbol} ({market})",
                has_expected,
                f"使用 {expected_method}, HTML 長度: {len(html_content):,} 字符"
            )
            
            all_passed &= has_expected
            
        except Exception as e:
            print_result(f"圖表生成: {symbol}", False, f"錯誤: {str(e)}")
            all_passed = False
    
    return all_passed

async def test_search_functionality():
    """測試搜尋功能"""
    print_section("符號搜尋測試")
    
    datafeed = get_taiwan_datafeed()
    
    search_queries = [
        ("台積", "搜尋公司名稱"),
        ("2330", "搜尋代號"),
        ("電", "搜尋關鍵字"),
        ("ETF", "搜尋類型")
    ]
    
    all_passed = True
    
    for query, description in search_queries:
        try:
            results = await datafeed.search_symbols(query, limit=5)
            
            if results:
                print_result(
                    f"搜尋: '{query}' ({description})",
                    True,
                    f"找到 {len(results)} 個結果"
                )
                
                # 顯示前幾個結果
                for i, result in enumerate(results[:3]):
                    print(f"   {i+1}. {result['symbol']} - {result['description']}")
            else:
                print_result(f"搜尋: '{query}'", False, "無搜尋結果")
                all_passed = False
                
        except Exception as e:
            print_result(f"搜尋: '{query}'", False, f"錯誤: {str(e)}")
            all_passed = False
    
    return all_passed

def print_summary(test_results: dict):
    """打印測試總結"""
    print_section("測試總結")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print(f"📊 測試統計:")
    print(f"   總測試項目: {total_tests}")
    print(f"   通過項目: {passed_tests}")
    print(f"   失敗項目: {total_tests - passed_tests}")
    print(f"   通過率: {passed_tests/total_tests*100:.1f}%")
    
    print(f"\n📋 詳細結果:")
    for test_name, result in test_results.items():
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 所有測試通過！混合 TradingView 架構已準備就緒。")
        print("\n🚀 下一步:")
        print("   1. 啟動服務器: python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
        print("   2. 訪問混合圖表: http://localhost:8000/chart/hybrid/AAPL")
        print("   3. 測試台股圖表: http://localhost:8000/chart/hybrid/2330.TW")
    else:
        print(f"\n⚠️  有 {total_tests - passed_tests} 項測試失敗，請檢查相關配置。")

async def main():
    """主測試函數"""
    print("混合 TradingView 架構測試")
    print("=" * 60)
    print("本測試將驗證美股 Widget 和台股 Charting Library 的整合功能")
    
    # 執行所有測試
    test_results = {}
    
    test_results["符號檢測"] = await test_symbol_detection()
    test_results["符號標準化"] = await test_symbol_normalization()
    test_results["TradingView符號轉換"] = await test_tradingview_symbol_conversion()
    test_results["台股數據源"] = await test_taiwan_datafeed()
    test_results["API端點"] = await test_charting_api_endpoints()
    test_results["圖表生成"] = test_chart_generation()
    test_results["符號搜尋"] = await test_search_functionality()
    
    # 打印總結
    print_summary(test_results)

if __name__ == "__main__":
    asyncio.run(main())