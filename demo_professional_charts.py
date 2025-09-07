#!/usr/bin/env python3
"""
展示TradingView級別專業K線圖功能
"""

import webbrowser
import time

BASE_URL = "http://localhost:8000"

def demo_professional_charts():
    print("=== TradingView級別專業K線圖展示 ===\n")
    
    print("[OK] 專業圖表功能已完成升級！\n")
    
    # 自動打開專業圖表
    print("正在開啟AAPL專業深色主題圖表...")
    url = f"{BASE_URL}/chart/professional/AAPL?period=3mo&theme=dark&include_patterns=true&include_indicators=true"
    webbrowser.open(url)
    
    print(f"圖表網址: {url}\n")
    
    print("專業圖表功能特色：")
    print("• [OK] TradingView風格設計")
    print("• [OK] 深色/淺色主題")
    print("• [OK] 商業級技術指標")
    print("• [OK] 專業形態標記")
    print("• [OK] 互動式操作")
    print("• [OK] 高品質視覺化\n")
    
    print("更多測試方式：")
    print(f"• 淺色主題: {BASE_URL}/chart/professional/TSLA?theme=light")
    print(f"• 圖形界面: python chart_viewer.py")
    print(f"• API文檔: {BASE_URL}/docs")

if __name__ == "__main__":
    demo_professional_charts()