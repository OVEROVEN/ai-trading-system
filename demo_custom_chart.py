#!/usr/bin/env python3
"""
定制TradingView圖表示範
包含K線、成交量、RSI和AI建議的專業圖表
"""

import webbrowser
import requests
import time
from urllib.parse import urlencode

def demo_custom_chart():
    """演示定制TradingView圖表功能"""
    
    BASE_URL = "http://localhost:8000"
    
    # 檢查API連接
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        if response.status_code != 200:
            print("❌ 無法連接到API服務器！")
            print("請先啟動API服務器：python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
            return
    except Exception as e:
        print("❌ API服務器連接失敗！")
        print("請確保API服務器正在運行")
        return
    
    print("🚀 定制TradingView圖表演示")
    print("=" * 50)
    
    # 推薦的股票列表
    recommended_stocks = {
        "1": ("AAPL", "蘋果公司"),
        "2": ("TSLA", "特斯拉"),
        "3": ("GOOGL", "Alphabet (Google)"),
        "4": ("MSFT", "微軟"),
        "5": ("NVDA", "NVIDIA"),
        "6": ("2330.TW", "台積電"),
        "7": ("SPY", "標普500 ETF"),
        "8": ("QQQ", "納斯達克100 ETF")
    }
    
    print("\n📊 選擇要分析的股票:")
    for key, (symbol, name) in recommended_stocks.items():
        print(f"  {key}. {symbol} - {name}")
    print("  9. 自定義輸入")
    
    choice = input("\n請選擇 (1-9): ").strip()
    
    if choice in recommended_stocks:
        symbol = recommended_stocks[choice][0]
    elif choice == "9":
        symbol = input("請輸入股票代號: ").strip().upper()
    else:
        print("無效選擇，使用默認股票 AAPL")
        symbol = "AAPL"
    
    print(f"\n🎯 分析股票: {symbol}")
    
    # 選擇主題
    print("\n🎨 選擇主題:")
    print("  1. 深色主題 (推薦)")
    print("  2. 淺色主題")
    
    theme_choice = input("請選擇主題 (1-2，默認1): ").strip()
    theme = "dark" if theme_choice != "2" else "light"
    
    # 選擇策略
    print("\n⚙️ 選擇交易策略:")
    print("  1. 形態交易策略 (推薦)")
    print("  2. RSI + K線 + 成交量策略")
    
    strategy_choice = input("請選擇策略 (1-2，默認1): ").strip()
    strategy = "pattern_trading" if strategy_choice != "2" else "rsi_volume"
    
    # 是否包含AI建議
    print("\n🤖 是否包含AI建議?")
    print("  1. 是 (推薦，需要OpenAI API Key)")
    print("  2. 否 (只顯示技術指標)")
    
    ai_choice = input("請選擇 (1-2，默認1): ").strip()
    include_ai = ai_choice != "2"
    
    # 構建URL參數
    params = {
        'theme': theme,
        'strategy': strategy,
        'include_ai': str(include_ai).lower()
    }
    
    chart_url = f"{BASE_URL}/chart/custom/{symbol}?{urlencode(params)}"
    
    print("\n🔗 生成的圖表URL:")
    print(chart_url)
    
    print("\n⏳ 正在打開定制TradingView圖表...")
    print("📊 圖表特色:")
    print("  ✅ 真實TradingView K線圖")
    print("  📊 成交量指標")
    print("  📈 RSI技術指標")
    print("  🤖 AI買賣區間建議")
    print("  ⚙️ 交易策略資訊")
    print("  📱 響應式設計")
    
    # 打開瀏覽器
    try:
        webbrowser.open(chart_url)
        print(f"\n✅ 已在瀏覽器中打開 {symbol} 的定制圖表！")
        
        print("\n💡 使用提示:")
        print("  • 左側是專業TradingView圖表")
        print("  • 右側包含股票數據、AI建議和策略資訊")
        print("  • 點擊刷新按鈕可更新最新數據")
        print("  • 支援響應式設計，適用於各種螢幕")
        
        print("\n🔄 要查看其他股票嗎? (y/n): ", end="")
        if input().lower() == 'y':
            demo_custom_chart()
            
    except Exception as e:
        print(f"❌ 打開瀏覽器失敗: {e}")
        print(f"請手動訪問: {chart_url}")

def test_api_endpoints():
    """測試相關的API端點"""
    
    BASE_URL = "http://localhost:8000"
    test_symbol = "AAPL"
    
    print("🧪 測試API端點...")
    
    endpoints_to_test = [
        f"/health",
        f"/symbols", 
        f"/analyze/{test_symbol}",
        f"/chart/custom/{test_symbol}"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            url = f"{BASE_URL}{endpoint}"
            if "chart" in endpoint:
                # 圖表端點返回HTML，只檢查狀態碼
                response = requests.get(url, timeout=10)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"{status} {endpoint} - 狀態碼: {response.status_code}")
            else:
                response = requests.get(url, timeout=10)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"{status} {endpoint} - 狀態碼: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - 錯誤: {str(e)}")

if __name__ == "__main__":
    print("🎯 定制TradingView圖表系統")
    print("=" * 50)
    
    print("\n選擇操作:")
    print("1. 演示定制圖表")
    print("2. 測試API端點")
    print("3. 直接訪問AAPL圖表")
    
    choice = input("\n請選擇 (1-3): ").strip()
    
    if choice == "1":
        demo_custom_chart()
    elif choice == "2":
        test_api_endpoints()
    elif choice == "3":
        url = "http://localhost:8000/chart/custom/AAPL?theme=dark&strategy=pattern_trading&include_ai=true"
        print(f"\n🔗 直接訪問URL: {url}")
        webbrowser.open(url)
        print("✅ 已在瀏覽器中打開AAPL定制圖表！")
    else:
        print("無效選擇")