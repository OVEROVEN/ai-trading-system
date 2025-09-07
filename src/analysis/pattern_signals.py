#!/usr/bin/env python3
"""
技術分析形態識別與買進訊號系統
專門識別箱型、楔型、三角形、旗型等技術形態並生成買進訊號
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PatternType(Enum):
    """技術形態類型"""
    RECTANGLE = "rectangle"  # 箱型整理
    ASCENDING_TRIANGLE = "ascending_triangle"  # 上升三角形
    DESCENDING_TRIANGLE = "descending_triangle"  # 下降三角形
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"  # 對稱三角形
    RISING_WEDGE = "rising_wedge"  # 上升楔型
    FALLING_WEDGE = "falling_wedge"  # 下降楔型
    BULL_FLAG = "bull_flag"  # 牛市旗型
    BEAR_FLAG = "bear_flag"  # 熊市旗型
    BULL_PENNANT = "bull_pennant"  # 牛市三角旗
    BEAR_PENNANT = "bear_pennant"  # 熊市三角旗

class SignalStrength(Enum):
    """訊號強度"""
    WEAK = "weak"
    MODERATE = "moderate" 
    STRONG = "strong"
    VERY_STRONG = "very_strong"

@dataclass
class PatternSignal:
    """形態訊號數據類"""
    pattern_type: PatternType
    signal_strength: SignalStrength
    confidence: float  # 信心度 0-100%
    entry_price: float  # 建議進場價
    target_price: float  # 目標價
    stop_loss: float  # 停損價
    risk_reward_ratio: float  # 風險報酬比
    pattern_start: datetime
    pattern_end: datetime
    breakout_point: Optional[float] = None
    volume_confirmation: bool = False
    description: str = ""
    technical_details: Dict[str, Any] = None

class TechnicalPatternAnalyzer:
    """技術形態分析器"""
    
    def __init__(self, min_pattern_days: int = 5, max_pattern_days: int = 50):
        self.min_pattern_days = min_pattern_days
        self.max_pattern_days = max_pattern_days
        
    def analyze_patterns(self, df: pd.DataFrame) -> List[PatternSignal]:
        """
        分析股價數據中的技術形態
        
        Args:
            df: 包含OHLCV數據的DataFrame
            
        Returns:
            識別到的形態訊號列表
        """
        signals = []
        
        try:
            # 確保數據充足
            if len(df) < self.min_pattern_days:
                return signals
                
            # 計算技術指標
            df = self._calculate_indicators(df)
            
            # 識別各種形態
            signals.extend(self._detect_rectangles(df))
            signals.extend(self._detect_triangles(df))
            signals.extend(self._detect_wedges(df))
            signals.extend(self._detect_flags_pennants(df))
            
            # 按信心度排序
            signals.sort(key=lambda x: x.confidence, reverse=True)
            
            logger.info(f"識別到 {len(signals)} 個技術形態訊號")
            
        except Exception as e:
            logger.error(f"形態分析錯誤: {e}")
            
        return signals
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """計算技術指標"""
        df = df.copy()
        
        # 移動平均線
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA50'] = df['close'].rolling(window=50).mean()
        
        # 布林通道
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        
        # RSI
        df['RSI'] = self._calculate_rsi(df['close'])
        
        # 成交量移動平均
        df['volume_MA'] = df['volume'].rolling(window=20).mean()
        
        # 價格波動度
        df['volatility'] = df['close'].rolling(window=20).std()
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """計算RSI指標"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _detect_rectangles(self, df: pd.DataFrame) -> List[PatternSignal]:
        """檢測箱型整理形態"""
        signals = []
        
        try:
            for i in range(self.min_pattern_days, min(len(df), self.max_pattern_days)):
                period_data = df.iloc[-i:]
                
                # 尋找水平支撐和阻力
                highs = period_data['high'].values
                lows = period_data['low'].values
                
                # 計算阻力位和支撐位
                resistance_level = np.percentile(highs, 95)
                support_level = np.percentile(lows, 5)
                
                # 檢查是否形成箱型
                if self._is_rectangle_pattern(period_data, support_level, resistance_level):
                    signal = self._create_rectangle_signal(period_data, support_level, resistance_level)
                    if signal:
                        signals.append(signal)
                        
        except Exception as e:
            logger.error(f"箱型檢測錯誤: {e}")
            
        return signals
    
    def _is_rectangle_pattern(self, data: pd.DataFrame, support: float, resistance: float) -> bool:
        """判斷是否為箱型形態"""
        try:
            # 箱型條件
            box_height = resistance - support
            price_range = data['high'].max() - data['low'].min()
            
            # 箱型高度應占總價格範圍的合理比例
            if box_height / price_range < 0.3 or box_height / price_range > 0.8:
                return False
                
            # 檢查價格是否在箱型範圍內震盪
            touches_resistance = (data['high'] >= resistance * 0.98).sum()
            touches_support = (data['low'] <= support * 1.02).sum()
            
            # 至少需要觸及支撐和阻力各2次
            return touches_resistance >= 2 and touches_support >= 2
            
        except Exception:
            return False
    
    def _create_rectangle_signal(self, data: pd.DataFrame, support: float, resistance: float) -> Optional[PatternSignal]:
        """創建箱型訊號"""
        try:
            current_price = data['close'].iloc[-1]
            
            # 判斷突破方向
            if current_price > resistance * 0.99:  # 向上突破
                target_price = resistance + (resistance - support)
                stop_loss = support
                signal_strength = SignalStrength.MODERATE
                confidence = 70.0
                
            elif current_price < support * 1.01:  # 向下突破（空頭訊號，暫不處理）
                return None
                
            else:  # 在箱型內，等待突破
                target_price = resistance + (resistance - support) * 0.5
                stop_loss = support
                signal_strength = SignalStrength.WEAK
                confidence = 50.0
            
            # 成交量確認
            recent_volume = data['volume'].iloc[-5:].mean()
            avg_volume = data['volume_MA'].iloc[-1] if 'volume_MA' in data.columns else data['volume'].mean()
            volume_confirmation = recent_volume > avg_volume * 1.2
            
            risk_reward = (target_price - current_price) / (current_price - stop_loss) if current_price > stop_loss else 0
            
            return PatternSignal(
                pattern_type=PatternType.RECTANGLE,
                signal_strength=signal_strength,
                confidence=confidence + (10 if volume_confirmation else 0),
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                risk_reward_ratio=risk_reward,
                pattern_start=data.index[0],
                pattern_end=data.index[-1],
                breakout_point=resistance if current_price > resistance * 0.99 else None,
                volume_confirmation=volume_confirmation,
                description=f"箱型整理 (支撐: ${support:.2f}, 阻力: ${resistance:.2f})",
                technical_details={
                    "support_level": support,
                    "resistance_level": resistance,
                    "box_height": resistance - support,
                    "current_position": "突破" if current_price > resistance * 0.99 else "整理中"
                }
            )
            
        except Exception as e:
            logger.error(f"創建箱型訊號錯誤: {e}")
            return None
    
    def _detect_triangles(self, df: pd.DataFrame) -> List[PatternSignal]:
        """檢測三角形形態"""
        signals = []
        
        try:
            for i in range(self.min_pattern_days, min(len(df), self.max_pattern_days)):
                period_data = df.iloc[-i:]
                
                # 尋找高點和低點趨勢線
                triangle_type = self._identify_triangle_type(period_data)
                
                if triangle_type:
                    signal = self._create_triangle_signal(period_data, triangle_type)
                    if signal:
                        signals.append(signal)
                        
        except Exception as e:
            logger.error(f"三角形檢測錯誤: {e}")
            
        return signals
    
    def _identify_triangle_type(self, data: pd.DataFrame) -> Optional[PatternType]:
        """識別三角形類型"""
        try:
            if len(data) < 10:
                return None
                
            # 計算高點和低點的趨勢
            highs = data['high'].rolling(window=3).max()
            lows = data['low'].rolling(window=3).min()
            
            # 找出相對高點和低點
            high_peaks = self._find_peaks(highs.values)
            low_peaks = self._find_peaks(-lows.values)
            
            if len(high_peaks) < 2 or len(low_peaks) < 2:
                return None
            
            # 計算趨勢線斜率
            high_slope = self._calculate_trendline_slope(high_peaks, highs.iloc[high_peaks].values)
            low_slope = self._calculate_trendline_slope(low_peaks, lows.iloc[low_peaks].values)
            
            # 判斷三角形類型
            if abs(high_slope) < 0.001:  # 水平阻力線
                if low_slope > 0.001:
                    return PatternType.ASCENDING_TRIANGLE
            elif abs(low_slope) < 0.001:  # 水平支撐線
                if high_slope < -0.001:
                    return PatternType.DESCENDING_TRIANGLE
            elif high_slope < -0.001 and low_slope > 0.001:  # 趨勢線收斂
                return PatternType.SYMMETRICAL_TRIANGLE
                
            return None
            
        except Exception:
            return None
    
    def _find_peaks(self, data: np.ndarray, prominence: float = 0.1) -> List[int]:
        """尋找波峰"""
        peaks = []
        for i in range(1, len(data) - 1):
            if data[i] > data[i-1] and data[i] > data[i+1]:
                peaks.append(i)
        return peaks
    
    def _calculate_trendline_slope(self, x_points: List[int], y_points: np.ndarray) -> float:
        """計算趨勢線斜率"""
        if len(x_points) < 2:
            return 0
        try:
            x = np.array(x_points)
            y = np.array(y_points)
            slope, _ = np.polyfit(x, y, 1)
            return slope
        except:
            return 0
    
    def _create_triangle_signal(self, data: pd.DataFrame, triangle_type: PatternType) -> Optional[PatternSignal]:
        """創建三角形訊號"""
        try:
            current_price = data['close'].iloc[-1]
            
            # 根據三角形類型設定參數
            if triangle_type == PatternType.ASCENDING_TRIANGLE:
                resistance = data['high'].rolling(window=5).max().iloc[-10:].max()
                target_price = resistance + (resistance - data['low'].min()) * 0.6
                stop_loss = data['low'].rolling(window=10).min().iloc[-1]
                confidence = 75.0
                signal_strength = SignalStrength.STRONG
                description = "上升三角形突破"
                
            elif triangle_type == PatternType.SYMMETRICAL_TRIANGLE:
                price_range = data['high'].max() - data['low'].min()
                target_price = current_price + price_range * 0.5
                stop_loss = current_price - price_range * 0.3
                confidence = 65.0
                signal_strength = SignalStrength.MODERATE
                description = "對稱三角形整理"
                
            else:  # DESCENDING_TRIANGLE - 通常為看跌形態
                return None
            
            risk_reward = (target_price - current_price) / (current_price - stop_loss) if current_price > stop_loss else 0
            
            return PatternSignal(
                pattern_type=triangle_type,
                signal_strength=signal_strength,
                confidence=confidence,
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                risk_reward_ratio=risk_reward,
                pattern_start=data.index[0],
                pattern_end=data.index[-1],
                volume_confirmation=False,  # 需要進一步實現
                description=description,
                technical_details={
                    "triangle_type": triangle_type.value,
                    "price_range": data['high'].max() - data['low'].min()
                }
            )
            
        except Exception as e:
            logger.error(f"創建三角形訊號錯誤: {e}")
            return None
    
    def _detect_wedges(self, df: pd.DataFrame) -> List[PatternSignal]:
        """檢測楔型形態"""
        signals = []
        
        try:
            for i in range(15, min(len(df), self.max_pattern_days)):
                period_data = df.iloc[-i:]
                
                wedge_type = self._identify_wedge_type(period_data)
                if wedge_type:
                    signal = self._create_wedge_signal(period_data, wedge_type)
                    if signal:
                        signals.append(signal)
                        
        except Exception as e:
            logger.error(f"楔型檢測錯誤: {e}")
            
        return signals
    
    def _identify_wedge_type(self, data: pd.DataFrame) -> Optional[PatternType]:
        """識別楔型類型"""
        try:
            if len(data) < 15:
                return None
                
            # 計算高點和低點趨勢線
            highs = data['high'].rolling(window=3).max()
            lows = data['low'].rolling(window=3).min()
            
            high_peaks = self._find_peaks(highs.values)
            low_peaks = self._find_peaks(-lows.values)
            
            if len(high_peaks) < 3 or len(low_peaks) < 3:
                return None
            
            # 計算趨勢線斜率
            high_slope = self._calculate_trendline_slope(high_peaks[-3:], highs.iloc[high_peaks[-3:]].values)
            low_slope = self._calculate_trendline_slope(low_peaks[-3:], lows.iloc[low_peaks[-3:]].values)
            
            # 楔型特徵：趨勢線同向且收斂
            if high_slope > 0.001 and low_slope > 0.001 and high_slope > low_slope:
                return PatternType.RISING_WEDGE  # 通常看跌
            elif high_slope < -0.001 and low_slope < -0.001 and abs(high_slope) > abs(low_slope):
                return PatternType.FALLING_WEDGE  # 通常看漲
                
            return None
            
        except Exception:
            return None
    
    def _create_wedge_signal(self, data: pd.DataFrame, wedge_type: PatternType) -> Optional[PatternSignal]:
        """創建楔型訊號"""
        try:
            current_price = data['close'].iloc[-1]
            
            if wedge_type == PatternType.FALLING_WEDGE:  # 看漲楔型
                price_range = data['high'].max() - data['low'].min()
                target_price = current_price + price_range * 0.8
                stop_loss = data['low'].rolling(window=10).min().iloc[-1]
                confidence = 70.0
                signal_strength = SignalStrength.MODERATE
                description = "下降楔型（看漲突破）"
                
            else:  # RISING_WEDGE - 通常看跌，不適合買進訊號
                return None
            
            risk_reward = (target_price - current_price) / (current_price - stop_loss) if current_price > stop_loss else 0
            
            return PatternSignal(
                pattern_type=wedge_type,
                signal_strength=signal_strength,
                confidence=confidence,
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                risk_reward_ratio=risk_reward,
                pattern_start=data.index[0],
                pattern_end=data.index[-1],
                volume_confirmation=False,
                description=description,
                technical_details={
                    "wedge_type": wedge_type.value,
                    "price_range": data['high'].max() - data['low'].min()
                }
            )
            
        except Exception as e:
            logger.error(f"創建楔型訊號錯誤: {e}")
            return None
    
    def _detect_flags_pennants(self, df: pd.DataFrame) -> List[PatternSignal]:
        """檢測旗型和三角旗形態"""
        signals = []
        
        try:
            # 旗型通常在強勢趨勢後出現短期整理
            for i in range(10, 30):  # 旗型持續時間較短
                if i > len(df):
                    continue
                    
                period_data = df.iloc[-i:]
                pre_trend_data = df.iloc[-i-20:-i] if len(df) > i+20 else df.iloc[:-i]
                
                flag_type = self._identify_flag_type(pre_trend_data, period_data)
                if flag_type:
                    signal = self._create_flag_signal(period_data, flag_type, pre_trend_data)
                    if signal:
                        signals.append(signal)
                        
        except Exception as e:
            logger.error(f"旗型檢測錯誤: {e}")
            
        return signals
    
    def _identify_flag_type(self, pre_trend: pd.DataFrame, flag_data: pd.DataFrame) -> Optional[PatternType]:
        """識別旗型類型"""
        try:
            if len(pre_trend) < 10 or len(flag_data) < 5:
                return None
            
            # 檢查前期趨勢強度
            trend_change = (pre_trend['close'].iloc[-1] - pre_trend['close'].iloc[0]) / pre_trend['close'].iloc[0]
            
            # 旗型需要明顯的前期趨勢（至少5%的漲幅）
            if trend_change > 0.05:  # 上升趨勢後的旗型
                # 檢查旗型整理期的特徵
                flag_volatility = flag_data['close'].std() / flag_data['close'].mean()
                
                if flag_volatility < 0.05:  # 低波動整理
                    return PatternType.BULL_FLAG
                elif self._is_triangular_consolidation(flag_data):
                    return PatternType.BULL_PENNANT
                    
            return None
            
        except Exception:
            return None
    
    def _is_triangular_consolidation(self, data: pd.DataFrame) -> bool:
        """檢查是否為三角形整理"""
        try:
            if len(data) < 5:
                return False
                
            # 簡單檢查：價格區間是否逐漸收窄
            early_range = data['high'].iloc[:3].max() - data['low'].iloc[:3].min()
            late_range = data['high'].iloc[-3:].max() - data['low'].iloc[-3:].min()
            
            return late_range < early_range * 0.7
            
        except Exception:
            return False
    
    def _create_flag_signal(self, flag_data: pd.DataFrame, flag_type: PatternType, pre_trend: pd.DataFrame) -> Optional[PatternSignal]:
        """創建旗型訊號"""
        try:
            current_price = flag_data['close'].iloc[-1]
            
            if flag_type in [PatternType.BULL_FLAG, PatternType.BULL_PENNANT]:
                # 旗型突破目標：旗桿高度加上突破點
                flagpole_height = pre_trend['close'].iloc[-1] - pre_trend['close'].iloc[0]
                breakout_level = flag_data['high'].max()
                target_price = breakout_level + flagpole_height
                stop_loss = flag_data['low'].min()
                confidence = 80.0  # 旗型通常是可靠的繼續形態
                signal_strength = SignalStrength.STRONG
                
                description = "牛市旗型" if flag_type == PatternType.BULL_FLAG else "牛市三角旗"
                
            else:
                return None  # 暫不處理熊市旗型
            
            risk_reward = (target_price - current_price) / (current_price - stop_loss) if current_price > stop_loss else 0
            
            return PatternSignal(
                pattern_type=flag_type,
                signal_strength=signal_strength,
                confidence=confidence,
                entry_price=current_price,
                target_price=target_price,
                stop_loss=stop_loss,
                risk_reward_ratio=risk_reward,
                pattern_start=flag_data.index[0],
                pattern_end=flag_data.index[-1],
                volume_confirmation=False,
                description=description,
                technical_details={
                    "flag_type": flag_type.value,
                    "flagpole_height": flagpole_height,
                    "breakout_level": breakout_level
                }
            )
            
        except Exception as e:
            logger.error(f"創建旗型訊號錯誤: {e}")
            return None

