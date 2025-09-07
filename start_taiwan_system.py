#!/usr/bin/env python3
"""
快速啟動台股整合系統
Updated with Taiwan Stock Integration
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path

def check_dependencies():
    """檢查必要的依賴項"""
    print("🔍 檢查系統依賴項...")
    
    required_packages = ['fastapi', 'uvicorn', 'pandas', 'yfinance', 'pytz']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - 已安裝")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 未安裝")
    
    if missing_packages:
        print(f"\n⚠️  缺少依賴項: {', '.join(missing_packages)}")
        print("💡 請運行: uv add " + " ".join(missing_packages))
        return False
    
    return True

def check_twstock():
    """檢查台股數據源"""
    try:
        import twstock
        print("✅ twstock - 台股數據源可用")
        return True
    except ImportError:
        print("⚠️  twstock 未安裝，將使用 yfinance 作為台股數據源")
        print("💡 建議安裝: uv add twstock")
        return False

def start_api_server():
    """啟動API服務器"""
    print("\n🚀 正在啟動台股整合API服務器...")
    print("📊 新功能包括:")
    print("   • 台股搜尋與報價 (/api/taiwan/)")
    print("   • TradingView Datafeed (/api/tradingview/)")
    print("   • 市場切換 (/api/market/)")
    print("   • 統一快取系統 (/api/cache/)")
    
    # 設定環境變量
    os.environ["PYTHONPATH"] = str(Path.cwd())
    
    try:
        # 使用 uvicorn 啟動 FastAPI
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "src.api.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ]
        
        print(f"\n⚡ 執行命令: {' '.join(cmd)}")
        print("🌐 API 文檔將在 http://localhost:8000/docs 提供")
        print("📈 TradingView 整合測試: http://localhost:8000/chart/custom/2330.TW")
        
        # 等待幾秒然後打開瀏覽器
        def open_browser():
            time.sleep(3)
            print("\n🌐 正在打開瀏覽器...")
            webbrowser.open("http://localhost:8000/docs")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 啟動服務器
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  服務器已停止")
    except Exception as e:
        print(f"\n❌ 啟動失敗: {str(e)}")
        print("\n🔧 可能的解決方案:")
        print("1. 確認所有依賴項已安裝")
        print("2. 檢查端口 8000 是否被占用")
        print("3. 運行: uv run python src/api/main.py")

def show_taiwan_features():
    """顯示台股功能介紹"""
    print("\n🇹🇼 台股功能總覽:")
    print("="*60)
    
    print("\n📊 新增 API 端點:")
    print("• GET  /api/taiwan/market-overview     - 台股市場總覽")
    print("• GET  /api/taiwan/stocks/search       - 搜尋台股")
    print("• GET  /api/taiwan/stocks/{symbol}/info - 個股資訊")
    print("• GET  /api/taiwan/stocks/{symbol}/quote - 即時報價")
    print("• POST /api/taiwan/stocks/{symbol}/historical - 歷史數據")
    
    print("\n📈 TradingView 整合:")
    print("• GET  /api/tradingview/config         - Datafeed 配置")
    print("• GET  /api/tradingview/symbols        - 符號搜尋")
    print("• GET  /api/tradingview/history        - K線數據")
    
    print("\n🔄 市場切換:")
    print("• POST /api/market/switch             - 切換美股/台股")
    print("• GET  /api/market/info               - 市場狀態")
    
    print("\n💾 快取系統:")
    print("• GET  /api/cache/stats               - 快取統計")
    
    print("\n🎯 支援的台股格式:")
    print("• 上市股票: 2330.TW (台積電)")
    print("• 上櫃股票: 3481.TWO (群創)")
    print("• 自動偵測: 2330 → 2330.TW")

def show_usage_examples():
    """顯示使用範例"""
    print("\n📖 使用範例:")
    print("="*60)
    
    print("\n1️⃣ 查看台積電資訊:")
    print("   GET http://localhost:8000/api/taiwan/stocks/2330.TW/info")
    
    print("\n2️⃣ 搜尋台股:")
    print("   GET http://localhost:8000/api/taiwan/stocks/search?query=台積")
    
    print("\n3️⃣ 切換到台股市場:")
    print("   POST http://localhost:8000/api/market/switch")
    print("   Body: {\"market\": \"TW\"}")
    
    print("\n4️⃣ 查看 TradingView 圖表:")
    print("   http://localhost:8000/chart/custom/2330.TW")
    
    print("\n5️⃣ 測試 Datafeed:")
    print("   GET http://localhost:8000/api/tradingview/symbols/2330.TW")

def main():
    """主函數"""
    print("🇹🇼 台股整合交易系統啟動器")
    print("="*60)
    print("Taiwan Stock Integration for AI Trading System")
    print("Version: 2.0 with Taiwan Market Support")
    
    # 檢查依賴項
    if not check_dependencies():
        print("\n❌ 請先安裝必要的依賴項")
        return
    
    # 檢查台股數據源
    check_twstock()
    
    # 顯示功能介紹
    show_taiwan_features()
    show_usage_examples()
    
    print("\n" + "="*60)
    choice = input("🚀 是否要啟動服務器? (Y/n): ").strip().lower()
    
    if choice in ['', 'y', 'yes']:
        start_api_server()
    else:
        print("\n💡 手動啟動指令:")
        print("   uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
        print("\n📚 或使用現有啟動方式:")
        print("   python start_system.py")

if __name__ == "__main__":
    main()