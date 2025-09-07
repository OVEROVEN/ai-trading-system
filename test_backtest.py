#!/usr/bin/env python3
"""
Test script for the backtesting API endpoints
"""

import requests
import json
import time
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("[OK] API is running")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print("[FAIL] API health check failed")
            return False
    except Exception as e:
        print(f"[FAIL] Cannot connect to API: {str(e)}")
        return False

def test_available_strategies():
    """Test getting available strategies"""
    try:
        response = requests.get(f"{BASE_URL}/backtest/strategies")
        if response.status_code == 200:
            print("[OK] Available strategies endpoint working")
            data = response.json()
            print("Available strategies:", data.get('available_strategies', []))
            return True
        else:
            print("[FAIL] Failed to get strategies")
            return False
    except Exception as e:
        print(f"[FAIL] Error getting strategies: {str(e)}")
        return False

def test_backtest_us_stock():
    """Test backtesting with US stock"""
    # Calculate date range (3 months back)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    backtest_request = {
        "symbol": "AAPL",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "strategy_name": "rsi_macd",
        "strategy_params": {
            "rsi_oversold": 30,
            "rsi_overbought": 70
        },
        "initial_capital": 10000,
        "commission": 0.001,
        "stop_loss_pct": 0.02,
        "take_profit_pct": 0.06
    }
    
    try:
        print(f"Testing backtest for AAPL from {start_date.date()} to {end_date.date()}")
        response = requests.post(f"{BASE_URL}/backtest", json=backtest_request)
        
        if response.status_code == 200:
            print("[OK] US stock backtest successful")
            data = response.json()
            
            # Print key results
            performance = data.get('performance_metrics', {})
            trades = data.get('trade_statistics', {})
            
            print(f"[RESULTS] Backtest Results for {data.get('symbol')}:")
            print(f"   Total Return: {performance.get('total_return_pct', 0):.2f}%")
            print(f"   Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}")
            print(f"   Max Drawdown: {performance.get('max_drawdown_pct', 0):.2f}%")
            print(f"   Total Trades: {trades.get('total_trades', 0)}")
            print(f"   Win Rate: {trades.get('win_rate', 0):.1f}%")
            
            return True
        else:
            print(f"[FAIL] US stock backtest failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"[FAIL] Error testing US stock backtest: {str(e)}")
        return False

def test_backtest_taiwan_stock():
    """Test backtesting with Taiwan stock"""
    # Calculate date range (3 months back)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    backtest_request = {
        "symbol": "2330.TW",  # Taiwan Semiconductor
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "strategy_name": "ma_crossover",
        "strategy_params": {
            "fast_period": 20,
            "slow_period": 50
        },
        "initial_capital": 10000,
        "commission": 0.001425,  # Taiwan commission rate
        "stop_loss_pct": 0.02,
        "take_profit_pct": 0.06
    }
    
    try:
        print(f"Testing backtest for 2330.TW from {start_date.date()} to {end_date.date()}")
        response = requests.post(f"{BASE_URL}/backtest", json=backtest_request)
        
        if response.status_code == 200:
            print("[OK] Taiwan stock backtest successful")
            data = response.json()
            
            # Print key results
            performance = data.get('performance_metrics', {})
            trades = data.get('trade_statistics', {})
            
            print(f"[RESULTS] Backtest Results for {data.get('symbol')}:")
            print(f"   Total Return: {performance.get('total_return_pct', 0):.2f}%")
            print(f"   Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}")
            print(f"   Max Drawdown: {performance.get('max_drawdown_pct', 0):.2f}%")
            print(f"   Total Trades: {trades.get('total_trades', 0)}")
            print(f"   Win Rate: {trades.get('win_rate', 0):.1f}%")
            
            return True
        else:
            print(f"[FAIL] Taiwan stock backtest failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"[FAIL] Error testing Taiwan stock backtest: {str(e)}")
        return False

def main():
    """Run all backtest tests"""
    print("Starting Backtesting System Tests")
    print("=" * 50)
    
    # Test API health
    if not test_health_check():
        print("[FAIL] API not available, stopping tests")
        return
    
    print("\n" + "=" * 50)
    
    # Test strategy endpoints
    test_available_strategies()
    
    print("\n" + "=" * 50)
    
    # Test US stock backtesting
    test_backtest_us_stock()
    
    print("\n" + "=" * 50)
    
    # Test Taiwan stock backtesting
    test_backtest_taiwan_stock()
    
    print("\n" + "=" * 50)
    print("[COMPLETE] Backtesting tests completed!")

if __name__ == "__main__":
    main()