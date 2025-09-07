"""
Comprehensive backtesting engine for trading strategies
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class BacktestConfig:
    """Configuration for backtesting"""
    initial_capital: float = 10000.0
    commission: float = 0.001  # 0.1% commission per trade
    slippage: float = 0.0005   # 0.05% slippage
    max_positions: int = 10    # Maximum number of concurrent positions
    risk_per_trade: float = 0.02  # 2% risk per trade
    stop_loss_pct: float = 0.02   # 2% stop loss
    take_profit_pct: float = 0.06 # 6% take profit

@dataclass
class Trade:
    """Represents a single trade"""
    symbol: str
    entry_date: datetime
    entry_price: float
    quantity: int
    action: str  # 'BUY' or 'SELL'
    signal_source: str
    signal_strength: float
    
    # Exit information (filled when trade is closed)
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    hold_period: Optional[int] = None
    exit_reason: Optional[str] = None

@dataclass
class Position:
    """Represents a current position"""
    symbol: str
    quantity: int
    entry_price: float
    entry_date: datetime
    current_price: float
    unrealized_pnl: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class BacktestResults:
    """Comprehensive backtest results"""
    # Basic metrics
    total_return: float
    total_return_pct: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    
    # Trade statistics  
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_profit: float
    avg_loss: float
    profit_factor: float
    
    # Risk metrics
    volatility: float
    calmar_ratio: float
    sortino_ratio: float
    var_95: float  # Value at Risk (95%)
    
    # Equity curve
    equity_curve: pd.Series
    
    # Trade history
    trades: List[Trade]
    
    # Monthly/yearly returns
    monthly_returns: pd.Series
    yearly_returns: pd.Series
    
    # Optional fields with defaults
    beta: Optional[float] = None
    alpha: Optional[float] = None
    benchmark_return: Optional[float] = None
    excess_return: Optional[float] = None

class TradingStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals for the given data
        
        Args:
            data: DataFrame with OHLCV data and indicators
            
        Returns:
            DataFrame with additional signal columns
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return the strategy name"""
        pass

class RSIMACDStrategy(TradingStrategy):
    """Combined RSI and MACD strategy"""
    
    def __init__(self, rsi_oversold=30, rsi_overbought=70):
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate RSI + MACD signals"""
        df = data.copy()
        
        # Initialize signal columns
        df['signal'] = 0
        df['signal_strength'] = 0.0
        df['signal_source'] = ''
        
        # RSI signals
        rsi_buy = (df['rsi'] < self.rsi_oversold) & (df['rsi'].shift(1) >= self.rsi_oversold)
        rsi_sell = (df['rsi'] > self.rsi_overbought) & (df['rsi'].shift(1) <= self.rsi_overbought)
        
        # MACD signals
        macd_buy = (df['macd'] > df['macd_signal']) & (df['macd'].shift(1) <= df['macd_signal'].shift(1))
        macd_sell = (df['macd'] < df['macd_signal']) & (df['macd'].shift(1) >= df['macd_signal'].shift(1))
        
        # Combined signals
        buy_signal = rsi_buy | macd_buy
        sell_signal = rsi_sell | macd_sell
        
        df.loc[buy_signal, 'signal'] = 1
        df.loc[sell_signal, 'signal'] = -1
        
        # Calculate signal strength - fix indexing issue
        buy_strength = np.where(
            rsi_buy & macd_buy, 1.0,  # Both signals
            np.where(rsi_buy, 0.7, 0.6)  # RSI stronger than MACD
        )
        df.loc[buy_signal, 'signal_strength'] = buy_strength[buy_signal]
        
        sell_strength = np.where(
            rsi_sell & macd_sell, 1.0,  # Both signals
            np.where(rsi_sell, 0.7, 0.6)  # RSI stronger than MACD
        )
        df.loc[sell_signal, 'signal_strength'] = sell_strength[sell_signal]
        
        # Signal source - fix indexing issue
        buy_source = np.where(
            rsi_buy & macd_buy, 'RSI+MACD',
            np.where(rsi_buy, 'RSI', 'MACD')
        )
        df.loc[buy_signal, 'signal_source'] = buy_source[buy_signal]
        
        sell_source = np.where(
            rsi_sell & macd_sell, 'RSI+MACD',
            np.where(rsi_sell, 'RSI', 'MACD')
        )
        df.loc[sell_signal, 'signal_source'] = sell_source[sell_signal]
        
        return df
    
    def get_strategy_name(self) -> str:
        return f"RSI_MACD_Strategy_{self.rsi_oversold}_{self.rsi_overbought}"

class MovingAverageCrossoverStrategy(TradingStrategy):
    """Moving average crossover strategy"""
    
    def __init__(self, fast_period=20, slow_period=50):
        self.fast_period = fast_period
        self.slow_period = slow_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate moving average crossover signals"""
        df = data.copy()
        
        # Calculate moving averages if not present
        if f'sma_{self.fast_period}' not in df.columns:
            df[f'sma_{self.fast_period}'] = df['close'].rolling(self.fast_period).mean()
        if f'sma_{self.slow_period}' not in df.columns:
            df[f'sma_{self.slow_period}'] = df['close'].rolling(self.slow_period).mean()
        
        fast_ma = df[f'sma_{self.fast_period}']
        slow_ma = df[f'sma_{self.slow_period}']
        
        # Initialize signal columns
        df['signal'] = 0
        df['signal_strength'] = 0.0
        df['signal_source'] = 'MA_Crossover'
        
        # Golden cross (buy signal)
        golden_cross = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
        
        # Death cross (sell signal)  
        death_cross = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))
        
        df.loc[golden_cross, 'signal'] = 1
        df.loc[death_cross, 'signal'] = -1
        
        # Signal strength based on MA spread
        ma_spread = abs(fast_ma - slow_ma) / slow_ma
        df.loc[golden_cross, 'signal_strength'] = np.clip(ma_spread[golden_cross] * 10, 0.3, 1.0)
        df.loc[death_cross, 'signal_strength'] = np.clip(ma_spread[death_cross] * 10, 0.3, 1.0)
        
        return df
    
    def get_strategy_name(self) -> str:
        return f"MA_Crossover_{self.fast_period}_{self.slow_period}"

