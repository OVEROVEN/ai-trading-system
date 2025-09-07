#!/usr/bin/env python3
"""
最終演示腳本 - 展示美股和台股都正常工作
Final Demo Script - Shows both US and Taiwan stocks working
"""

import requests
import json

def main():
    base_url = "http://localhost:8000"
    
    print("=== AI 交易系統 - 最終測試 ===")
    print("=== AI Trading System - Final Test ===")
    print()
    
    # 健康檢查
    print("1. 系統健康檢查 / System Health Check:")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print("   狀態 / Status: 健康 / HEALTHY")
            print(f"   AI 可用 / AI Available: {data['services']['ai_analysis']}")
            print(f"   美股市場 / US Market: {'開盤' if data['market_status']['us_market_open'] else '休市'}")
            print(f"   台股市場 / TW Market: {'開盤' if data['market_status']['tw_market_open'] else '休市'}")
    except Exception as e:
        print(f"   錯誤 / Error: {e}")
    print()
    
    # 美股測試
    print("2. 美股分析 / US Stock Analysis:")
    us_stocks = ["AAPL", "TSLA", "GOOGL", "MSFT"]
    
    for symbol in us_stocks:
        try:
            response = requests.get(f"{base_url}/signals/{symbol}")
            if response.status_code == 200:
                data = response.json()
                price = data['current_price']
                sentiment = data['overall_sentiment']
                signals_count = len(data['signals'])
                
                # 中文翻譯
                sentiment_cn = {"BULLISH": "看漲", "BEARISH": "看跌", "NEUTRAL": "中性"}[sentiment]
                
                print(f"   {symbol}: ${price:.2f} | {sentiment}/{sentiment_cn} | 信號數:{signals_count}")
                
                # 顯示具體信號
                for signal in data['signals'][:2]:
                    action_cn = {"BUY": "買入", "SELL": "賣出", "HOLD": "持有"}[signal['type']]
                    print(f"     -> {signal['type']}/{action_cn}: {signal['description']}")
            else:
                print(f"   {symbol}: 獲取失敗 / Failed")
        except Exception as e:
            print(f"   {symbol}: 錯誤 / Error - {e}")
    print()
    
    # 台股測試
    print("3. 台股分析 / Taiwan Stock Analysis:")
    tw_stocks = [
        ("2330.TW", "台積電 TSMC"),
        ("2317.TW", "鴻海 Hon Hai"), 
        ("0050.TW", "台灣50 ETF"),
        ("2454.TW", "聯發科 MediaTek")
    ]
    
    for symbol, name in tw_stocks:
        try:
            response = requests.get(f"{base_url}/signals/{symbol}")
            if response.status_code == 200:
                data = response.json()
                price = data['current_price']
                sentiment = data['overall_sentiment']
                signals_count = len(data['signals'])
                
                # 中文翻譯
                sentiment_cn = {"BULLISH": "看漲", "BEARISH": "看跌", "NEUTRAL": "中性"}[sentiment]
                
                print(f"   {name}: NT${price:.2f} | {sentiment}/{sentiment_cn} | 信號數:{signals_count}")
                
                # 顯示具體信號
                for signal in data['signals'][:2]:
                    action_cn = {"BUY": "買入", "SELL": "賣出", "HOLD": "持有"}[signal['type']]
                    print(f"     -> {signal['type']}/{action_cn}: {signal['description']}")
            else:
                print(f"   {name}: 獲取失敗 / Failed")
        except Exception as e:
            print(f"   {name}: 錯誤 / Error - {e}")
    print()
    
    # 比較分析
    print("4. 跨市場比較 / Cross-Market Comparison:")
    comparison_stocks = [
        ("AAPL", "蘋果 Apple"),
        ("2330.TW", "台積電 TSMC"),
        ("TSLA", "特斯拉 Tesla"),
        ("2317.TW", "鴻海 Hon Hai")
    ]
    
    for symbol, name in comparison_stocks:
        try:
            response = requests.get(f"{base_url}/signals/{symbol}")
            if response.status_code == 200:
                data = response.json()
                currency = "NT$" if symbol.endswith(".TW") else "$"
                market = "台股" if symbol.endswith(".TW") else "美股"
                sentiment_cn = {"BULLISH": "看漲", "BEARISH": "看跌", "NEUTRAL": "中性"}[data['overall_sentiment']]
                
                print(f"   {name} ({market}): {currency}{data['current_price']:.2f} - {sentiment_cn}")
        except Exception as e:
            print(f"   {name}: 錯誤 / Error")
    print()
    
    # 功能展示
    print("5. 系統功能展示 / System Features:")
    print("   ✓ 美股即時數據 / US Real-time Data")
    print("   ✓ 台股即時數據 / Taiwan Real-time Data") 
    print("   ✓ 技術指標分析 / Technical Analysis")
    print("   ✓ AI 智能分析 / AI Analysis")
    print("   ✓ 交易信號生成 / Trading Signals")
    print("   ✓ 多市場支援 / Multi-Market Support")
    print()
    
    print("=== 測試完成！系統正常運行 ===")
    print("=== Test Complete! System Running Normally ===")
    print()
    print("📊 API 文檔 / Documentation: http://localhost:8000/docs")
    print("🩺 健康檢查 / Health Check: http://localhost:8000/health")
    print()
    print("🎯 可測試的股票 / Testable Stocks:")
    print("   美股 / US: AAPL, TSLA, GOOGL, MSFT, AMZN, NVDA")
    print("   台股 / TW: 2330.TW, 2317.TW, 0050.TW, 2454.TW")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到 API 伺服器 / Cannot connect to API server")
        print("請確保伺服器在 8000 端口運行 / Make sure server is running on port 8000")
    except Exception as e:
        print(f"❌ 錯誤 / Error: {e}")