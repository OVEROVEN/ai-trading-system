#!/usr/bin/env python3
"""
Debug API endpoint date filtering issues
"""

import pandas as pd
from datetime import datetime, timedelta
from src.data_fetcher.us_stocks import USStockDataFetcher
from src.data_fetcher.tw_stocks import TWStockDataFetcher
from src.analysis.technical_indicators import IndicatorAnalyzer

def debug_us_api_logic():
    print("=== US API Logic Debug ===")
    
    # Simulate API endpoint logic
    symbol = "AAPL"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    
    # Calculate period for US stocks (same logic as in API)
    days_diff = (end_date - start_date).days
    if days_diff <= 7:
        period = "5d"
    elif days_diff <= 30:
        period = "1mo"
    elif days_diff <= 90:
        period = "3mo"
    elif days_diff <= 180:
        period = "6mo"
    elif days_diff <= 365:
        period = "1y"
    else:
        period = "max"
    
    print(f"Calculated period: {period}")
    
    # Fetch data
    us_fetcher = USStockDataFetcher()
    data = us_fetcher.fetch_historical_data(symbol, period=period)
    
    print(f"Original data shape: {data.shape}")
    print(f"Original index type: {type(data.index)}")
    print(f"Original date range: {data.index.min()} to {data.index.max()}")
    
    # Filter by date range if we got more data than requested
    if not data.empty:
        # Convert index to datetime if it isn't already
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
        # Filter by date range
        print("Applying date filter...")
        print(f"Filtering: {start_date.date()} <= dates <= {end_date.date()}")
        
        try:
            filtered_data = data[(data.index.date >= start_date.date()) & (data.index.date <= end_date.date())]
            print(f"Filtered data shape: {filtered_data.shape}")
            print(f"Filtered index type: {type(filtered_data.index)}")
            
            if not filtered_data.empty:
                print(f"Filtered date range: {filtered_data.index.min()} to {filtered_data.index.max()}")
        except Exception as e:
            print(f"[FAIL] Date filtering failed: {str(e)}")
            import traceback
            traceback.print_exc()

def debug_tw_api_logic():
    print("\n=== Taiwan API Logic Debug ===")
    
    # Simulate API endpoint logic
    symbol = "2330.TW"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    
    # Fetch Taiwan data
    tw_fetcher = TWStockDataFetcher()
    data = tw_fetcher.fetch_historical_data(symbol, start_date=start_date, end_date=end_date)
    
    print(f"TW data shape: {data.shape}")
    print(f"TW index type: {type(data.index)}")
    
    if not data.empty:
        print(f"TW date range: {data.index.min()} to {data.index.max()}")

if __name__ == "__main__":
    debug_us_api_logic()
    debug_tw_api_logic()