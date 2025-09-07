#!/usr/bin/env python3
"""
測試K線圖功能
"""

import webbrowser
import time

BASE_URL = "http://localhost:8000"

def test_charts():
    print("=== K線圖功能測試 ===\n")
    
    print("1. 基本K線圖 (AAPL, 3個月)")
    url1 = f"{BASE_URL}/chart/AAPL?period=3mo&include_patterns=true&include_indicators=true"
    print(f"   網址: {url1}")
    webbrowser.open(url1)
    
    input("\n按 Enter 繼續下一個圖表...")
    
    print("\n2. 不含形態標記的圖表 (TSLA, 1個月)")
    url2 = f"{BASE_URL}/chart/TSLA?period=1mo&include_patterns=false&include_indicators=true"
    print(f"   網址: {url2}")
    webbrowser.open(url2)
    
    input("\n按 Enter 繼續下一個圖表...")
    
    print("\n3. 策略績效比較圖 (AAPL)")
    url3 = f"{BASE_URL}/chart/performance/AAPL?strategy=pattern_trading&days=90"
    print(f"   網址: {url3}")
    webbrowser.open(url3)
    
    print("\n✅ K線圖功能測試完成！")
    print("\n📊 功能說明:")
    print("• 互動式K線圖，可縮放查看細節")
    print("• 自動標記檢測到的形態")
    print("• 顯示技術指標 (RSI, MACD, 移動平均線)")
    print("• 策略績效與基準比較")
    
    print("\n🎯 使用方式:")
    print("1. 圖形化界面: python chart_viewer.py")
    print("2. 直接訪問: http://localhost:8000/chart/SYMBOL")
    print("3. Web API 文檔: http://localhost:8000/docs")

if __name__ == "__main__":
    test_charts()