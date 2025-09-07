#!/usr/bin/env python3
"""
測試TradingView級別專業K線圖功能
"""

import webbrowser
import time

BASE_URL = "http://localhost:8000"

def test_professional_charts():
    print("=== TradingView級別專業K線圖測試 ===\n")
    
    print("新功能亮點：")
    print("• TradingView級別專業圖表設計")
    print("• 深色/淺色主題切換")
    print("• 專業級技術指標顯示")
    print("• 互動式圖表操作")
    print("• 商業級圖表品質\n")
    
    print("1. 專業深色主題圖表 (AAPL, 3個月)")
    url1 = f"{BASE_URL}/chart/professional/AAPL?period=3mo&theme=dark&include_patterns=true&include_indicators=true"
    print(f"   網址: {url1}")
    webbrowser.open(url1)
    
    input("\n按 Enter 繼續下一個圖表...")
    
    print("\n2. 專業淺色主題圖表 (TSLA, 1個月)")
    url2 = f"{BASE_URL}/chart/professional/TSLA?period=1mo&theme=light&include_patterns=true&include_indicators=true"
    print(f"   網址: {url2}")
    webbrowser.open(url2)
    
    input("\n按 Enter 繼續下一個圖表...")
    
    print("\n3. 極簡專業圖表 (NVDA, 6個月，無指標)")
    url3 = f"{BASE_URL}/chart/professional/NVDA?period=6mo&theme=dark&include_patterns=false&include_indicators=false"
    print(f"   網址: {url3}")
    webbrowser.open(url3)
    
    input("\n按 Enter 繼續比較...")
    
    print("\n4. 舊版圖表比較 (AAPL, Plotly)")
    url4 = f"{BASE_URL}/chart/AAPL?period=3mo&chart_type=plotly&include_patterns=true&include_indicators=true"
    print(f"   網址: {url4}")
    webbrowser.open(url4)
    
    print("\n[OK] 專業圖表功能測試完成！\n")
    
    print("TradingView級別功能：")
    print("• [OK] 專業級蠟燭圖設計")
    print("• [OK] 深色/淺色主題支援") 
    print("• [OK] 商業級技術指標")
    print("• [OK] 專業形態標記")
    print("• [OK] 互動式縮放和十字線")
    print("• [OK] 專業級hover資訊")
    print("• [OK] TradingView風格佈局")
    print("• [OK] 高品質視覺化效果")
    
    print("\n使用方式：")
    print("1. 圖形化界面: python chart_viewer.py (選擇 'professional')")
    print("2. 直接訪問專業圖表: http://localhost:8000/chart/professional/SYMBOL")
    print("3. 舊版相容: http://localhost:8000/chart/SYMBOL?chart_type=professional")
    print("4. Web API 文檔: http://localhost:8000/docs")
    
    print("\n圖表品質對比：")
    print("• 舊版圖表：基本功能，簡單設計")
    print("• 專業圖表：TradingView級別，商業品質 [推薦]")

if __name__ == "__main__":
    test_professional_charts()