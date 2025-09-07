import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import asyncio
import aiohttp
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

@dataclass
class StockData:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: float

@dataclass
class RealTimeQuote:
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime

class USStockDataFetcher:
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def fetch_historical_data(
        self, 
        symbol: str, 
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical stock data using yfinance.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data found for symbol {symbol}")
                return pd.DataFrame()
            
            # Clean and format data - keep datetime index for backtesting
            if 'Date' not in data.columns:
                # Index is already datetime, just clean column names
                data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            else:
                # Reset index was called, need to set it back
                data.reset_index(inplace=True)
                data.columns = [col.lower().replace(' ', '_') for col in data.columns]
                if 'date' in data.columns:
                    data.set_index('date', inplace=True)
            
            # Ensure index is datetime
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)
            
            # Add symbol column
            data['symbol'] = symbol
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def fetch_multiple_symbols(
        self, 
        symbols: List[str], 
        period: str = "1y",
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical data for multiple symbols concurrently.
        
        Args:
            symbols: List of stock symbols
            period: Data period
            interval: Data interval
            
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        results = {}
        
        # Use ThreadPoolExecutor for concurrent API calls
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.fetch_historical_data, symbol, period, interval): symbol 
                for symbol in symbols
            }
            
            for future in future_to_symbol:
                symbol = future_to_symbol[future]
                try:
                    data = future.result()
                    if not data.empty:
                        results[symbol] = data
                    else:
                        logger.warning(f"Empty data for symbol {symbol}")
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {str(e)}")
        
        return results
    
    def get_stock_data(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """
        Get stock data - wrapper for fetch_historical_data to match API expectations
        
        Args:
            symbol: Stock symbol
            period: Data period
            
        Returns:
            DataFrame with OHLCV data
        """
        return self.fetch_historical_data(symbol, period)
    
    def get_real_time_quote(self, symbol: str) -> Optional[RealTimeQuote]:
        """
        Get real-time quote for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            RealTimeQuote object or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
            
            price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            change = info.get('regularMarketChange', 0)
            change_percent = info.get('regularMarketChangePercent', 0)
            volume = info.get('regularMarketVolume', 0)
            
            return RealTimeQuote(
                symbol=symbol,
                price=price,
                change=change,
                change_percent=change_percent * 100,  # Convert to percentage
                volume=volume,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching real-time quote for {symbol}: {str(e)}")
            return None
    
    def get_company_info(self, symbol: str) -> Optional[Dict]:
        """
        Get company information for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company info or None
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                return None
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'beta': info.get('beta', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'description': info.get('longBusinessSummary', ''),
            }
            
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {str(e)}")
            return None
    
    def calculate_price_change(self, data: pd.DataFrame, periods: int = 1) -> pd.DataFrame:
        """
        Calculate price change over specified periods.
        
        Args:
            data: OHLCV DataFrame
            periods: Number of periods to look back
            
        Returns:
            DataFrame with price change columns added
        """
        if data.empty:
            return data
        
        df = data.copy()
        
        # Calculate returns
        df['price_change'] = df['close'].diff(periods)
        df['price_change_pct'] = df['close'].pct_change(periods) * 100
        
        # Calculate volatility (rolling standard deviation)
        df['volatility_20d'] = df['close'].pct_change().rolling(20).std() * np.sqrt(252) * 100
        
        # Calculate high-low spread
        df['hl_spread'] = ((df['high'] - df['low']) / df['close']) * 100
        
        return df
    
    def get_intraday_data(self, symbol: str, days: int = 1) -> pd.DataFrame:
        """
        Get intraday data (1-minute intervals) for recent days.
        
        Args:
            symbol: Stock symbol
            days: Number of days to fetch (max 7 for yfinance)
            
        Returns:
            DataFrame with 1-minute interval data
        """
        try:
            # yfinance limits intraday data to last 7 days
            days = min(days, 7)
            period = f"{days}d"
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval="1m")
            
            if data.empty:
                logger.warning(f"No intraday data found for symbol {symbol}")
                return pd.DataFrame()
            
            # Clean and format data
            data.reset_index(inplace=True)
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            data['symbol'] = symbol
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def is_market_open(self) -> bool:
        """
        Check if US market is currently open.
        
        Returns:
            True if market is open, False otherwise
        """
        try:
            # Get current time in ET (market timezone)
            import pytz
            et_tz = pytz.timezone('US/Eastern')
            now_et = datetime.now(et_tz)
            
            # Check if it's a weekday
            if now_et.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return False
            
            # Check if it's within market hours (9:30 AM - 4:00 PM ET)
            market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
            
            return market_open <= now_et <= market_close
            
        except Exception as e:
            logger.error(f"Error checking market status: {str(e)}")
            return False
    
    async def stream_real_time_data(self, symbols: List[str], callback=None):
        """
        Stream real-time data for multiple symbols.
        Note: This is a basic implementation. For production, consider using WebSocket APIs.
        
        Args:
            symbols: List of symbols to stream
            callback: Function to call with new data
        """
        while True:
            try:
                for symbol in symbols:
                    quote = self.get_real_time_quote(symbol)
                    if quote and callback:
                        await callback(quote)
                
                # Wait before next update (avoid rate limiting)
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in real-time stream: {str(e)}")
                await asyncio.sleep(10)

# Example usage
if __name__ == "__main__":
    # Initialize fetcher
    fetcher = USStockDataFetcher()
    
    # Fetch data for Apple
    aapl_data = fetcher.fetch_historical_data("AAPL", period="3mo", interval="1d")
    print(f"AAPL data shape: {aapl_data.shape}")
    print(aapl_data.head())
    
    # Get real-time quote
    quote = fetcher.get_real_time_quote("AAPL")
    if quote:
        print(f"AAPL: ${quote.price:.2f} ({quote.change:+.2f}, {quote.change_percent:+.2f}%)")
    
    # Fetch multiple symbols
    symbols = ["AAPL", "GOOGL", "TSLA", "SPY"]
    data_dict = fetcher.fetch_multiple_symbols(symbols, period="1mo")
    
    for symbol, data in data_dict.items():
        print(f"{symbol}: {len(data)} data points")
    
    # Check market status
    print(f"Market is {'open' if fetcher.is_market_open() else 'closed'}")