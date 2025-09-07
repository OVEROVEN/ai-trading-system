#!/usr/bin/env python3
"""
自動交易系統啟動器 - 提供多種圖形化操作方式
"""

import webbrowser
import sys
import subprocess
import time

def main():
    print("[START] 自動交易系統操作選擇")
    print("="*50)
    
    print("\n[OPTIONS] 選擇您偏好的操作方式:")
    print("1. [WEB] Web API 圖形化介面 (最推薦)")
    print("   - 點擊式操作，直接在網頁中測試")
    print("   - 自動產生介面，無需安裝額外軟體")
    print("   - 支援所有功能：形態分析、AI討論、回測")
    
    print("\n2. [CHART] K線圖查看器 (新功能!)")
    print("   - 視覺化K線圖和技術指標")
    print("   - 形態標記和交易訊號")
    print("   - 策略績效比較圖表")
    
    print("\n3. [CLI] 命令行互動選單")
    print("   - 文字選單式操作")
    print("   - 所有選項都可以用數字選擇")
    print("   - 無需記憶複雜指令")
    
    print("\n4. [DEMO] 快速功能示範")
    print("   - 一鍵展示所有功能")
    print("   - 查看系統能力")
    
    choice = input("\n請選擇操作方式 (1-4, 預設1): ").strip()
    
    if choice == "2":
        print("\n[CHART] 啟動K線圖查看器...")
        print("[TIP] 提示：可視化股票圖表，支援形態標記和技術指標")
        time.sleep(2)
        subprocess.run([sys.executable, "chart_viewer.py"])
        
    elif choice == "3":
        print("\n[CLI] 啟動命令行互動介面...")
        print("[TIP] 提示：所有參數都可以用選單選擇，不需要手動輸入")
        time.sleep(2)
        subprocess.run([sys.executable, "interactive_trading.py"])
        
    elif choice == "4":
        print("\n[DEMO] 運行功能示範...")
        print("[INFO] 將展示：形態分析、AI討論、策略回測等功能")
        time.sleep(2)
        subprocess.run([sys.executable, "quick_demo.py"])
        
    else:
        print("\n[WEB] 打開 Web API 圖形化介面...")
        print("\n[GUIDE] 使用說明:")
        print("[OK] 頁面會自動顯示所有可用功能")
        print("[OK] 每個功能都有「Try it out」按鈕可以直接測試")
        print("[OK] 所有參數都有下拉選單或預設值")
        print("[OK] 不需要手動輸入複雜的 JSON 格式")
        print("[OK] 可以直接看到結果和回應")
        
        print("\n[FEATURES] 主要功能:")
        print("• [PATTERN] POST /patterns/advanced/{symbol} - 形態分析")
        print("• [AI] POST /ai/discuss-strategy - AI 策略討論") 
        print("• [BACKTEST] POST /backtest - 策略回測")
        print("• [STRATEGY] GET /backtest/strategies - 查看可用策略")
        
        print("\n[OPEN] 正在打開瀏覽器...")
        time.sleep(2)
        webbrowser.open("http://localhost:8000/docs")
        
        print("\n[TIPS] 小技巧:")
        print("• 點擊任何 API 端點展開")
        print("• 點擊「Try it out」開始測試")
        print("• 修改參數後點擊「Execute」")
        print("• 在 Response body 查看結果")

if __name__ == "__main__":
    main()