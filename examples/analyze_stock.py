#!/usr/bin/env python3
"""
股票技術分析範例
"""
import requests
import json
from datetime import datetime

def analyze_stock(symbol, period="3mo", include_ai=True):
    """
    分析股票
    
    Args:
        symbol: 股票代號 (如 'AAPL', '2330.TW')
        period: 分析期間 ('1d', '5d', '1mo', '3mo', '6mo', '1y')
        include_ai: 是否包含 AI 分析
    """
    
    url = f"http://localhost:8000/analyze/{symbol}"
    
    payload = {
        "symbol": symbol,
        "period": period,
        "include_ai": include_ai,
        "include_patterns": True
    }
    
    try:
        print(f"📊 分析 {symbol}...")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n🎯 {data['symbol']} 技術分析結果")
            print(f"📅 時間: {data['timestamp']}")
            print(f"💰 當前價格: ${data['current_price']:.2f}")
            
            # 技術指標
            indicators = data['technical_indicators']
            print(f"\n📈 技術指標:")
            print(f"  RSI: {indicators.get('rsi', 'N/A'):.2f}")
            print(f"  MACD: {indicators.get('macd', 'N/A'):.2f}")
            print(f"  布林帶上軌: ${indicators.get('bb_upper', 'N/A'):.2f}")
            print(f"  布林帶下軌: ${indicators.get('bb_lower', 'N/A'):.2f}")
            print(f"  20日均線: ${indicators.get('sma_20', 'N/A'):.2f}")
            print(f"  50日均線: ${indicators.get('sma_50', 'N/A'):.2f}")
            
            # 交易訊號
            signals = data['signals']
            print(f"\n📡 交易訊號:")
            for signal in signals:
                print(f"  {signal['signal_type']}: {signal['reasoning']} (信心度: {signal['confidence']:.1f})")
            
            # 模式識別
            patterns = data['patterns']
            print(f"\n🔍 檢測到的技術型態:")
            for pattern_type, pattern_list in patterns.items():
                if pattern_list:
                    print(f"  {pattern_type}: {len(pattern_list)} 個型態")
            
            # AI 分析
            if include_ai and data.get('ai_analysis'):
                ai = data['ai_analysis']
                if 'error' not in ai:
                    print(f"\n🤖 AI 分析:")
                    print(f"  建議: {ai.get('recommendation', 'N/A')}")
                    print(f"  信心度: {ai.get('confidence', 'N/A'):.2f}")
                    print(f"  理由: {ai.get('reasoning', 'N/A')}")
                    if ai.get('price_target'):
                        print(f"  目標價: ${ai['price_target']:.2f}")
                else:
                    print(f"\n🤖 AI 分析: {ai['error']}")
            
        else:
            print(f"❌ 分析失敗: {response.text}")
            
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")

def main():
    """主程式"""
    print("🎯 股票技術分析範例")
    
    # 分析美股
    analyze_stock("AAPL", period="3mo", include_ai=False)
    
    print("\n" + "="*50)
    
    # 分析台股
    analyze_stock("2330.TW", period="1mo", include_ai=False)

if __name__ == "__main__":
    main()