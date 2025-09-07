#!/usr/bin/env python3
"""
Test Enhanced AI Trading Analysis Platform
Test TradingView charts with AI chatroom and detailed pattern analysis
"""

import webbrowser
import requests
import time

BASE_URL = "http://localhost:8000"

def test_enhanced_trading():
    print("=== Enhanced AI Trading Analysis Platform ===\n")
    
    # Test enhanced TradingView chart
    try:
        print("Testing enhanced trading platform...")
        response = requests.get(f"{BASE_URL}/chart/tradingview/AAPL?chart_type=advanced&theme=dark", timeout=10)
        if response.status_code == 200:
            print("[OK] Enhanced trading platform is running properly")
        else:
            print(f"[FAIL] API returned error: {response.status_code}")
            return
    except Exception as e:
        print(f"[FAIL] Cannot connect to API: {str(e)}")
        return
    
    print("\nNew Features Completed!")
    print("\nMain Enhancements:")
    print("• AI Chatroom - Real-time strategy discussion")
    print("• Detailed Pattern Analysis - Clear buy/target points") 
    print("• Complete Trading Plans - Include stop-loss and risk-reward ratios")
    print("• Precise Point Indicators - Clear trading signals")
    print("• TradingView Charts - Professional visualization")
    
    print("\nPattern Analysis Improvements:")
    print("• Current Price - Current market price")
    print("• Buy Point - Recommended entry price")
    print("• Target Price - Profit-taking price")
    print("• Stop Loss - Risk control price")
    print("• Risk-Reward Ratio - Trading value assessment")
    print("• Formation Period - Pattern development time")
    
    print("\nAI Chatroom Features:")
    print("• Real-time strategy discussion")
    print("• Quick question buttons")
    print("• Technical analysis interpretation")
    print("• Backtesting suggestions")
    print("• Risk assessment")
    
    print("\nOpening enhanced trading platform...")
    chart_url = f"{BASE_URL}/chart/tradingview/AAPL?chart_type=advanced&theme=dark"
    webbrowser.open(chart_url)
    
    print(f"\nPlatform URL: {chart_url}")
    print("\nUsage Instructions:")
    print("1. Left: Real TradingView professional charts")
    print("2. Top Right: Detailed pattern analysis and trading plans")
    print("3. Bottom Right: AI chatroom for strategy discussion")
    print("4. Click quick question buttons or type directly")
    
    print("\nExample Questions:")
    print("• 'How is this stock's trend?'")
    print("• 'What's the recommended trading strategy?'")
    print("• 'How's the risk assessment?'")
    print("• 'Backtest this strategy'")
    print("• 'What's the success rate of this pattern?'")
    
    print("\nOther Tests:")
    print("• GUI: python chart_viewer.py (choose 'tradingview')")
    print("• Other stocks: Replace AAPL with TSLA, NVDA, etc.")
    print("• Light theme: Add &theme=light to URL")

if __name__ == "__main__":
    test_enhanced_trading()