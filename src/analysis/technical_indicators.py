import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, Any
import logging

# Try to import talib, fallback to manual calculations if not available
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logging.warning("TA-Lib not available. Using manual calculations for technical indicators.")

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """
    Comprehensive technical indicators calculator with fallback implementations.
    """
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        if TALIB_AVAILABLE:
            return pd.Series(talib.SMA(data.values, timeperiod=period), index=data.index)
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        if TALIB_AVAILABLE:
            return pd.Series(talib.EMA(data.values, timeperiod=period), index=data.index)
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Relative Strength Index
        
        Args:
            data: Price series (typically close prices)
            period: RSI period (default 14)
            
        Returns:
            RSI values (0-100)
        """
        if TALIB_AVAILABLE:
            return pd.Series(talib.RSI(data.values, timeperiod=period), index=data.index)
        
        # Manual calculation
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(data: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACD (Moving Average Convergence Divergence)
        
        Args:
            data: Price series
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line EMA period
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        if TALIB_AVAILABLE:
            macd_line, signal_line, histogram = talib.MACD(
                data.values, fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period
            )
            return (
                pd.Series(macd_line, index=data.index),
                pd.Series(signal_line, index=data.index),
                pd.Series(histogram, index=data.index)
            )
        
        # Manual calculation
        ema_fast = TechnicalIndicators.ema(data, fast_period)
        ema_slow = TechnicalIndicators.ema(data, slow_period)
        
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal_period)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands
        
        Args:
            data: Price series
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            Tuple of (Upper band, Middle band/SMA, Lower band)
        """
        if TALIB_AVAILABLE:
            upper, middle, lower = talib.BBANDS(
                data.values, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev, matype=0
            )
            return (
                pd.Series(upper, index=data.index),
                pd.Series(middle, index=data.index),
                pd.Series(lower, index=data.index)
            )
        
        # Manual calculation
        sma = TechnicalIndicators.sma(data, period)
        rolling_std = data.rolling(window=period).std()
        
        upper_band = sma + (rolling_std * std_dev)
        lower_band = sma - (rolling_std * std_dev)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def stochastic_oscillator(high: pd.Series, low: pd.Series, close: pd.Series, 
                            k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Stochastic Oscillator
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            k_period: %K period
            d_period: %D period
            
        Returns:
            Tuple of (%K, %D)
        """
        if TALIB_AVAILABLE:
            slowk, slowd = talib.STOCH(
                high.values, low.values, close.values,
                fastk_period=k_period, slowk_period=3, slowk_matype=0,
                slowd_period=d_period, slowd_matype=0
            )
            return (
                pd.Series(slowk, index=close.index),
                pd.Series(slowd, index=close.index)
            )
        
        # Manual calculation
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return k_percent, d_percent
    
    @staticmethod
    def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Williams %R
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Lookback period
            
        Returns:
            Williams %R values (-100 to 0)
        """
        if TALIB_AVAILABLE:
            return pd.Series(talib.WILLR(high.values, low.values, close.values, timeperiod=period), 
                           index=close.index)
        
        # Manual calculation
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        
        wr = -100 * ((highest_high - close) / (highest_high - lowest_low))
        return wr
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Average True Range
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period
            
        Returns:
            ATR values
        """
        if TALIB_AVAILABLE:
            return pd.Series(talib.ATR(high.values, low.values, close.values, timeperiod=period),
                           index=close.index)
        
        # Manual calculation
        high_low = high - low
        high_close_prev = abs(high - close.shift(1))
        low_close_prev = abs(low - close.shift(1))
        
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Average Directional Index
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ADX period
            
        Returns:
            ADX values
        """
        if TALIB_AVAILABLE:
            return pd.Series(talib.ADX(high.values, low.values, close.values, timeperiod=period),
                           index=close.index)
        
        # Manual calculation (simplified)
        plus_dm = high.diff()
        minus_dm = low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        minus_dm = abs(minus_dm)
        
        atr_values = TechnicalIndicators.atr(high, low, close, period)
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr_values)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr_values)
        
        dx = 100 * abs((plus_di - minus_di) / (plus_di + minus_di))
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def volume_sma(volume: pd.Series, period: int = 20) -> pd.Series:
        """Volume Simple Moving Average"""
        return volume.rolling(window=period).mean()
    
    @staticmethod
    def price_volume_trend(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        Price Volume Trend
        
        Args:
            close: Close prices
            volume: Volume data
            
        Returns:
            PVT values
        """
        price_change_pct = close.pct_change()
        pvt = (price_change_pct * volume).cumsum()
        return pvt
    
    @staticmethod
    def on_balance_volume(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        On Balance Volume
        
        Args:
            close: Close prices
            volume: Volume data
            
        Returns:
            OBV values
        """
        if TALIB_AVAILABLE:
            return pd.Series(talib.OBV(close.values, volume.values), index=close.index)
        
        # Manual calculation
        price_change = close.diff()
        obv = volume.copy()
        obv[price_change < 0] = -obv[price_change < 0]
        obv[price_change == 0] = 0
        obv = obv.cumsum()
        
        return obv

class IndicatorAnalyzer:
    """
    Analyze technical indicators and generate signals.
    """
    
    def __init__(self):
        self.ti = TechnicalIndicators()
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators for OHLCV data.
        
        Args:
            data: DataFrame with OHLCV columns
            
        Returns:
            DataFrame with all indicators added
        """
        df = data.copy()
        
        try:
            # Moving Averages
            df['sma_20'] = self.ti.sma(df['close'], 20)
            df['sma_50'] = self.ti.sma(df['close'], 50)
            df['ema_12'] = self.ti.ema(df['close'], 12)
            df['ema_26'] = self.ti.ema(df['close'], 26)
            
            # RSI
            df['rsi'] = self.ti.rsi(df['close'])
            
            # MACD
            macd_line, signal_line, histogram = self.ti.macd(df['close'])
            df['macd'] = macd_line
            df['macd_signal'] = signal_line
            df['macd_histogram'] = histogram
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = self.ti.bollinger_bands(df['close'])
            df['bb_upper'] = bb_upper
            df['bb_middle'] = bb_middle
            df['bb_lower'] = bb_lower
            df['bb_width'] = (bb_upper - bb_lower) / bb_middle
            df['bb_position'] = (df['close'] - bb_lower) / (bb_upper - bb_lower)
            
            # Stochastic
            stoch_k, stoch_d = self.ti.stochastic_oscillator(df['high'], df['low'], df['close'])
            df['stoch_k'] = stoch_k
            df['stoch_d'] = stoch_d
            
            # Williams %R
            df['williams_r'] = self.ti.williams_r(df['high'], df['low'], df['close'])
            
            # ATR
            df['atr'] = self.ti.atr(df['high'], df['low'], df['close'])
            
            # ADX
            df['adx'] = self.ti.adx(df['high'], df['low'], df['close'])
            
            # Volume indicators
            df['volume_sma'] = self.ti.volume_sma(df['volume'])
            df['obv'] = self.ti.on_balance_volume(df['close'], df['volume'])
            df['pvt'] = self.ti.price_volume_trend(df['close'], df['volume'])
            
            # Additional calculated fields
            df['price_change'] = df['close'].pct_change()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {str(e)}")
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on technical indicators.
        
        Args:
            data: DataFrame with indicators
            
        Returns:
            DataFrame with signal columns added
        """
        df = data.copy()
        
        # RSI signals
        df['rsi_oversold'] = df['rsi'] < 30
        df['rsi_overbought'] = df['rsi'] > 70
        
        # MACD signals
        df['macd_bullish'] = (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))
        df['macd_bearish'] = (df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))
        
        # Moving Average signals
        df['sma_bullish'] = df['close'] > df['sma_20']
        df['golden_cross'] = (df['sma_20'] > df['sma_50']) & (df['sma_20'].shift(1) <= df['sma_50'].shift(1))
        df['death_cross'] = (df['sma_20'] < df['sma_50']) & (df['sma_20'].shift(1) >= df['sma_50'].shift(1))
        
        # Bollinger Bands signals
        df['bb_squeeze'] = df['bb_width'] < df['bb_width'].rolling(20).mean() * 0.8
        df['bb_breakout_upper'] = (df['close'] > df['bb_upper']) & (df['close'].shift(1) <= df['bb_upper'].shift(1))
        df['bb_breakout_lower'] = (df['close'] < df['bb_lower']) & (df['close'].shift(1) >= df['bb_lower'].shift(1))
        
        # Volume signals
        df['volume_spike'] = df['volume_ratio'] > 2.0
        
        # Composite signals
        df['bullish_signal'] = (
            df['rsi_oversold'] | 
            df['macd_bullish'] | 
            df['golden_cross'] |
            (df['bb_breakout_lower'] & df['volume_spike'])
        )
        
        df['bearish_signal'] = (
            df['rsi_overbought'] | 
            df['macd_bearish'] | 
            df['death_cross'] |
            (df['bb_breakout_upper'] & df['volume_spike'])
        )
        
        return df
    
    def calculate_indicator_strength(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate the strength of various indicators.
        
        Args:
            data: DataFrame with indicators
            
        Returns:
            Dictionary with indicator strengths
        """
        latest = data.iloc[-1] if len(data) > 0 else pd.Series()
        
        strengths = {}
        
        # RSI strength (distance from neutral 50)
        if 'rsi' in latest and not pd.isna(latest['rsi']):
            rsi_distance = abs(latest['rsi'] - 50) / 50
            strengths['rsi'] = min(rsi_distance, 1.0)
        
        # MACD strength (histogram magnitude)
        if 'macd_histogram' in latest and not pd.isna(latest['macd_histogram']):
            hist_abs = abs(latest['macd_histogram'])
            hist_max = data['macd_histogram'].abs().rolling(50).max().iloc[-1] if len(data) >= 50 else hist_abs
            strengths['macd'] = min(hist_abs / hist_max if hist_max > 0 else 0, 1.0)
        
        # Volume strength
        if 'volume_ratio' in latest and not pd.isna(latest['volume_ratio']):
            strengths['volume'] = min(latest['volume_ratio'] / 3.0, 1.0)  # Normalize to 3x average
        
        # Trend strength (ADX)
        if 'adx' in latest and not pd.isna(latest['adx']):
            strengths['trend'] = min(latest['adx'] / 50.0, 1.0)  # Normalize to 50
        
        return strengths
    
    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive analysis of technical indicators
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Dictionary with indicator values and analysis
        """
        if data.empty:
            return {}
        
        # Calculate all indicators
        df_with_indicators = self.calculate_all_indicators(data)
        
        # Get latest values
        latest = df_with_indicators.iloc[-1] if len(df_with_indicators) > 0 else pd.Series()
        
        return {
            'rsi': latest.get('rsi', 50),
            'macd': latest.get('macd', 0),
            'macd_signal': latest.get('macd_signal', 0),
            'macd_histogram': latest.get('macd_histogram', 0),
            'sma_20': latest.get('sma_20', 0),
            'sma_50': latest.get('sma_50', 0),
            'ema_12': latest.get('ema_12', 0),
            'ema_26': latest.get('ema_26', 0),
            'bb_upper': latest.get('bb_upper', 0),
            'bb_middle': latest.get('bb_middle', 0),
            'bb_lower': latest.get('bb_lower', 0),
            'stoch_k': latest.get('stoch_k', 50),
            'stoch_d': latest.get('stoch_d', 50),
            'williams_r': latest.get('williams_r', -50),
            'current_price': float(data['close'].iloc[-1]) if len(data) > 0 else 0
        }

# Example usage
if __name__ == "__main__":
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # Generate sample OHLCV data
    close_prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    high_prices = close_prices + np.random.rand(100) * 2
    low_prices = close_prices - np.random.rand(100) * 2
    open_prices = close_prices + (np.random.randn(100) * 0.3)
    volumes = np.random.randint(1000000, 5000000, 100)
    
    sample_data = pd.DataFrame({
        'date': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    })
    
    # Calculate indicators
    analyzer = IndicatorAnalyzer()
    data_with_indicators = analyzer.calculate_all_indicators(sample_data)
    data_with_signals = analyzer.generate_signals(data_with_indicators)
    
    # Display results
    print("Sample data with indicators:")
    print(data_with_signals[['date', 'close', 'rsi', 'macd', 'bb_upper', 'bb_lower']].tail())
    
    # Calculate strengths
    strengths = analyzer.calculate_indicator_strength(data_with_signals)
    print(f"\nIndicator strengths: {strengths}")