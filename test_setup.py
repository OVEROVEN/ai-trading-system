#!/usr/bin/env python3
"""
Quick test script to verify the AI Trading System setup
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

def test_environment():
    """Test if environment variables are set."""
    print("Testing environment configuration...")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("Warning: python-dotenv not installed, loading .env manually")
        # Load .env manually
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key.startswith('sk-'):
        print("OK - OpenAI API key found and looks valid")
        return True
    else:
        print("ERROR - OpenAI API key missing or invalid")
        return False

def test_basic_imports():
    """Test if we can import our modules."""
    print("\nTesting basic imports...")
    
    try:
        # Test basic imports
        import pandas as pd
        print("OK - pandas imported")
        
        import numpy as np
        print("OK - numpy imported")
        
        import yfinance as yf
        print("OK - yfinance imported")
        
        # Test our modules
        from src.data_fetcher.us_stocks import USStockDataFetcher
        print("OK - US stock fetcher imported")
        
        from src.analysis.technical_indicators import IndicatorAnalyzer
        print("OK - Technical indicators imported")
        
        from config.settings import settings
        print("OK - Settings imported")
        
        return True
        
    except Exception as e:
        print(f"ERROR - Import failed: {str(e)}")
        return False

def test_data_fetching():
    """Test basic data fetching functionality."""
    print("\nTesting data fetching...")
    
    try:
        from src.data_fetcher.us_stocks import USStockDataFetcher
        
        fetcher = USStockDataFetcher()
        
        # Test fetching Apple data
        print("  Fetching AAPL data...")
        data = fetcher.fetch_historical_data("AAPL", period="5d", interval="1d")
        
        if not data.empty:
            print(f"OK - Successfully fetched {len(data)} data points for AAPL")
            print(f"  Latest close price: ${data['close'].iloc[-1]:.2f}")
            return True
        else:
            print("ERROR - No data retrieved for AAPL")
            return False
            
    except Exception as e:
        print(f"ERROR - Data fetching failed: {str(e)}")
        return False

def test_technical_analysis():
    """Test technical analysis functionality."""
    print("\nTesting technical analysis...")
    
    try:
        from src.data_fetcher.us_stocks import USStockDataFetcher
        from src.analysis.technical_indicators import IndicatorAnalyzer
        import pandas as pd
        
        # Get some data
        fetcher = USStockDataFetcher()
        data = fetcher.fetch_historical_data("AAPL", period="1mo", interval="1d")
        
        if data.empty:
            print("ERROR - No data for technical analysis")
            return False
        
        # Calculate indicators
        analyzer = IndicatorAnalyzer()
        data_with_indicators = analyzer.calculate_all_indicators(data)
        
        latest = data_with_indicators.iloc[-1]
        
        print("OK - Technical indicators calculated successfully:")
        if not pd.isna(latest.get('rsi')):
            print(f"  RSI: {latest['rsi']:.2f}")
        if not pd.isna(latest.get('macd')):
            print(f"  MACD: {latest['macd']:.4f}")
        if not pd.isna(latest.get('sma_20')):
            print(f"  SMA(20): ${latest['sma_20']:.2f}")
        
        return True
            
    except Exception as e:
        print(f"ERROR - Technical analysis failed: {str(e)}")
        return False

async def test_ai_analysis():
    """Test AI analysis functionality."""
    print("\nTesting AI analysis...")
    
    try:
        from src.analysis.ai_analyzer import OpenAIAnalyzer
        
        # Initialize AI analyzer
        ai_analyzer = OpenAIAnalyzer()
        print("OK - AI analyzer initialized successfully")
        
        # Create minimal test data
        import pandas as pd
        import numpy as np
        
        # Create sample data
        dates = pd.date_range('2023-01-01', periods=20, freq='D')
        data = pd.DataFrame({
            'close': 100 + np.cumsum(np.random.randn(20) * 0.5),
            'volume': np.random.randint(1000000, 5000000, 20)
        }, index=dates)
        
        # Test basic AI analysis
        indicators = {'rsi': 65, 'macd': 0.5}
        patterns = {'breakouts': []}
        
        print("  Running AI analysis (this may take a moment)...")
        result = await ai_analyzer.analyze_technical_data(
            'AAPL', data, indicators, patterns, context="Test analysis"
        )
        
        print("OK - AI analysis completed successfully:")
        print(f"  Recommendation: {result.recommendation}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Reasoning: {result.reasoning[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"ERROR - AI analysis failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("AI Trading System Setup Test")
    print("=" * 40)
    
    tests = [
        ("Environment", test_environment),
        ("Basic Imports", test_basic_imports),
        ("Data Fetching", test_data_fetching),
        ("Technical Analysis", test_technical_analysis),
    ]
    
    results = []
    
    # Run synchronous tests first
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"ERROR - {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Run AI test separately (async)
    try:
        ai_success = asyncio.run(test_ai_analysis())
        results.append(("AI Analysis", ai_success))
    except Exception as e:
        print(f"ERROR - AI Analysis test crashed: {str(e)}")
        results.append(("AI Analysis", False))
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    print("=" * 40)
    
    passed = 0
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name:20} {status}")
        if success:
            passed += 1
    
    print(f"\n{passed}/{len(results)} tests passed")
    
    if passed >= 4:  # At least basic functionality working
        print("\nSuccess! Your AI Trading System is ready!")
        print("\nNext steps:")
        print("1. Start the API server:")
        print("   python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload")
        print("2. Open your browser to: http://localhost:8000/docs")
        print("3. Try the API endpoints!")
        
        # Show example API calls
        print("\nExample API calls:")
        print("curl http://localhost:8000/health")
        print("curl -X POST http://localhost:8000/analyze/AAPL")
        print("curl http://localhost:8000/signals/TSLA")
        
    else:
        print(f"\nSome tests failed. Please check the error messages above.")
        if passed == 0:
            print("Try installing missing dependencies:")
            print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()