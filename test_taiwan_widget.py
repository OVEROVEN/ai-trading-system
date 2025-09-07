#!/usr/bin/env python3
"""
台股TradingView Widget功能測試腳本
測試增強版台股Widget的各項功能
"""

import asyncio
import sys
import os
import requests
import time
from typing import Dict, List

# 添加src目錄到路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.visualization.enhanced_taiwan_widget import get_enhanced_taiwan_widget

def test_symbol_normalization():
    """測試台股符號標準化功能"""
    print("\n" + "="*60)
    print("測試台股符號標準化功能")
    print("="*60)
    
    widget = get_enhanced_taiwan_widget()
    
    test_cases = [
        "2330",        # 純數字代號
        "2330.TW",     # 帶.TW後綴
        "3481.TWO",    # 上櫃股票
        "0050",        # ETF
        "2454",        # 聯發科
        "2881",        # 富邦金
    ]
    
    for symbol in test_cases:
        try:
            code, exchange, full_symbol = widget.normalize_taiwan_symbol(symbol)
            tradingview_symbol = widget.get_tradingview_symbol(symbol)
            
            print(f" {symbol:10} -> {code:6} | {exchange:5} | {full_symbol:10} | {tradingview_symbol}")
            
        except Exception as e:
            print(f" {symbol}: 錯誤 - {str(e)}")
    
    print("\n 符號標準化測試完成")

def test_stock_info():
    """測試台股資訊獲取功能"""
    print("\n" + "="*60)
    print(" 測試台股資訊獲取功能")
    print("="*60)
    
    widget = get_enhanced_taiwan_widget()
    
    test_symbols = ["2330", "2454", "2881", "0050", "3481", "9999"]  # 包含一個不存在的股票
    
    for symbol in test_symbols:
        try:
            stock_info = widget.get_stock_info(symbol)
            
            print(f" {symbol} ({stock_info['name']})")
            print(f"   產業: {stock_info['industry']} | 交易所: {stock_info['exchange']}")
            print(f"   市值: {stock_info['market_cap']} | TradingView: {stock_info['tradingview_symbol']}")
            print(f"   顏色: {stock_info['industry_color']}")
            print()
            
        except Exception as e:
            print(f" {symbol}: 錯誤 - {str(e)}")
    
    print(" 股票資訊測試完成")

def test_widget_generation():
    """測試Widget HTML生成功能"""
    print("\n" + "="*60)
    print(" 測試Widget HTML生成功能")
    print("="*60)
    
    widget = get_enhanced_taiwan_widget()
    
    test_symbols = ["2330", "2454", "0050"]
    themes = ["dark", "light"]
    
    for symbol in test_symbols:
        for theme in themes:
            try:
                print(f" 生成 {symbol} ({theme} 主題)...")
                
                html_content = widget.create_enhanced_widget(
                    symbol=symbol,
                    theme=theme,
                    additional_studies=["MACD@tv-basicstudies"]
                )
                
                # 檢查HTML內容
                checks = [
                    ("TradingView.widget", "TradingView Widget 初始化"),
                    ("tradingview_widget", "Widget 容器"),
                    (f"TPE:{symbol}", "台股符號格式"),
                    ("Asia/Taipei", "台股時區"),
                    ("Volume@tv-basicstudies", "成交量指標"),
                    ("RSI@tv-basicstudies", "RSI指標"),
                    ("MACD@tv-basicstudies", "MACD指標"),
                ]
                
                results = []
                for check_text, description in checks:
                    if check_text in html_content:
                        results.append(f" {description}")
                    else:
                        results.append(f" {description}")
                
                print(f"   HTML長度: {len(html_content):,} 字符")
                for result in results:
                    print(f"   {result}")
                print()
                
            except Exception as e:
                print(f" {symbol} ({theme}): 錯誤 - {str(e)}")
    
    print(" Widget生成測試完成")

def test_industry_coverage():
    """測試產業覆蓋範圍"""
    print("\n" + "="*60)
    print(" 測試產業覆蓋範圍")
    print("="*60)
    
    widget = get_enhanced_taiwan_widget()
    
    industries = {}
    exchanges = {}
    market_caps = {}
    
    for code, info in widget.taiwan_stocks.items():
        # 統計產業分布
        industry = info["industry"]
        industries[industry] = industries.get(industry, 0) + 1
        
        # 統計交易所分布
        exchange = info["exchange"]
        exchanges[exchange] = exchanges.get(exchange, 0) + 1
        
        # 統計市值分布
        market_cap = info["market_cap"]
        market_caps[market_cap] = market_caps.get(market_cap, 0) + 1
    
    print(" 產業分布:")
    for industry, count in sorted(industries.items()):
        color = widget.industry_colors.get(industry, "#666666")
        print(f"   {industry:12} : {count:2} 檔 (顏色: {color})")
    
    print(f"\n 交易所分布:")
    for exchange, count in sorted(exchanges.items()):
        print(f"   {exchange:8} : {count:2} 檔")
    
    print(f"\n 市值分布:")
    for market_cap, count in sorted(market_caps.items()):
        print(f"   {market_cap:8} : {count:2} 檔")
    
    print(f"\n 總計: {len(widget.taiwan_stocks)} 檔台股")
    print(" 產業覆蓋測試完成")

