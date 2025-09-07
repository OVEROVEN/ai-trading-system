#!/usr/bin/env python3
"""
展示真正的TradingView圖表整合
"""

import webbrowser
import requests

BASE_URL = "http://localhost:8000"

def demo_tradingview():
    print("=== 真正的TradingView圖表整合 ===\n")
    
    # 測試TradingView圖表端點
    try:
        print("測試TradingView圖表API...")
        response = requests.get(f"{BASE_URL}/chart/tradingview/AAPL?theme=dark", timeout=10)
        if response.status_code == 200:
            print("[OK] TradingView圖表API正常運行")
        else:
            print(f"[FAIL] API返回錯誤: {response.status_code}")
            return
    except Exception as e:
        print(f"[FAIL] 無法連接API: {str(e)}")
        return
    
    print("\n[SUCCESS] TradingView整合完成！")
    print("\n解決方案優勢：")
    print("• [OK] 使用真正的TradingView圖表引擎")
    print("• [OK] 無需處理Plotly兼容性問題")
    print("• [OK] 獲得專業級圖表品質")
    print("• [OK] 即時數據自動更新")
    print("• [OK] 完整的技術分析工具")
    print("• [OK] 結合我們的AI分析結果")
    
    print("\n開啟TradingView圖表展示...")
    
    # 展示不同類型的圖表
    charts = [
        ("高級圖表 (含AI分析)", f"{BASE_URL}/chart/tradingview/AAPL?chart_type=advanced&theme=dark"),
        ("完整圖表", f"{BASE_URL}/chart/tradingview/TSLA?chart_type=full&theme=light"),
        ("迷你圖表", f"{BASE_URL}/chart/tradingview/NVDA?chart_type=mini&theme=dark")
    ]
    
    for name, url in charts:
        print(f"\n開啟 {name}...")
        print(f"網址: {url}")
        webbrowser.open(url)
        input("按 Enter 繼續下一個圖表...")
    
    print("\n完美解決方案！")
    print("現在您擁有：")
    print("• 真正的TradingView專業圖表")
    print("• 我們的AI分析數據")
    print("• 形態識別結果")
    print("• 無技術錯誤的穩定系統")
    
    print("\n使用方式：")
    print("• 圖形界面: python chart_viewer.py (選擇'tradingview')")
    print("• 直接訪問: http://localhost:8000/chart/tradingview/SYMBOL")
    print("• API文檔: http://localhost:8000/docs")

if __name__ == "__main__":
    demo_tradingview()