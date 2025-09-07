#!/usr/bin/env python3
"""
Demo script for the AI Trading System
Shows the working features and API endpoints
"""

import requests
import json
import time

def test_api():
    """Test the working API endpoints."""
    base_url = "http://localhost:8000"
    
    print("=== AI Trading System Demo ===\n")
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    response = requests.get(f"{base_url}/health")
    if response.status_code == 200:
        data = response.json()
        print("   OK - System is healthy!")
        print(f"   - AI Analysis: {'Available' if data['services']['ai_analysis'] else 'Unavailable'}")
        print(f"   - US Market Open: {data['market_status']['us_market_open']}")
        print(f"   - TW Market Open: {data['market_status']['tw_market_open']}")
    else:
        print("   ERROR - Health check failed")
        return
    
    print()
    
    # Test 2: Available Symbols
    print("2. Getting Available Symbols...")
    response = requests.get(f"{base_url}/symbols")
    if response.status_code == 200:
        data = response.json()
        print("   ✓ Available symbols:")
        print(f"   - US: {', '.join(data['us_symbols'][:5])}...")
        print(f"   - Taiwan: {', '.join(data['taiwan_symbols'][:3])}...")
    else:
        print("   ✗ Failed to get symbols")
    
    print()
    
    # Test 3: Trading Signals
    symbols_to_test = ["AAPL", "TSLA", "GOOGL"]
    
    for symbol in symbols_to_test:
        print(f"3. Testing Trading Signals for {symbol}...")
        response = requests.get(f"{base_url}/signals/{symbol}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ {symbol} Analysis:")
            print(f"   - Current Price: ${data['current_price']:.2f}")
            print(f"   - Signals Found: {len(data['signals'])}")
            print(f"   - Overall Sentiment: {data['overall_sentiment']}")
            
            # Show signals if any
            for signal in data['signals'][:2]:  # Show first 2 signals
                print(f"     • {signal['type']} signal from {signal['source']}: {signal['description']}")
        else:
            print(f"   ✗ Failed to get signals for {symbol}")
        
        print()
        time.sleep(1)  # Be nice to the API
    
    # Test 4: Pattern Recognition (if working)
    print("4. Testing Pattern Recognition...")
    response = requests.get(f"{base_url}/patterns/AAPL")
    if response.status_code == 200:
        data = response.json()
        print("   ✓ Pattern analysis completed:")
        for pattern_type, patterns in data['patterns'].items():
            if patterns:
                print(f"   - {pattern_type.replace('_', ' ').title()}: {len(patterns)} detected")
    else:
        print("   ✗ Pattern recognition failed")
    
    print()
    
    # Test 5: Real-time Data Fetching Demo
    print("5. Real-time Data Demonstration...")
    from src.data_fetcher.us_stocks import USStockDataFetcher
    
    fetcher = USStockDataFetcher()
    
    for symbol in ["AAPL", "TSLA"]:
        quote = fetcher.get_real_time_quote(symbol)
        if quote:
            print(f"   ✓ {symbol} Real-time Quote:")
            print(f"     Price: ${quote.price:.2f}")
            print(f"     Change: {quote.change:+.2f} ({quote.change_percent:+.2f}%)")
            print(f"     Volume: {quote.volume:,}")
        else:
            print(f"   ✗ Failed to get real-time quote for {symbol}")
        print()
    
    # Test 6: Technical Indicators Demo
    print("6. Technical Indicators Demonstration...")
    from src.analysis.technical_indicators import IndicatorAnalyzer
    
    analyzer = IndicatorAnalyzer()
    data = fetcher.fetch_historical_data("AAPL", period="3mo")
    
    if not data.empty:
        data_with_indicators = analyzer.calculate_all_indicators(data)
        latest = data_with_indicators.iloc[-1]
        
        print("   ✓ AAPL Technical Indicators:")
        if not pd.isna(latest.get('rsi')):
            print(f"     RSI: {latest['rsi']:.2f}")
        if not pd.isna(latest.get('macd')):
            print(f"     MACD: {latest['macd']:.4f}")
        if not pd.isna(latest.get('sma_20')):
            print(f"     SMA(20): ${latest['sma_20']:.2f}")
        if not pd.isna(latest.get('bb_upper')):
            print(f"     Bollinger Upper: ${latest['bb_upper']:.2f}")
            print(f"     Bollinger Lower: ${latest['bb_lower']:.2f}")
    
    print()
    
    # Test 7: AI Analysis Demo (if available)
    print("7. AI Analysis Demonstration...")
    try:
        from src.analysis.ai_analyzer import OpenAIAnalyzer
        import pandas as pd
        import numpy as np
        
        ai_analyzer = OpenAIAnalyzer()
        
        # Create test data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        sample_data = pd.DataFrame({
            'close': 150 + np.cumsum(np.random.randn(30) * 0.5),
            'volume': np.random.randint(1000000, 5000000, 30)
        }, index=dates)
        
        # Test AI analysis
        indicators = {'rsi': 65, 'macd': 0.8}
        patterns = {'breakouts': []}
        
        print("   Running AI analysis...")
        import asyncio
        result = asyncio.run(ai_analyzer.analyze_technical_data(
            'DEMO', sample_data, indicators, patterns, context="Demo analysis"
        ))
        
        print("   ✓ AI Analysis Results:")
        print(f"     Recommendation: {result.recommendation}")
        print(f"     Confidence: {result.confidence:.2f}")
        print(f"     Reasoning: {result.reasoning[:100]}...")
        
    except Exception as e:
        print(f"   ⚠ AI analysis not available: {str(e)}")
    
    print("\n=== Demo Complete ===")
    print("\nYour AI Trading System is working! 🎉")
    print("\nNext steps:")
    print("1. Open http://localhost:8000/docs to explore the full API")
    print("2. Try the WebSocket endpoint for real-time streaming")
    print("3. Customize the indicators and patterns in the code")
    print("4. Add your own trading strategies")

if __name__ == "__main__":
    try:
        import pandas as pd
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print("Make sure the server is running:")
        print("python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload")
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")