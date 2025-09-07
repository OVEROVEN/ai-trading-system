#!/usr/bin/env python3
"""
增強版策略回測系統
支援技術形態策略回測和詳細績效分析
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from enum import Enum

from src.analysis.pattern_signals import BuySignalEngine, PatternSignal, PatternType

logger = logging.getLogger(__name__)

class PositionType(Enum):
    """倉位類型"""
    LONG = "long"
    SHORT = "short"
    CASH = "cash"

@dataclass
class Trade:
    """交易記錄"""
    symbol: str
    entry_date: datetime
    exit_date: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    position_type: PositionType
    quantity: float
    entry_signal: str
    exit_signal: Optional[str]
    return_pct: Optional[float] = None
    holding_days: Optional[int] = None
    max_profit: Optional[float] = None
    max_loss: Optional[float] = None

@dataclass
class BacktestResult:
    """回測結果"""
    strategy_name: str
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_return: float
    avg_holding_days: float
    best_trade: float
    worst_trade: float
    trades: List[Trade]
    daily_returns: pd.Series
    equity_curve: pd.Series
    detailed_stats: Dict[str, Any]

class PatternBasedStrategy:
    """基於技術形態的交易策略"""
    
    def __init__(self, 
                 pattern_types: List[PatternType] = None,
                 min_confidence: float = 60.0,
                 risk_reward_ratio: float = 2.0,
                 max_holding_days: int = 30,
                 stop_loss_pct: float = 0.05):
        """
        初始化形態策略
        
        Args:
            pattern_types: 允許的形態類型
            min_confidence: 最小信心度
            risk_reward_ratio: 最小風險報酬比
            max_holding_days: 最大持有天數
            stop_loss_pct: 停損比例
        """
        self.pattern_types = pattern_types or [
            PatternType.RECTANGLE, 
            PatternType.ASCENDING_TRIANGLE,
            PatternType.BULL_FLAG,
            PatternType.BULL_PENNANT,
            PatternType.FALLING_WEDGE
        ]
        self.min_confidence = min_confidence
        self.risk_reward_ratio = risk_reward_ratio
        self.max_holding_days = max_holding_days
        self.stop_loss_pct = stop_loss_pct
        self.signal_engine = BuySignalEngine()
        
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        生成交易訊號
        
        Args:
            df: 股價數據
            
        Returns:
            交易訊號序列 (1=買進, -1=賣出, 0=持有)
        """
        signals = pd.Series(0, index=df.index)
        
        try:
            # 滾動窗口分析形態
            for i in range(30, len(df)):
                window_data = df.iloc[i-30:i+1]
                
                # 生成買進訊號
                signal_result = self.signal_engine.generate_buy_signals("TEMP", window_data)
                
                if 'pattern_signals' in signal_result:
                    for pattern_dict in signal_result['pattern_signals']:
                        if self._is_valid_signal(pattern_dict):
                            signals.iloc[i] = 1  # 買進訊號
                            break
                            
        except Exception as e:
            logger.error(f"生成訊號錯誤: {e}")
            
        return signals
    
    def _is_valid_signal(self, pattern_dict: Dict[str, Any]) -> bool:
        """檢查訊號是否有效"""
        try:
            pattern_type = PatternType(pattern_dict.get('pattern_type'))
            confidence = pattern_dict.get('confidence', 0)
            risk_reward = pattern_dict.get('risk_reward_ratio', 0)
            
            return (pattern_type in self.pattern_types and 
                    confidence >= self.min_confidence and 
                    risk_reward >= self.risk_reward_ratio)
                    
        except (ValueError, KeyError):
            return False