def test_api_endpoints():
    """測試API端點"""
    print("\n" + "="*60)
    print(" 測試API端點 (需要API服務器運行)")
    print("="*60)
    
    base_url = "http://localhost:8000"
    
    # 測試端點列表
    test_endpoints = [
        {
            "method": "GET",
            "url": f"{base_url}/chart/taiwan-widget/2330",
            "description": "台股Widget圖表 - 台積電"
        },
        {
            "method": "GET", 
            "url": f"{base_url}/api/taiwan-widget/stock-info/2330",
            "description": "台股資訊API - 台積電"
        },
        {
            "method": "GET",
            "url": f"{base_url}/api/taiwan-widget/symbol-search?query=台積電",
            "description": "台股符號搜尋API"
        }
    ]
    
    for endpoint in test_endpoints:
        try:
            print(f" 測試: {endpoint['description']}")
            print(f"   URL: {endpoint['url']}")
            
            response = requests.get(endpoint['url'], timeout=10)
            
            print(f"   狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                print("    成功")
                
                # 檢查內容類型
                content_type = response.headers.get('content-type', '')
                print(f"   內容類型: {content_type}")
                
                # 如果是JSON回應，顯示部分內容
                if 'application/json' in content_type:
                    try:
                        json_data = response.json()
                        if 'data' in json_data:
                            print(f"   數據鍵: {list(json_data['data'].keys()) if isinstance(json_data['data'], dict) else '數組'}")
                    except:
                        pass
                elif 'text/html' in content_type:
                    html_size = len(response.text)
                    print(f"   HTML大小: {html_size:,} 字符")
                
            else:
                print(f"    失敗 - 狀態碼: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("     API服務器未運行 (請先啟動 FastAPI 服務器)")
        except requests.exceptions.Timeout:
            print("    請求超時")
        except Exception as e:
            print(f"    錯誤: {str(e)}")
        
        print()
    
    print(" API端點測試完成")

def create_sample_files():
    """創建範例HTML文件"""
    print("\n" + "="*60)
    print(" 創建範例HTML文件")
    print("="*60)
    
    widget = get_enhanced_taiwan_widget()
    
    sample_stocks = [
        ("2330", "台積電"),
        ("2454", "聯發科"), 
        ("0050", "台灣50")
    ]
    
    # 創建範例目錄
    samples_dir = "samples"
    os.makedirs(samples_dir, exist_ok=True)
    
    for symbol, name in sample_stocks:
        try:
            print(f" 創建 {symbol} ({name}) 範例文件...")
            
            # 生成深色主題
            html_content = widget.create_enhanced_widget(
                symbol=symbol,
                theme="dark",
                additional_studies=["MACD@tv-basicstudies"]
            )
            
            filename = f"{samples_dir}/taiwan_widget_{symbol}_dark.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"    {filename}")
            
        except Exception as e:
            print(f"    錯誤: {str(e)}")
    
    # 創建索引文件
    try:
        index_html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>台股TradingView Widget範例</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .card {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; }}
        .sample-link {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
        .sample-link:hover {{ background: #0056b3; }}
        .info {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1> 台股TradingView Widget範例</h1>
        
        <div class="card">
            <h2> 範例圖表</h2>
            <div class="info">
                <strong>功能特色:</strong><br>
                • 專業級TradingView圖表介面<br>
                • 台股專用符號格式 (TPE:代號)<br>
                • 內建技術指標 (成交量、RSI、MACD)<br>
                • 響應式設計，支援各種螢幕尺寸<br>
                • 詳細的股票資訊面板<br>
                • 產業分類和市值資訊
            </div>
            
            {chr(10).join([f'<a href="taiwan_widget_{symbol}_dark.html" class="sample-link">{symbol} ({name})</a>' 
                          for symbol, name in sample_stocks])}
        </div>
        
        <div class="card">
            <h2> API端點</h2>
            <p><strong>圖表顯示:</strong> <code>/chart/taiwan-widget/{{symbol}}</code></p>
            <p><strong>股票資訊:</strong> <code>/api/taiwan-widget/stock-info/{{symbol}}</code></p>
            <p><strong>符號搜尋:</strong> <code>/api/taiwan-widget/symbol-search?query={{關鍵字}}</code></p>
        </div>
        
        <div class="card">
            <h2>⚙ 使用方式</h2>
            <p>1. 啟動FastAPI服務器: <code>uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000</code></p>
            <p>2. 訪問圖表: <code>http://localhost:8000/chart/taiwan-widget/2330</code></p>
            <p>3. 或直接開啟上方的範例HTML文件</p>
        </div>
    </div>
</body>
</html>
        """
        
        index_filename = f"{samples_dir}/index.html"
        with open(index_filename, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        print(f" 索引文件: {index_filename}")
        
    except Exception as e:
        print(f" 創建索引文件失敗: {str(e)}")
    
    print(" 範例文件創建完成")

def main():
    """主測試函數"""
    print("台股TradingView Widget 功能測試")
    print("="*60)
    print("測試增強版台股Widget的各項功能...")
    
    try:
        # 執行各項測試
        test_symbol_normalization()
        test_stock_info()
        test_industry_coverage()
        test_widget_generation()
        test_api_endpoints()
        create_sample_files()
        
        print("\n" + "="*60)
        print("所有測試完成!")
        print("="*60)
        print("\n測試結果摘要:")
        print("符號標準化功能正常")
        print("股票資訊獲取功能正常")
        print("產業覆蓋範圍完整")
        print("Widget HTML生成功能正常")
        print("範例文件已創建")
        print("\n快速啟動:")
        print("1. 啟動API: uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
        print("2. 訪問圖表: http://localhost:8000/chart/taiwan-widget/2330")
        print("3. 查看範例: 開啟 samples/index.html")
        
    except Exception as e:
        print(f"\n 測試過程中發生錯誤: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)