class BuySignalEngine:
    """買進訊號引擎"""
    
    def __init__(self):
        self.pattern_analyzer = TechnicalPatternAnalyzer()
        
    def generate_buy_signals(self, symbol: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        生成綜合買進訊號
        
        Args:
            symbol: 股票代號
            df: 股價數據
            
        Returns:
            包含所有訊號的字典
        """
        try:
            # 技術形態分析
            pattern_signals = self.pattern_analyzer.analyze_patterns(df)
            
            # 基本技術指標訊號
            indicator_signals = self._analyze_indicators(df)
            
            # 綜合評分
            overall_signal = self._calculate_overall_signal(pattern_signals, indicator_signals)
            
            return {
                "symbol": symbol,
                "timestamp": datetime.now(),
                "pattern_signals": [self._signal_to_dict(s) for s in pattern_signals],
                "indicator_signals": indicator_signals,
                "overall_signal": overall_signal,
                "summary": self._generate_signal_summary(pattern_signals, indicator_signals, overall_signal)
            }
            
        except Exception as e:
            logger.error(f"生成買進訊號錯誤: {e}")
            return {"error": str(e)}
    
    def _analyze_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析基本技術指標"""
        try:
            latest = df.iloc[-1]
            
            # RSI訊號
            rsi = self.pattern_analyzer._calculate_rsi(df['close']).iloc[-1]
            rsi_signal = "超賣" if rsi < 30 else "超買" if rsi > 70 else "中性"
            
            # 移動平均訊號
            ma20 = df['close'].rolling(window=20).mean().iloc[-1]
            ma50 = df['close'].rolling(window=50).mean().iloc[-1] if len(df) >= 50 else ma20
            
            ma_signal = "看漲" if latest['close'] > ma20 > ma50 else "看跌" if latest['close'] < ma20 < ma50 else "震盪"
            
            # 成交量訊號
            recent_volume = df['volume'].iloc[-5:].mean()
            avg_volume = df['volume'].mean()
            volume_signal = "放量" if recent_volume > avg_volume * 1.5 else "縮量" if recent_volume < avg_volume * 0.7 else "正常"
            
            return {
                "rsi": {"value": round(rsi, 2), "signal": rsi_signal},
                "moving_average": {"ma20": round(ma20, 2), "ma50": round(ma50, 2), "signal": ma_signal},
                "volume": {"recent_avg": int(recent_volume), "overall_avg": int(avg_volume), "signal": volume_signal},
                "price_trend": self._analyze_price_trend(df)
            }
            
        except Exception as e:
            logger.error(f"指標分析錯誤: {e}")
            return {}
    
    def _analyze_price_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析價格趨勢"""
        try:
            # 短期趨勢（5天）
            short_trend = (df['close'].iloc[-1] - df['close'].iloc[-6]) / df['close'].iloc[-6] * 100
            
            # 中期趨勢（20天）
            mid_trend = (df['close'].iloc[-1] - df['close'].iloc[-21]) / df['close'].iloc[-21] * 100 if len(df) >= 21 else short_trend
            
            return {
                "short_term": {"change_pct": round(short_trend, 2), "direction": "上漲" if short_trend > 0 else "下跌"},
                "medium_term": {"change_pct": round(mid_trend, 2), "direction": "上漲" if mid_trend > 0 else "下跌"}
            }
            
        except Exception:
            return {"short_term": {"change_pct": 0, "direction": "持平"}, "medium_term": {"change_pct": 0, "direction": "持平"}}
    
    def _calculate_overall_signal(self, pattern_signals: List[PatternSignal], indicator_signals: Dict[str, Any]) -> Dict[str, Any]:
        """計算綜合訊號評分"""
        try:
            score = 0
            max_score = 100
            
            # 形態訊號權重 (60%)
            if pattern_signals:
                pattern_score = sum(s.confidence for s in pattern_signals[:3]) / len(pattern_signals[:3])
                score += pattern_score * 0.6
            
            # 技術指標權重 (40%)
            indicator_score = 0
            
            # RSI權重
            if 'rsi' in indicator_signals:
                rsi_val = indicator_signals['rsi']['value']
                if 30 <= rsi_val <= 50:  # 適中偏低，較適合買進
                    indicator_score += 25
                elif 50 < rsi_val <= 60:
                    indicator_score += 15
                elif rsi_val < 30:  # 超賣
                    indicator_score += 30
            
            # 移動平均權重
            if 'moving_average' in indicator_signals:
                if indicator_signals['moving_average']['signal'] == "看漲":
                    indicator_score += 25
                elif indicator_signals['moving_average']['signal'] == "震盪":
                    indicator_score += 10
            
            # 成交量權重
            if 'volume' in indicator_signals:
                if indicator_signals['volume']['signal'] == "放量":
                    indicator_score += 15
                elif indicator_signals['volume']['signal'] == "正常":
                    indicator_score += 10
            
            score += (indicator_score / 65) * 40  # 最大65分，轉換為40%
            
            # 確定訊號強度
            if score >= 80:
                strength = "非常強烈"
                recommendation = "強烈建議買進"
            elif score >= 65:
                strength = "強烈"
                recommendation = "建議買進"
            elif score >= 50:
                strength = "中等"
                recommendation = "可考慮買進"
            elif score >= 35:
                strength = "偏弱"
                recommendation = "觀望"
            else:
                strength = "弱"
                recommendation = "不建議買進"
            
            return {
                "score": round(score, 1),
                "max_score": max_score,
                "strength": strength,
                "recommendation": recommendation,
                "confidence_level": "高" if score >= 70 else "中" if score >= 50 else "低"
            }
            
        except Exception as e:
            logger.error(f"綜合訊號計算錯誤: {e}")
            return {"score": 0, "strength": "無法評估", "recommendation": "數據不足"}
    
    def _generate_signal_summary(self, pattern_signals: List[PatternSignal], indicator_signals: Dict[str, Any], overall_signal: Dict[str, Any]) -> str:
        """生成訊號摘要"""
        try:
            summary_parts = []
            
            # 綜合評分
            summary_parts.append(f"綜合評分: {overall_signal.get('score', 0)}/100 ({overall_signal.get('strength', '未知')})")
            
            # 主要形態訊號
            if pattern_signals:
                top_pattern = pattern_signals[0]
                summary_parts.append(f"主要形態: {top_pattern.description} (信心度: {top_pattern.confidence}%)")
            
            # 技術指標摘要
            if 'rsi' in indicator_signals:
                rsi_info = indicator_signals['rsi']
                summary_parts.append(f"RSI: {rsi_info['value']} ({rsi_info['signal']})")
            
            if 'moving_average' in indicator_signals:
                ma_info = indicator_signals['moving_average']
                summary_parts.append(f"均線: {ma_info['signal']}")
            
            # 建議
            summary_parts.append(f"建議: {overall_signal.get('recommendation', '觀望')}")
            
            return " | ".join(summary_parts)
            
        except Exception:
            return "訊號分析完成，請查看詳細數據"
    
    def _signal_to_dict(self, signal: PatternSignal) -> Dict[str, Any]:
        """將PatternSignal轉換為字典"""
        return {
            "pattern_type": signal.pattern_type.value,
            "signal_strength": signal.signal_strength.value,
            "confidence": signal.confidence,
            "entry_price": signal.entry_price,
            "target_price": signal.target_price,
            "stop_loss": signal.stop_loss,
            "risk_reward_ratio": round(signal.risk_reward_ratio, 2),
            "pattern_start": signal.pattern_start.isoformat() if signal.pattern_start else None,
            "pattern_end": signal.pattern_end.isoformat() if signal.pattern_end else None,
            "breakout_point": signal.breakout_point,
            "volume_confirmation": signal.volume_confirmation,
            "description": signal.description,
            "technical_details": signal.technical_details or {}
        }