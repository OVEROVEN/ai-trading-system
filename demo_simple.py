#!/usr/bin/env python3
"""
Simple demo script for the AI Trading System
"""

import requests
import json

def main():
    base_url = "http://localhost:8000"
    
    print("=== AI Trading System Demo ===")
    print()
    
    # Test 1: Health Check
    print("1. Health Check:")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print("   Status: HEALTHY")
            print(f"   AI Available: {data['services']['ai_analysis']}")
            print(f"   US Market Open: {data['market_status']['us_market_open']}")
        else:
            print("   Status: FAILED")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 2: Get Trading Signals
    print("2. Trading Signals for AAPL:")
    try:
        response = requests.get(f"{base_url}/signals/AAPL")
        if response.status_code == 200:
            data = response.json()
            print(f"   Price: ${data['current_price']:.2f}")
            print(f"   Signals: {len(data['signals'])}")
            print(f"   Sentiment: {data['overall_sentiment']}")
            
            for signal in data['signals'][:3]:
                print(f"   - {signal['type']}: {signal['description']}")
        else:
            print("   Status: FAILED")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 3: Available Symbols
    print("3. Available Symbols:")
    try:
        response = requests.get(f"{base_url}/symbols")
        if response.status_code == 200:
            data = response.json()
            print(f"   US Stocks: {', '.join(data['us_symbols'][:5])}")
            print(f"   Taiwan Stocks: {', '.join(data['taiwan_symbols'][:3])}")
        else:
            print("   Status: FAILED")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 4: Multiple Stock Signals
    print("4. Multiple Stock Analysis:")
    symbols = ["AAPL", "TSLA", "GOOGL"]
    
    for symbol in symbols:
        try:
            response = requests.get(f"{base_url}/signals/{symbol}")
            if response.status_code == 200:
                data = response.json()
                print(f"   {symbol}: ${data['current_price']:.2f} ({data['overall_sentiment']})")
            else:
                print(f"   {symbol}: FAILED")
        except Exception as e:
            print(f"   {symbol}: Error - {e}")
    
    print()
    
    # Test 5: Pattern Recognition
    print("5. Pattern Recognition for AAPL:")
    try:
        response = requests.get(f"{base_url}/patterns/AAPL")
        if response.status_code == 200:
            data = response.json()
            print("   Pattern analysis completed")
            for pattern_type, patterns in data['patterns'].items():
                if patterns:
                    print(f"   - {pattern_type}: {len(patterns)} detected")
        else:
            print("   Status: FAILED")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    print("=== Demo Complete ===")
    print()
    print("Your AI Trading System is working!")
    print()
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print()
    print("Example API calls:")
    print("  curl http://localhost:8000/signals/AAPL")
    print("  curl http://localhost:8000/patterns/TSLA")
    print("  curl http://localhost:8000/symbols")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server")
        print("Make sure the server is running on port 8000")
    except Exception as e:
        print(f"ERROR: {e}")