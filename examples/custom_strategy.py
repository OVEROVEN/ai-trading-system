#!/usr/bin/env python3
"""
自定義策略範例 - 如何新增新的交易策略
"""

import pandas as pd
import numpy as np
from src.backtesting.backtest_engine import TradingStrategy

class BollingerBandStrategy(TradingStrategy):
    """
    布林帶策略範例
    
    買入訊號: 價格觸及下軌且 RSI < 30
    賣出訊號: 價格觸及上軌且 RSI > 70
    """
    
    def __init__(self, bb_period=20, bb_std=2, rsi_oversold=30, rsi_overbought=70):
        """
        初始化策略參數
        
        Args:
            bb_period: 布林帶週期
            bb_std: 布林帶標準差倍數
            rsi_oversold: RSI 超賣閾值
            rsi_overbought: RSI 超買閾值
        """
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易訊號
        
        Args:
            data: 包含 OHLCV 和技術指標的 DataFrame
            
        Returns:
            添加訊號欄位的 DataFrame
        """
        df = data.copy()
        
        # 初始化訊號欄位
        df['signal'] = 0
        df['signal_strength'] = 0.0
        df['signal_source'] = 'BollingerBand'
        
        # 確保有必要的技術指標
        if 'bb_upper' not in df.columns or 'bb_lower' not in df.columns:
            # 計算布林帶
            sma = df['close'].rolling(self.bb_period).mean()
            std = df['close'].rolling(self.bb_period).std()
            df['bb_upper'] = sma + (std * self.bb_std)
            df['bb_lower'] = sma - (std * self.bb_std)
            df['bb_middle'] = sma
        
        # 買入訊號: 價格觸及下軌且 RSI 超賣
        buy_signal = (
            (df['close'] <= df['bb_lower']) & 
            (df['rsi'] < self.rsi_oversold) &
            (df['close'].shift(1) > df['bb_lower'].shift(1))  # 剛觸及下軌
        )
        
        # 賣出訊號: 價格觸及上軌且 RSI 超買
        sell_signal = (
            (df['close'] >= df['bb_upper']) & 
            (df['rsi'] > self.rsi_overbought) &
            (df['close'].shift(1) < df['bb_upper'].shift(1))  # 剛觸及上軌
        )
        
        # 設定訊號
        df.loc[buy_signal, 'signal'] = 1
        df.loc[sell_signal, 'signal'] = -1
        
        # 計算訊號強度
        # 越接近布林帶邊界且 RSI 越極端，訊號越強
        buy_strength = np.where(
            buy_signal,
            np.clip((self.rsi_oversold - df['rsi']) / self.rsi_oversold + 
                   (df['bb_lower'] - df['close']) / (df['bb_upper'] - df['bb_lower']), 
                   0.3, 1.0),
            0.0
        )
        
        sell_strength = np.where(
            sell_signal,
            np.clip((df['rsi'] - self.rsi_overbought) / (100 - self.rsi_overbought) + 
                   (df['close'] - df['bb_upper']) / (df['bb_upper'] - df['bb_lower']), 
                   0.3, 1.0),
            0.0
        )
        
        df.loc[buy_signal, 'signal_strength'] = buy_strength[buy_signal]
        df.loc[sell_signal, 'signal_strength'] = sell_strength[sell_signal]
        
        return df
    
    def get_strategy_name(self) -> str:
        """返回策略名稱"""
        return f"BollingerBand_Strategy_{self.bb_period}_{self.bb_std}_{self.rsi_oversold}_{self.rsi_overbought}"

class MACDDivergenceStrategy(TradingStrategy):
    """
    MACD 背離策略範例
    
    買入訊號: 價格創新低但 MACD 沒有創新低 (正背離)
    賣出訊號: 價格創新高但 MACD 沒有創新高 (負背離)
    """
    
    def __init__(self, lookback_period=20, min_divergence_strength=0.5):
        """
        初始化策略參數
        
        Args:
            lookback_period: 背離檢測回看期間
            min_divergence_strength: 最小背離強度
        """
        self.lookback_period = lookback_period
        self.min_divergence_strength = min_divergence_strength
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成 MACD 背離訊號"""
        df = data.copy()
        
        # 初始化訊號欄位
        df['signal'] = 0
        df['signal_strength'] = 0.0
        df['signal_source'] = 'MACD_Divergence'
        
        # 計算局部高低點
        df['price_high'] = df['high'].rolling(self.lookback_period, center=True).max()
        df['price_low'] = df['low'].rolling(self.lookback_period, center=True).min()
        df['macd_high'] = df['macd'].rolling(self.lookback_period, center=True).max()
        df['macd_low'] = df['macd'].rolling(self.lookback_period, center=True).min()
        
        # 檢測背離
        bullish_divergence = (
            (df['low'] == df['price_low']) &  # 價格低點
            (df['low'] < df['low'].shift(self.lookback_period)) &  # 價格創新低
            (df['macd'] > df['macd'].shift(self.lookback_period))  # MACD 沒創新低
        )
        
        bearish_divergence = (
            (df['high'] == df['price_high']) &  # 價格高點
            (df['high'] > df['high'].shift(self.lookback_period)) &  # 價格創新高
            (df['macd'] < df['macd'].shift(self.lookback_period))  # MACD 沒創新高
        )
        
        # 設定訊號
        df.loc[bullish_divergence, 'signal'] = 1
        df.loc[bearish_divergence, 'signal'] = -1
        
        # 計算訊號強度 (基於背離程度)
        df.loc[bullish_divergence, 'signal_strength'] = 0.8
        df.loc[bearish_divergence, 'signal_strength'] = 0.8
        
        return df
    
    def get_strategy_name(self) -> str:
        """返回策略名稱"""
        return f"MACD_Divergence_{self.lookback_period}_{self.min_divergence_strength}"

