#!/usr/bin/env python3
"""
Simple test replicating API logic exactly
"""

import pandas as pd
from datetime import datetime, timedelta
from src.data_fetcher.us_stocks import USStockDataFetcher
from src.data_fetcher.tw_stocks import TWStockDataFetcher
from src.analysis.technical_indicators import IndicatorAnalyzer
from src.backtesting.backtest_engine import BacktestEngine, BacktestConfig, StrategyFactory

def test_us_api_exact():
    print("=== Testing US API Logic Exactly ===")
    
    try:
        # Replicate API logic exactly
        symbol = "AAPL"
        start_date = datetime.strptime("2025-05-17", "%Y-%m-%d")
        end_date = datetime.strptime("2025-08-15", "%Y-%m-%d")
        
        print(f"Symbol: {symbol}")
        print(f"Dates: {start_date} to {end_date}")
        
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
            
        print(f"Period: {period}")
        
        # Fetch data using API logic
        us_fetcher = USStockDataFetcher()
        data = us_fetcher.fetch_historical_data(symbol, period=period)
        
        print(f"Raw data shape: {data.shape}")
        print(f"Raw data index type: {type(data.index)}")
        
        # Filter by date range if we got more data than requested
        if not data.empty:
            # Convert index to datetime if it isn't already
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)
            # Filter by date range
            data = data[(data.index.date >= start_date.date()) & (data.index.date <= end_date.date())]
        
        print(f"Filtered data shape: {data.shape}")
        print(f"Filtered data index type: {type(data.index)}")
        
        if data.empty:
            print("No data found after filtering")
            return
            
        # Calculate technical indicators
        print("Calculating indicators...")
        indicator_analyzer = IndicatorAnalyzer()
        data_with_indicators = indicator_analyzer.calculate_all_indicators(data)
        
        print(f"Data with indicators shape: {data_with_indicators.shape}")
        print(f"Data with indicators index type: {type(data_with_indicators.index)}")
        
        # Create strategy
        print("Creating strategy...")
        strategy = StrategyFactory.create_strategy("rsi_macd", rsi_oversold=30, rsi_overbought=70)
        
        # Configure backtest
        print("Configuring backtest...")
        config = BacktestConfig(
            initial_capital=10000,
            commission=0.001,
            stop_loss_pct=0.02,
            take_profit_pct=0.06
        )
        
        # Run backtest
        print("Running backtest...")
        engine = BacktestEngine(config)
        results = engine.run_backtest(strategy, data_with_indicators, symbol)
        
        print(f"[SUCCESS] Backtest completed!")
        print(f"Total return: {results.total_return_pct:.2%}")
        print(f"Total trades: {results.total_trades}")
        
    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_us_api_exact()