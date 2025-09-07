#!/usr/bin/env python3
"""
Enhanced Strategy Analysis Dashboard Demo
增強型策略分析儀表板演示

這個演示展示了完整的TradingView整合與策略分析界面
"""

import webbrowser
import time
import subprocess
import sys
from pathlib import Path

def main():
    """演示增強型策略分析儀表板"""
    
    print("🚀 啟動增強型AI策略分析儀表板演示")
    print("=" * 60)
    
    print("\n📊 功能特色:")
    print("✅ TradingView 圖表完整整合")
    print("✅ 即時技術指標與交易訊號")
    print("✅ AI 策略建議與對話")
    print("✅ 綜合回測分析")
    print("✅ 響應式設計，支援台股與美股")
    
    print("\n🔧 啟動 FastAPI 服務器...")
    try:
        # 使用 uv 啟動服務器
        print("正在啟動服務器... (uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000)")
        server_process = subprocess.Popen([
            "uv", "run", "python", "-m", "uvicorn", 
            "src.api.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], 
        cwd=Path.cwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
        )
        
        # 等待服務器啟動
        print("等待服務器啟動...")
        time.sleep(5)
        
        print("\n🌐 訪問增強型儀表板:")
        dashboard_url = "http://localhost:8000/dashboard"
        print(f"   主儀表板: {dashboard_url}")
        print(f"   API文檔: http://localhost:8000/docs")
        print(f"   TradingView整合: http://localhost:8000/chart/custom/AAPL")
        
        print("\n🎯 建議測試流程:")
        print("1. 在儀表板中輸入股票代號 (例: AAPL, TSLA, 2330.TW)")
        print("2. 點擊 '分析' 查看完整技術分析")
        print("3. 使用 AI 策略顧問進行對話")
        print("4. 查看回測結果與策略表現")
        print("5. 切換不同股票測試多市場支援")
        
        print("\n📱 響應式設計測試:")
        print("• 桌面版: 完整雙欄布局")
        print("• 平板版: 垂直堆疊布局") 
        print("• 手機版: 單欄優化顯示")
        
        # 自動開啟瀏覽器
        try:
            webbrowser.open(dashboard_url)
            print(f"\n✅ 已自動開啟瀏覽器: {dashboard_url}")
        except Exception as e:
            print(f"\n⚠️ 請手動開啟: {dashboard_url}")
        
        print("\n🔥 系統狀態監控:")
        print("   服務器日誌:")
        
        # 顯示服務器輸出
        try:
            for line in server_process.stdout:
                if line:
                    print(f"   {line.strip()}")
                if "Application startup complete" in line:
                    print("\n✅ 服務器完全啟動!")
                    break
        except KeyboardInterrupt:
            print("\n\n🛑 正在關閉服務器...")
            server_process.terminate()
            server_process.wait()
            print("✅ 服務器已關閉")
            
    except FileNotFoundError:
        print("\n❌ 錯誤: 找不到 uv 命令")
        print("請確保已安裝 uv 並且在 PATH 中")
        print("安裝指令: pip install uv")
    
    except Exception as e:
        print(f"\n❌ 啟動錯誤: {e}")
        print("\n🔧 手動啟動方式:")
        print("uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")

def show_api_endpoints():
    """顯示可用的API端點"""
    print("\n📡 新增API端點:")
    print("├── GET /dashboard - 策略分析儀表板")
    print("├── GET /api/dashboard/signals/{symbol} - 即時交易訊號")
    print("├── GET /api/analysis/comprehensive/{symbol} - 綜合分析")
    print("├── POST /api/patterns/signals - 技術形態訊號")
    print("├── POST /api/ai/strategy-chat/start - AI策略對話")
    print("├── POST /api/backtest/pattern-strategy - 形態策略回測")
    print("└── GET /chart/custom/{symbol} - TradingView整合")

if __name__ == "__main__":
    show_api_endpoints()
    main()