#!/usr/bin/env python3
"""
Test individual API components to isolate the issue
"""

import pandas as pd
from datetime import datetime, timedelta
from src.data_fetcher.us_stocks import USStockDataFetcher
from src.analysis.technical_indicators import IndicatorAnalyzer
from src.backtesting.backtest_engine import BacktestEngine, BacktestConfig, StrategyFactory

def test_data_processing():
    """Test the exact data processing flow from the API"""
    print("=== Testing Data Processing Flow ===")
    
    try:
        # Parse dates like the API does
        start_date = datetime.strptime("2025-05-17", "%Y-%m-%d")
        end_date = datetime.strptime("2025-08-15", "%Y-%m-%d")
        symbol = "AAPL"
        
        print(f"Parsed dates: {start_date} to {end_date}")
        
        # Initialize components like the API does
        us_fetcher = USStockDataFetcher()
        indicator_analyzer = IndicatorAnalyzer()
        
        # Calculate period exactly like API does
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
        
        # Fetch data exactly like API does
        data = us_fetcher.fetch_historical_data(symbol, period=period)
        print(f"Fetched data: shape={data.shape}, index_type={type(data.index)}")
        
        # Filter exactly like API does
        if not data.empty:
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)
            data = data[(data.index.date >= start_date.date()) & (data.index.date <= end_date.date())]
        
        print(f"Filtered data: shape={data.shape}, index_type={type(data.index)}")
        
        if data.empty:
            print("No data found")
            return
        
        # Calculate indicators exactly like API does
        data_with_indicators = indicator_analyzer.calculate_all_indicators(data)
        print(f"Data with indicators: shape={data_with_indicators.shape}")
        
        # Create strategy exactly like API does
        strategy_params = {'rsi_oversold': 30, 'rsi_overbought': 70}
        strategy = StrategyFactory.create_strategy("rsi_macd", **strategy_params)
        print(f"Strategy created: {strategy.get_strategy_name()}")
        
        # Create config exactly like API does
        config = BacktestConfig(
            initial_capital=10000,
            commission=0.001,
            stop_loss_pct=0.02,
            take_profit_pct=0.06
        )
        print(f"Config created")
        
        # Run backtest exactly like API does
        engine = BacktestEngine(config)
        print(f"Engine created, starting backtest...")
        results = engine.run_backtest(strategy, data_with_indicators, symbol)
        
        print(f"SUCCESS! Total return: {results.total_return_pct:.2%}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_processing()