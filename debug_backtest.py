#!/usr/bin/env python3
"""
Debug backtesting engine issues
"""

import pandas as pd
import traceback
from datetime import datetime, timedelta
from src.data_fetcher.us_stocks import USStockDataFetcher
from src.analysis.technical_indicators import IndicatorAnalyzer
from src.backtesting.backtest_engine import BacktestEngine, BacktestConfig, StrategyFactory

def debug_backtest():
    print("=== Backtest Debug ===")
    
    try:
        # Get data
        fetcher = USStockDataFetcher()
        data = fetcher.fetch_historical_data("AAPL", period="3mo")
        print(f"Data fetched: {data.shape}")
        
        # Calculate indicators
        analyzer = IndicatorAnalyzer()
        data_with_indicators = analyzer.calculate_all_indicators(data)
        print(f"Indicators calculated: {data_with_indicators.shape}")
        
        # Create strategy
        strategy = StrategyFactory.create_strategy("rsi_macd")
        print(f"Strategy created: {strategy.get_strategy_name()}")
        
        # Run backtest
        config = BacktestConfig(initial_capital=10000, commission=0.001)
        engine = BacktestEngine(config)
        
        print("Starting backtest...")
        results = engine.run_backtest(strategy, data_with_indicators, "AAPL")
        
        print(f"Backtest completed successfully!")
        print(f"Total return: {results.total_return_pct:.2%}")
        print(f"Total trades: {results.total_trades}")
        
    except Exception as e:
        print(f"[FAIL] Backtest failed: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_backtest()