class StrategyBacktester:
    """策略回測引擎"""
    
    def __init__(self, initial_capital: float = 100000.0, commission: float = 0.001):
        """
        初始化回測引擎
        
        Args:
            initial_capital: 初始資金
            commission: 手續費率
        """
        self.initial_capital = initial_capital
        self.commission = commission
        
    def run_backtest(self, 
                     df: pd.DataFrame, 
                     strategy, 
                     symbol: str = "UNKNOWN",
                     strategy_name: str = "Pattern Strategy") -> BacktestResult:
        """
        執行策略回測
        
        Args:
            df: 股價數據
            strategy: 交易策略
            symbol: 股票代號
            strategy_name: 策略名稱
            
        Returns:
            回測結果
        """
        try:
            # 生成交易訊號
            signals = strategy.generate_signals(df)
            
            # 執行交易模擬
            trades, equity_curve = self._simulate_trading(df, signals, strategy)
            
            # 計算績效指標
            result = self._calculate_performance(
                trades, equity_curve, df, symbol, strategy_name
            )
            
            logger.info(f"回測完成: {strategy_name} - 總報酬: {result.total_return:.2%}")
            return result
            
        except Exception as e:
            logger.error(f"回測執行錯誤: {e}")
            raise
    
    def _simulate_trading(self, 
                         df: pd.DataFrame, 
                         signals: pd.Series, 
                         strategy) -> Tuple[List[Trade], pd.Series]:
        """
        模擬交易執行
        
        Args:
            df: 股價數據
            signals: 交易訊號
            strategy: 交易策略
            
        Returns:
            交易記錄列表和權益曲線
        """
        trades = []
        current_position = None
        cash = self.initial_capital
        equity_values = []
        
        for i, (date, row) in enumerate(df.iterrows()):
            current_price = row['close']
            signal = signals.iloc[i] if i < len(signals) else 0
            
            # 計算當前權益
            if current_position:
                position_value = current_position.quantity * current_price
                current_equity = cash + position_value
            else:
                current_equity = cash
            
            equity_values.append(current_equity)
            
            # 處理交易訊號
            if signal == 1 and current_position is None:  # 買進訊號
                # 開倉
                quantity = (cash * 0.95) / current_price  # 保留5%現金
                transaction_cost = quantity * current_price * self.commission
                
                current_position = Trade(
                    symbol=df.attrs.get('symbol', 'UNKNOWN'),
                    entry_date=date,
                    exit_date=None,
                    entry_price=current_price,
                    exit_price=None,
                    position_type=PositionType.LONG,
                    quantity=quantity,
                    entry_signal="Pattern Signal",
                    exit_signal=None
                )
                
                cash -= (quantity * current_price + transaction_cost)
                
            elif current_position is not None:  # 檢查出場條件
                # 計算持有天數
                holding_days = (date - current_position.entry_date).days
                
                # 停損檢查
                unrealized_return = (current_price - current_position.entry_price) / current_position.entry_price
                
                should_exit = False
                exit_reason = ""
                
                # 停損條件
                if unrealized_return <= -strategy.stop_loss_pct:
                    should_exit = True
                    exit_reason = "Stop Loss"
                
                # 最大持有天數
                elif holding_days >= strategy.max_holding_days:
                    should_exit = True
                    exit_reason = "Max Holding Days"
                
                # 技術止盈（可以根據需要添加更多條件）
                elif unrealized_return >= 0.15:  # 15%止盈
                    should_exit = True
                    exit_reason = "Take Profit"
                
                if should_exit:
                    # 平倉
                    transaction_cost = current_position.quantity * current_price * self.commission
                    cash += (current_position.quantity * current_price - transaction_cost)
                    
                    # 完成交易記錄
                    current_position.exit_date = date
                    current_position.exit_price = current_price
                    current_position.exit_signal = exit_reason
                    current_position.return_pct = unrealized_return
                    current_position.holding_days = holding_days
                    
                    trades.append(current_position)
                    current_position = None
        
        # 如果最後還有持倉，強制平倉
        if current_position:
            final_price = df['close'].iloc[-1]
            final_date = df.index[-1]
            
            cash += current_position.quantity * final_price
            current_position.exit_date = final_date
            current_position.exit_price = final_price
            current_position.exit_signal = "End of Period"
            current_position.return_pct = (final_price - current_position.entry_price) / current_position.entry_price
            current_position.holding_days = (final_date - current_position.entry_date).days
            
            trades.append(current_position)
        
        equity_curve = pd.Series(equity_values, index=df.index)
        return trades, equity_curve
    
    def _calculate_performance(self, 
                              trades: List[Trade], 
                              equity_curve: pd.Series, 
                              df: pd.DataFrame, 
                              symbol: str, 
                              strategy_name: str) -> BacktestResult:
        """計算績效指標"""
        try:
            # 基本指標
            final_capital = equity_curve.iloc[-1]
            total_return = (final_capital - self.initial_capital) / self.initial_capital
            
            # 年化報酬率
            days = (df.index[-1] - df.index[0]).days
            annual_return = (1 + total_return) ** (365.25 / days) - 1 if days > 0 else 0
            
            # 日報酬率
            daily_returns = equity_curve.pct_change().dropna()
            
            # 最大回撤
            rolling_max = equity_curve.expanding().max()
            drawdown = (equity_curve - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # 夏普比率和索丁諾比率
            excess_returns = daily_returns - 0.02/252  # 假設無風險利率2%
            sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
            
            negative_returns = excess_returns[excess_returns < 0]
            sortino_ratio = excess_returns.mean() / negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 and negative_returns.std() > 0 else 0
            
            # 交易統計
            if trades:
                winning_trades = [t for t in trades if t.return_pct > 0]
                losing_trades = [t for t in trades if t.return_pct <= 0]
                
                win_rate = len(winning_trades) / len(trades)
                avg_trade_return = np.mean([t.return_pct for t in trades])
                avg_holding_days = np.mean([t.holding_days for t in trades])
                best_trade = max([t.return_pct for t in trades])
                worst_trade = min([t.return_pct for t in trades])
                
                # 獲利因子
                total_profit = sum([t.return_pct for t in winning_trades]) if winning_trades else 0
                total_loss = abs(sum([t.return_pct for t in losing_trades])) if losing_trades else 0.001
                profit_factor = total_profit / total_loss if total_loss > 0 else 0
                
            else:
                win_rate = 0
                avg_trade_return = 0
                avg_holding_days = 0
                best_trade = 0
                worst_trade = 0
                profit_factor = 0
            
            # 詳細統計
            detailed_stats = {
                "volatility": daily_returns.std() * np.sqrt(252),
                "calmar_ratio": annual_return / abs(max_drawdown) if max_drawdown != 0 else 0,
                "recovery_factor": total_return / abs(max_drawdown) if max_drawdown != 0 else 0,
                "profit_factor": profit_factor,
                "expectancy": avg_trade_return,
                "winning_trades": len([t for t in trades if t.return_pct > 0]),
                "losing_trades": len([t for t in trades if t.return_pct <= 0]),
                "largest_winning_streak": self._calculate_largest_streak(trades, True),
                "largest_losing_streak": self._calculate_largest_streak(trades, False),
                "avg_win": np.mean([t.return_pct for t in trades if t.return_pct > 0]) if any(t.return_pct > 0 for t in trades) else 0,
                "avg_loss": np.mean([t.return_pct for t in trades if t.return_pct <= 0]) if any(t.return_pct <= 0 for t in trades) else 0
            }
            
            return BacktestResult(
                strategy_name=strategy_name,
                symbol=symbol,
                start_date=df.index[0],
                end_date=df.index[-1],
                initial_capital=self.initial_capital,
                final_capital=final_capital,
                total_return=total_return,
                annual_return=annual_return,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                win_rate=win_rate,
                profit_factor=profit_factor,
                total_trades=len(trades),
                avg_trade_return=avg_trade_return,
                avg_holding_days=avg_holding_days,
                best_trade=best_trade,
                worst_trade=worst_trade,
                trades=trades,
                daily_returns=daily_returns,
                equity_curve=equity_curve,
                detailed_stats=detailed_stats
            )
            
        except Exception as e:
            logger.error(f"績效計算錯誤: {e}")
            raise
    
    def _calculate_largest_streak(self, trades: List[Trade], winning: bool) -> int:
        """計算最長連勝/連敗紀錄"""
        if not trades:
            return 0
            
        max_streak = 0
        current_streak = 0
        
        for trade in trades:
            if (winning and trade.return_pct > 0) or (not winning and trade.return_pct <= 0):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
                
        return max_streak
    
    def compare_strategies(self, results: List[BacktestResult]) -> Dict[str, Any]:
        """比較多個策略結果"""
        try:
            comparison = {
                "strategies": [],
                "summary": {},
                "rankings": {}
            }
            
            for result in results:
                strategy_data = {
                    "name": result.strategy_name,
                    "total_return": result.total_return,
                    "annual_return": result.annual_return,
                    "max_drawdown": result.max_drawdown,
                    "sharpe_ratio": result.sharpe_ratio,
                    "win_rate": result.win_rate,
                    "total_trades": result.total_trades,
                    "profit_factor": result.profit_factor
                }
                comparison["strategies"].append(strategy_data)
            
            # 排名
            metrics = ["total_return", "annual_return", "sharpe_ratio", "win_rate", "profit_factor"]
            for metric in metrics:
                sorted_strategies = sorted(results, key=lambda x: getattr(x, metric), reverse=True)
                comparison["rankings"][metric] = [s.strategy_name for s in sorted_strategies]
            
            # 摘要統計
            comparison["summary"] = {
                "best_total_return": max(results, key=lambda x: x.total_return).strategy_name,
                "best_sharpe_ratio": max(results, key=lambda x: x.sharpe_ratio).strategy_name,
                "lowest_drawdown": min(results, key=lambda x: abs(x.max_drawdown)).strategy_name,
                "highest_win_rate": max(results, key=lambda x: x.win_rate).strategy_name
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"策略比較錯誤: {e}")
            return {"error": str(e)}

class PerformanceAnalyzer:
    """績效分析器"""
    
    @staticmethod
    def generate_performance_report(result: BacktestResult) -> Dict[str, Any]:
        """生成詳細績效報告"""
        try:
            report = {
                "basic_stats": {
                    "策略名稱": result.strategy_name,
                    "股票代號": result.symbol,
                    "回測期間": f"{result.start_date.strftime('%Y-%m-%d')} 至 {result.end_date.strftime('%Y-%m-%d')}",
                    "初始資金": f"${result.initial_capital:,.2f}",
                    "最終資金": f"${result.final_capital:,.2f}",
                    "總報酬率": f"{result.total_return:.2%}",
                    "年化報酬率": f"{result.annual_return:.2%}",
                    "最大回撤": f"{result.max_drawdown:.2%}",
                    "夏普比率": f"{result.sharpe_ratio:.2f}",
                    "索丁諾比率": f"{result.sortino_ratio:.2f}"
                },
                "trading_stats": {
                    "總交易次數": result.total_trades,
                    "勝率": f"{result.win_rate:.2%}",
                    "獲利因子": f"{result.profit_factor:.2f}",
                    "平均交易報酬": f"{result.avg_trade_return:.2%}",
                    "平均持有天數": f"{result.avg_holding_days:.1f}天",
                    "最佳交易": f"{result.best_trade:.2%}",
                    "最差交易": f"{result.worst_trade:.2%}"
                },
                "advanced_metrics": result.detailed_stats,
                "risk_metrics": {
                    "波動率": f"{result.detailed_stats.get('volatility', 0):.2%}",
                    "卡瑪比率": f"{result.detailed_stats.get('calmar_ratio', 0):.2f}",
                    "恢復因子": f"{result.detailed_stats.get('recovery_factor', 0):.2f}",
                    "最長連勝": f"{result.detailed_stats.get('largest_winning_streak', 0)}次",
                    "最長連敗": f"{result.detailed_stats.get('largest_losing_streak', 0)}次"
                }
            }
            
            # 交易明細
            if result.trades:
                report["trade_details"] = [
                    {
                        "進場日期": trade.entry_date.strftime('%Y-%m-%d'),
                        "出場日期": trade.exit_date.strftime('%Y-%m-%d') if trade.exit_date else "持有中",
                        "進場價格": f"${trade.entry_price:.2f}",
                        "出場價格": f"${trade.exit_price:.2f}" if trade.exit_price else "N/A",
                        "報酬率": f"{trade.return_pct:.2%}" if trade.return_pct else "N/A",
                        "持有天數": f"{trade.holding_days}天" if trade.holding_days else "N/A",
                        "出場原因": trade.exit_signal or "N/A"
                    }
                    for trade in result.trades[-10:]  # 顯示最近10筆交易
                ]
            
            return report
            
        except Exception as e:
            logger.error(f"生成績效報告錯誤: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def analyze_monthly_returns(equity_curve: pd.Series) -> pd.DataFrame:
        """分析月度報酬"""
        try:
            monthly_returns = equity_curve.resample('M').last().pct_change().dropna()
            
            analysis = pd.DataFrame({
                "月度報酬": monthly_returns,
                "累積報酬": (1 + monthly_returns).cumprod() - 1
            })
            
            analysis["年月"] = analysis.index.strftime('%Y-%m')
            return analysis
            
        except Exception as e:
            logger.error(f"月度報酬分析錯誤: {e}")
            return pd.DataFrame()

# 預設策略實例
default_pattern_strategy = PatternBasedStrategy(
    min_confidence=65.0,
    risk_reward_ratio=1.5,
    max_holding_days=20,
    stop_loss_pct=0.08
)

def run_pattern_backtest(df: pd.DataFrame, 
                        symbol: str = "UNKNOWN",
                        strategy: PatternBasedStrategy = None) -> BacktestResult:
    """
    執行形態策略回測的便利函數
    
    Args:
        df: 股價數據
        symbol: 股票代號
        strategy: 策略實例，如果未提供則使用預設策略
        
    Returns:
        回測結果
    """
    if strategy is None:
        strategy = default_pattern_strategy
    
    backtester = StrategyBacktester()
    return backtester.run_backtest(df, strategy, symbol, "Pattern Based Strategy")