class BacktestEngine:
    """Comprehensive backtesting engine"""
    
    def __init__(self, config: BacktestConfig = None):
        self.config = config or BacktestConfig()
        self.trades: List[Trade] = []
        self.positions: Dict[str, Position] = {}
        self.equity_curve: List[float] = []
        self.cash = self.config.initial_capital
        self.total_value = self.config.initial_capital
        
    def run_backtest(
        self, 
        strategy: TradingStrategy,
        data: pd.DataFrame,
        symbol: str,
        benchmark_data: Optional[pd.DataFrame] = None
    ) -> BacktestResults:
        """
        Run a complete backtest
        
        Args:
            strategy: Trading strategy to test
            data: Price and indicator data
            symbol: Stock symbol
            benchmark_data: Benchmark data for comparison (optional)
            
        Returns:
            Comprehensive backtest results
        """
        logger.info(f"Starting backtest for {strategy.get_strategy_name()} on {symbol}")
        
        # Reset state
        self._reset_state()
        
        # Generate signals
        data_with_signals = strategy.generate_signals(data)
        
        # Process each trading day
        for i, (timestamp, row) in enumerate(data_with_signals.iterrows()):
            # Create a proper series with the timestamp as name
            row_with_timestamp = row.copy()
            row_with_timestamp.name = timestamp
            self._process_day(row_with_timestamp, symbol)
        
        # Close all remaining positions
        final_row = data_with_signals.iloc[-1]
        final_row.name = data_with_signals.index[-1]  # Ensure the row has the correct timestamp
        self._close_all_positions(final_row)
        
        # Calculate results
        results = self._calculate_results(data_with_signals, benchmark_data)
        
        logger.info(f"Backtest completed. Total return: {results.total_return_pct:.2f}%")
        return results
    
    def _reset_state(self):
        """Reset backtester state"""
        self.trades = []
        self.positions = {}
        self.equity_curve = []
        self.cash = self.config.initial_capital
        self.total_value = self.config.initial_capital
    
    def _process_day(self, row: pd.Series, symbol: str):
        """Process a single trading day"""
        current_price = row['close']
        current_date = row.name
        
        # Update positions with current prices
        self._update_positions(current_price)
        
        # Check for stop loss and take profit
        self._check_exit_conditions(row, symbol)
        
        # Process new signals
        if row['signal'] != 0 and not pd.isna(row['signal']):
            self._process_signal(row, symbol)
        
        # Update equity curve
        self._update_equity_curve()
    
    def _update_positions(self, current_price: float):
        """Update all positions with current market price"""
        for position in self.positions.values():
            position.current_price = current_price
            position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
    
    def _check_exit_conditions(self, row: pd.Series, symbol: str):
        """Check if any positions should be closed due to stop loss or take profit"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        current_price = row['close']
        
        should_exit = False
        exit_reason = ""
        
        # Check stop loss
        if position.stop_loss and current_price <= position.stop_loss:
            should_exit = True
            exit_reason = "stop_loss"
        
        # Check take profit
        elif position.take_profit and current_price >= position.take_profit:
            should_exit = True
            exit_reason = "take_profit"
        
        if should_exit:
            self._close_position(symbol, current_price, row.name, exit_reason)
    
    def _process_signal(self, row: pd.Series, symbol: str):
        """Process a trading signal"""
        signal = row['signal']
        price = row['close']
        date = row.name
        
        if signal > 0:  # Buy signal
            if symbol not in self.positions:
                self._open_position(row, symbol, 'BUY')
        elif signal < 0:  # Sell signal
            if symbol in self.positions:
                self._close_position(symbol, price, date, "signal")
    
    def _open_position(self, row: pd.Series, symbol: str, action: str):
        """Open a new position"""
        price = row['close']
        date = row.name
        
        # Calculate position size based on risk management
        position_value = self._calculate_position_size(price)
        
        if position_value < self.cash:
            quantity = int(position_value / price)
            if quantity > 0:
                # Calculate transaction costs
                transaction_cost = position_value * self.config.commission
                total_cost = position_value + transaction_cost
                
                if total_cost <= self.cash:
                    # Create position
                    self.positions[symbol] = Position(
                        symbol=symbol,
                        quantity=quantity,
                        entry_price=price,
                        entry_date=date,
                        current_price=price,
                        unrealized_pnl=0.0,
                        stop_loss=price * (1 - self.config.stop_loss_pct),
                        take_profit=price * (1 + self.config.take_profit_pct)
                    )
                    
                    # Create trade record
                    trade = Trade(
                        symbol=symbol,
                        entry_date=date,
                        entry_price=price,
                        quantity=quantity,
                        action=action,
                        signal_source=row.get('signal_source', 'unknown'),
                        signal_strength=row.get('signal_strength', 0.0)
                    )
                    self.trades.append(trade)
                    
                    # Update cash
                    self.cash -= total_cost
                    
                    logger.debug(f"Opened {action} position: {quantity} shares of {symbol} at ${price:.2f}")
    
    def _close_position(self, symbol: str, price: float, date: datetime, reason: str):
        """Close an existing position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        # Calculate proceeds
        gross_proceeds = position.quantity * price
        transaction_cost = gross_proceeds * self.config.commission
        net_proceeds = gross_proceeds - transaction_cost
        
        # Calculate profit/loss
        profit_loss = net_proceeds - (position.quantity * position.entry_price)
        profit_loss_pct = profit_loss / (position.quantity * position.entry_price)
        
        # Update trade record
        for trade in reversed(self.trades):
            if trade.symbol == symbol and trade.exit_date is None:
                trade.exit_date = date
                trade.exit_price = price
                trade.profit_loss = profit_loss
                trade.profit_loss_pct = profit_loss_pct
                trade.hold_period = (date - trade.entry_date).days
                trade.exit_reason = reason
                break
        
        # Update cash
        self.cash += net_proceeds
        
        # Remove position
        del self.positions[symbol]
        
        logger.debug(f"Closed position: {symbol} at ${price:.2f}, P&L: ${profit_loss:.2f} ({profit_loss_pct:.2%})")
    
    def _close_all_positions(self, final_row: pd.Series):
        """Close all remaining positions at the end of backtest"""
        symbols_to_close = list(self.positions.keys())
        for symbol in symbols_to_close:
            self._close_position(symbol, final_row['close'], final_row.name, "end_of_backtest")
    
    def _calculate_position_size(self, price: float) -> float:
        """Calculate position size based on risk management rules"""
        # Simple position sizing: risk a fixed percentage of capital
        risk_amount = self.total_value * self.config.risk_per_trade
        stop_loss_distance = price * self.config.stop_loss_pct
        
        if stop_loss_distance > 0:
            shares = risk_amount / stop_loss_distance
            position_value = shares * price
            
            # Don't exceed available cash
            max_position_value = self.cash * 0.9  # Keep 10% cash buffer
            return min(position_value, max_position_value)
        
        return self.cash * 0.1  # Default to 10% of cash
    
    def _update_equity_curve(self):
        """Update the equity curve"""
        positions_value = sum(pos.quantity * pos.current_price for pos in self.positions.values())
        self.total_value = self.cash + positions_value
        self.equity_curve.append(self.total_value)
    
    def _calculate_results(self, data: pd.DataFrame, benchmark_data: Optional[pd.DataFrame]) -> BacktestResults:
        """Calculate comprehensive backtest results"""
        # Ensure we have the right length for equity curve
        if len(self.equity_curve) != len(data):
            # Pad or truncate to match data length
            if len(self.equity_curve) < len(data):
                self.equity_curve.extend([self.equity_curve[-1]] * (len(data) - len(self.equity_curve)))
            else:
                self.equity_curve = self.equity_curve[:len(data)]
        
        equity_series = pd.Series(self.equity_curve, index=data.index)
        
        # Basic metrics
        total_return = self.total_value - self.config.initial_capital
        total_return_pct = total_return / self.config.initial_capital
        
        # Trade statistics
        completed_trades = [t for t in self.trades if t.exit_date is not None]
        winning_trades = [t for t in completed_trades if t.profit_loss > 0]
        losing_trades = [t for t in completed_trades if t.profit_loss < 0]
        
        win_rate = len(winning_trades) / len(completed_trades) if completed_trades else 0
        avg_profit = np.mean([t.profit_loss for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([abs(t.profit_loss) for t in losing_trades]) if losing_trades else 0
        profit_factor = abs(avg_profit / avg_loss) if avg_loss != 0 else 0
        
        # Risk metrics
        returns = equity_series.pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualized
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        max_drawdown, max_drawdown_pct = self._calculate_max_drawdown(equity_series)
        calmar_ratio = total_return_pct / abs(max_drawdown_pct) if max_drawdown_pct != 0 else 0
        sortino_ratio = self._calculate_sortino_ratio(returns)
        var_95 = np.percentile(returns, 5)
        
        # Monthly and yearly returns - fix deprecated frequency
        try:
            monthly_returns = returns.resample('ME').apply(lambda x: (1 + x).prod() - 1) if len(returns) > 0 else pd.Series(dtype=float)
            yearly_returns = returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) if len(returns) > 0 else pd.Series(dtype=float)
        except:
            # Fallback for older pandas versions
            monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1) if len(returns) > 0 else pd.Series(dtype=float)
            yearly_returns = returns.resample('Y').apply(lambda x: (1 + x).prod() - 1) if len(returns) > 0 else pd.Series(dtype=float)
        
        # Benchmark comparison
        benchmark_return = None
        excess_return = None
        beta = None
        alpha = None
        
        if benchmark_data is not None:
            benchmark_returns = benchmark_data['close'].pct_change().dropna()
            benchmark_return = (benchmark_data['close'].iloc[-1] / benchmark_data['close'].iloc[0]) - 1
            excess_return = total_return_pct - benchmark_return
            
            if len(benchmark_returns) == len(returns):
                beta = np.cov(returns, benchmark_returns)[0, 1] / np.var(benchmark_returns)
                alpha = total_return_pct - (benchmark_return * beta)
        
        return BacktestResults(
            total_return=total_return,
            total_return_pct=total_return_pct,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            total_trades=len(completed_trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            avg_profit=avg_profit,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            volatility=volatility,
            beta=beta,
            alpha=alpha,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            calmar_ratio=calmar_ratio,
            sortino_ratio=sortino_ratio,
            var_95=var_95,
            equity_curve=equity_series,
            trades=completed_trades,
            monthly_returns=monthly_returns,
            yearly_returns=yearly_returns
        )
    
    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if returns.std() == 0:
            return 0
        
        excess_returns = returns.mean() * 252 - risk_free_rate  # Annualized
        return excess_returns / (returns.std() * np.sqrt(252))
    
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> Tuple[float, float]:
        """Calculate maximum drawdown"""
        peak = equity_curve.expanding().max()
        drawdown = equity_curve - peak
        max_drawdown = drawdown.min()
        max_drawdown_pct = (drawdown / peak).min()
        
        return max_drawdown, max_drawdown_pct
    
    def _calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio (uses downside deviation instead of total volatility)"""
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return 0
        
        downside_deviation = downside_returns.std() * np.sqrt(252)
        excess_returns = returns.mean() * 252 - risk_free_rate
        
        return excess_returns / downside_deviation if downside_deviation != 0 else 0

# Example usage and strategy factory
class StrategyFactory:
    """Factory for creating trading strategies"""
    
    @staticmethod
    def create_strategy(strategy_name: str, **kwargs) -> TradingStrategy:
        """Create a strategy by name"""
        try:
            # 導入形態策略
            from src.strategies.pattern_strategy import PatternTradingStrategy, EnhancedPatternStrategy
        except ImportError:
            PatternTradingStrategy = None
            EnhancedPatternStrategy = None
        
        strategies = {
            'rsi_macd': RSIMACDStrategy,
            'ma_crossover': MovingAverageCrossoverStrategy,
        }
        
        # 添加形態策略 (如果可用)
        if PatternTradingStrategy:
            strategies['pattern_trading'] = PatternTradingStrategy
            strategies['enhanced_pattern'] = EnhancedPatternStrategy
        
        if strategy_name not in strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(strategies.keys())}")
        
        return strategies[strategy_name](**kwargs)
    
    @staticmethod
    def get_available_strategies() -> List[str]:
        """Get list of available strategies"""
        base_strategies = ['rsi_macd', 'ma_crossover']
        
        try:
            # 檢查形態策略是否可用
            from src.strategies.pattern_strategy import PatternTradingStrategy
            base_strategies.extend(['pattern_trading', 'enhanced_pattern'])
        except ImportError:
            pass
        
        return base_strategies