# 如何註冊新策略到系統中
def register_custom_strategies():
    """
    將自定義策略註冊到策略工廠
    
    使用方法:
    1. 在 src/backtesting/backtest_engine.py 的 StrategyFactory 中添加新策略
    2. 或者創建新的策略模組並導入到 main.py
    """
    
    # 示例代碼 (需要添加到 StrategyFactory.create_strategy 方法中):
    """
    strategies = {
        'rsi_macd': RSIMACDStrategy,
        'ma_crossover': MovingAverageCrossoverStrategy,
        'bollinger_band': BollingerBandStrategy,          # 新增
        'macd_divergence': MACDDivergenceStrategy,        # 新增
    }
    """
    
    print("📝 新增策略步驟:")
    print("1. 創建繼承 TradingStrategy 的新類別")
    print("2. 實現 generate_signals() 方法")
    print("3. 實現 get_strategy_name() 方法")
    print("4. 在 StrategyFactory 中註冊策略")
    print("5. 更新 API 文檔中的策略描述")

def test_custom_strategy():
    """測試自定義策略"""
    from src.data_fetcher.us_stocks import USStockDataFetcher
    from src.analysis.technical_indicators import IndicatorAnalyzer
    from src.backtesting.backtest_engine import BacktestEngine, BacktestConfig
    
    print("🧪 測試自定義布林帶策略...")
    
    # 獲取數據
    fetcher = USStockDataFetcher()
    data = fetcher.fetch_historical_data("AAPL", period="6mo")
    
    # 計算技術指標
    analyzer = IndicatorAnalyzer()
    data_with_indicators = analyzer.calculate_all_indicators(data)
    
    # 創建自定義策略
    strategy = BollingerBandStrategy(bb_period=20, bb_std=2)
    
    # 回測
    config = BacktestConfig(initial_capital=100000)
    engine = BacktestEngine(config)
    results = engine.run_backtest(strategy, data_with_indicators, "AAPL")
    
    print(f"✓ 策略測試完成!")
    print(f"  總報酬率: {results.total_return_pct:.2%}")
    print(f"  總交易次數: {results.total_trades}")
    print(f"  勝率: {results.win_rate:.1%}")

if __name__ == "__main__":
    print("🎯 自定義策略開發指南")
    register_custom_strategies()
    print("\n" + "="*50)
    test_custom_strategy()