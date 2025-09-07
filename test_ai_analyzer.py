#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.abspath('.'))

from src.analysis.ai_analyzer import OpenAIAnalyzer
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_ai_analyzer():
    print("Testing AI Analyzer initialization and language support...")
    
    try:
        # Test initialization
        print("1. Testing AI Analyzer initialization...")
        analyzer = OpenAIAnalyzer()
        print("✅ AI Analyzer initialized successfully")
        
        # Test language support with a simple analysis
        print("2. Testing AI analysis with Chinese language...")
        
        # Create dummy data for testing
        data = pd.DataFrame({
            'Close': [100, 101, 102, 101, 103],
            'Volume': [1000, 1100, 900, 1200, 1050],
            'High': [101, 102, 103, 102, 104],
            'Low': [99, 100, 101, 100, 102],
            'Open': [100, 101, 102, 101, 103]
        })
        
        indicators = {
            'rsi': 55.5,
            'macd': 0.5,
            'sma_20': 101.4
        }
        
        patterns = {}
        
        # Test with English
        print("Testing with English (en)...")
        result_en = await analyzer.analyze_technical_data(
            'AAPL', data, indicators, patterns, language='en'
        )
        print(f"English result: {result_en.reasoning[:100]}...")
        
        # Test with Chinese
        print("Testing with Chinese (zh-TW)...")
        result_zh = await analyzer.analyze_technical_data(
            'AAPL', data, indicators, patterns, language='zh-TW'
        )
        print(f"Chinese result: {result_zh.reasoning[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_ai_analyzer())
    sys.exit(0 if success else 1)