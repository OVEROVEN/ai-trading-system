#!/usr/bin/env python3
"""
Debug script to understand data format issues
"""

import pandas as pd
from datetime import datetime, timedelta
from src.data_fetcher.us_stocks import USStockDataFetcher
from src.data_fetcher.tw_stocks import TWStockDataFetcher
from src.analysis.technical_indicators import IndicatorAnalyzer

def debug_us_data():
    print("=== US Data Debug ===")
    fetcher = USStockDataFetcher()
    data = fetcher.fetch_historical_data("AAPL", period="3mo")
    
    print(f"Data shape: {data.shape}")
    print(f"Index type: {type(data.index)}")
    print(f"Index dtype: {data.index.dtype}")
    print(f"Columns: {list(data.columns)}")
    print(f"First few rows:")
    print(data.head())
    print()
    
    # Test with indicators
    analyzer = IndicatorAnalyzer()
    try:
        data_with_indicators = analyzer.calculate_all_indicators(data)
        print("[OK] Technical indicators calculated successfully")
        print(f"Indicators shape: {data_with_indicators.shape}")
        print(f"Indicators index type: {type(data_with_indicators.index)}")
    except Exception as e:
        print(f"[FAIL] Technical indicators failed: {str(e)}")
    
    print()

def debug_tw_data():
    print("=== Taiwan Data Debug ===")
    fetcher = TWStockDataFetcher()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    data = fetcher.fetch_historical_data("2330.TW", start_date=start_date, end_date=end_date)
    
    print(f"Data shape: {data.shape}")
    print(f"Index type: {type(data.index)}")
    print(f"Index dtype: {data.index.dtype}")
    print(f"Columns: {list(data.columns)}")
    print(f"First few rows:")
    print(data.head())
    print()
    
    # Test with indicators
    analyzer = IndicatorAnalyzer()
    try:
        data_with_indicators = analyzer.calculate_all_indicators(data)
        print("[OK] Technical indicators calculated successfully")
        print(f"Indicators shape: {data_with_indicators.shape}")
        print(f"Indicators index type: {type(data_with_indicators.index)}")
    except Exception as e:
        print(f"[FAIL] Technical indicators failed: {str(e)}")
    
    print()

if __name__ == "__main__":
    debug_us_data()
    debug_tw_data()