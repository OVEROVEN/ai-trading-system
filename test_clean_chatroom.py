#!/usr/bin/env python3
"""
Test Clean TradingView with Working Chatroom
This version isolates TradingView widget to prevent JavaScript conflicts
"""

import webbrowser
import requests

BASE_URL = "http://localhost:8000"

def test_clean_chatroom():
    print("=== Testing Clean TradingView with AI Chatroom ===\n")
    
    # Test the clean implementation
    try:
        print("Testing clean TradingView implementation...")
        response = requests.get(f"{BASE_URL}/chart/tradingview/AAPL?chart_type=advanced&theme=dark", timeout=5)
        if response.status_code == 200:
            print("[OK] Clean TradingView implementation is working")
        else:
            print(f"[FAIL] API returned error: {response.status_code}")
            return
    except Exception as e:
        print(f"[FAIL] Cannot connect to API: {str(e)}")
        return
    
    print("\nKey Improvements in Clean Version:")
    print("• TradingView widget isolated in iframe")
    print("• JavaScript conflicts resolved")
    print("• AI Chatroom completely independent")
    print("• Cleaner error handling")
    print("• Better responsive design")
    print("• Enhanced status indicators")
    
    print("\nChatroom Features:")
    print("• Real-time AI strategy discussion")
    print("• Quick question buttons")
    print("• Loading indicators")
    print("• Error handling with helpful messages")
    print("• Character limit (500) for better responses")
    print("• Auto-focus input field")
    
    print("\nPattern Analysis Features:")
    print("• Clear buy/target/stop points")
    print("• Risk-reward ratios")
    print("• Trading plan descriptions")
    print("• Confidence levels")
    print("• Profit potential percentages")
    
    print("\nOpening clean implementation...")
    chart_url = f"{BASE_URL}/chart/tradingview/AAPL?chart_type=advanced&theme=dark"
    webbrowser.open(chart_url)
    
    print(f"\nDirect URL: {chart_url}")
    
    print("\nTesting Instructions:")
    print("1. Check if TradingView chart loads properly on the left")
    print("2. Look for AI chatroom on the right side")
    print("3. Try clicking quick question buttons")
    print("4. Test typing in the input field")
    print("5. Verify no JavaScript errors in browser console")
    
    print("\nIf chatroom still doesn't appear, check:")
    print("• Browser developer console for errors")
    print("• Network tab for failed requests")
    print("• Browser zoom level (try 100%)")
    print("• Try different browser")
    
    # Test other stocks
    print(f"\nTest other stocks:")
    print(f"• TSLA: {BASE_URL}/chart/tradingview/TSLA?chart_type=advanced")
    print(f"• NVDA: {BASE_URL}/chart/tradingview/NVDA?chart_type=advanced")
    print(f"• GOOGL: {BASE_URL}/chart/tradingview/GOOGL?chart_type=advanced")

if __name__ == "__main__":
    test_clean_chatroom()