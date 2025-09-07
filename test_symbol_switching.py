#!/usr/bin/env python3
"""
測試符號切換和右側數據更新功能
Test Symbol Switching and Right Panel Data Updates
"""

import requests
import json
import time

def test_api_endpoints():
    """測試API端點是否正常工作"""
    base_url = "http://localhost:8000"
    
    test_symbols = ["AAPL", "2330.TW", "TSLA", "2317.TW"]
    
    print("Testing API Endpoints...")
    print("="*50)
    
    for symbol in test_symbols:
        print(f"\nTesting symbol: {symbol}")
        
        # 測試股票數據端點
        try:
            response = requests.get(f"{base_url}/api/stock-data/{symbol}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 股票數據: 價格 ${data.get('current_price', 'N/A')}, 漲跌 {data.get('change_percent', 'N/A')}%")
            else:
                print(f"❌ 股票數據失敗: {response.status_code}")
        except Exception as e:
            print(f"❌ 股票數據錯誤: {str(e)}")
        
        # 測試AI建議端點
        try:
            response = requests.get(f"{base_url}/api/ai-recommendations/{symbol}")
            if response.status_code == 200:
                data = response.json()
                recommendations = []
                if 'buy_zone' in data:
                    recommendations.append("買入建議")
                if 'sell_zone' in data:
                    recommendations.append("賣出建議") 
                if 'hold_recommendation' in data:
                    recommendations.append("持有建議")
                print(f"✅ AI建議: {', '.join(recommendations) if recommendations else '無建議'}")
            else:
                print(f"❌ AI建議失敗: {response.status_code}")
        except Exception as e:
            print(f"❌ AI建議錯誤: {str(e)}")
        
        time.sleep(0.5)  # 避免請求過快

def test_market_switching():
    """測試市場切換功能"""
    base_url = "http://localhost:8000"
    
    print("\n🔄 測試市場切換...")
    print("="*50)
    
    markets = ["US", "TW", "AUTO"]
    
    for market in markets:
        try:
            response = requests.post(f"{base_url}/api/market/switch", 
                                   json={"market": market})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 切換到 {market}: {data.get('current_market', 'Unknown')}")
            else:
                print(f"❌ 市場切換失敗: {response.status_code}")
        except Exception as e:
            print(f"❌ 市場切換錯誤: {str(e)}")
        
        time.sleep(0.5)

def test_taiwan_specific_endpoints():
    """測試台股專用端點"""
    base_url = "http://localhost:8000"
    
    print("\n🇹🇼 測試台股專用端點...")
    print("="*50)
    
    # 測試市場總覽
    try:
        response = requests.get(f"{base_url}/api/taiwan/market-overview")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 市場總覽: {data.get('market_status', 'Unknown')}")
        else:
            print(f"❌ 市場總覽失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ 市場總覽錯誤: {str(e)}")
    
    # 測試搜尋功能
    try:
        response = requests.get(f"{base_url}/api/taiwan/stocks/search?query=台積")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 台股搜尋: 找到 {len(data)} 筆結果")
        else:
            print(f"❌ 台股搜尋失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ 台股搜尋錯誤: {str(e)}")
    
    # 測試個股資訊
    try:
        response = requests.get(f"{base_url}/api/taiwan/stocks/2330.TW/info")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 個股資訊: {data.get('name', 'Unknown')}")
        else:
            print(f"❌ 個股資訊失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ 個股資訊錯誤: {str(e)}")

def test_cache_system():
    """測試快取系統"""
    base_url = "http://localhost:8000"
    
    print("\n💾 測試快取系統...")
    print("="*50)
    
    try:
        response = requests.get(f"{base_url}/api/cache/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 快取統計:")
            for key, value in data.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ 快取統計失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ 快取統計錯誤: {str(e)}")

def generate_test_instructions():
    """生成測試說明"""
    print("\n📖 手動測試指南:")
    print("="*50)
    
    print("\n1️⃣ 訪問圖表頁面:")
    print("   http://localhost:8000/chart/custom/2330.TW")
    
    print("\n2️⃣ 打開瀏覽器開發者工具 (F12)")
    print("   - 切換到 Console 標籤")
    print("   - 查看是否有錯誤訊息")
    
    print("\n3️⃣ 測試符號切換:")
    print("   - 點擊不同的股票按鈕 (AAPL, TSLA, 台積電等)")
    print("   - 觀察右側數據是否更新")
    print("   - 在Console中輸入: window.debugInfo()")
    
    print("\n4️⃣ 測試手動輸入:")
    print("   - 在輸入框中輸入: GOOGL")
    print("   - 點擊「查看」按鈕")
    print("   - 觀察數據更新情況")
    
    print("\n5️⃣ 檢查Console輸出:")
    print("   - 查看「Loading stock data for:」訊息")
    print("   - 查看「Stock data received:」訊息")
    print("   - 查看任何錯誤訊息")
    
    print("\n🔧 除錯提示:")
    print("   - 如果右側不更新，檢查Console是否有紅色錯誤")
    print("   - 確認API端點回應正常")
    print("   - 確認JavaScript函數正確執行")

def main():
    """主測試函數"""
    print("Taiwan Stock Integration System - Symbol Switching Test")
    print("="*60)
    
    # 檢查服務器是否運行
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ 服務器正常運行")
        else:
            print("❌ 服務器回應異常")
            return
    except Exception as e:
        print(f"❌ 無法連接到服務器: {str(e)}")
        print("💡 請確認服務器已啟動: uv run python start_taiwan_system.py")
        return
    
    # 執行測試
    test_api_endpoints()
    test_market_switching()
    test_taiwan_specific_endpoints()
    test_cache_system()
    
    # 生成手動測試指南
    generate_test_instructions()
    
    print("\n🎉 自動測試完成！")
    print("請按照上面的手動測試指南進行進一步測試。")

if __name__ == "__main__":
    main()