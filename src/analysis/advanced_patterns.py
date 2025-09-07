#!/usr/bin/env python3
"""
進階形態學分析 - 旗型、楔型、三角形等
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class PatternSignal:
    """形態訊號類別"""
    pattern_type: str
    pattern_name: str
    start_date: datetime
    end_date: datetime
    confidence: float
    breakout_level: float
    target_price: float
    stop_loss: float
    direction: str  # 'bullish' or 'bearish'
    description: str
    key_points: List[Tuple[datetime, float]]

class AdvancedPatternRecognizer:
    """進階形態識別器"""
    
    def __init__(self, min_pattern_length=10, max_pattern_length=50):
        self.min_pattern_length = min_pattern_length
        self.max_pattern_length = max_pattern_length
        
    def analyze_all_patterns(self, data: pd.DataFrame) -> Dict[str, List[PatternSignal]]:
        """分析所有進階形態"""
        patterns = {
            'flags': self.detect_flags(data),
            'pennants': self.detect_pennants(data),
            'wedges': self.detect_wedges(data),
            'triangles': self.detect_triangles(data),
            'channels': self.detect_channels(data),
            'cup_and_handle': self.detect_cup_and_handle(data)
        }
        
        return patterns
    
    def detect_flags(self, data: pd.DataFrame) -> List[PatternSignal]:
        """檢測旗型形態"""
        flags = []
        
        for i in range(self.min_pattern_length, len(data) - self.min_pattern_length):
            # 尋找旗型：強勢上漲後的矩形整理
            window = data.iloc[i-self.min_pattern_length:i+self.min_pattern_length]
            
            # 前期趨勢檢查 (旗桿)
            pre_trend = data.iloc[i-self.min_pattern_length*2:i-self.min_pattern_length]
            if self._is_strong_uptrend(pre_trend):
                # 檢測旗型本體 (矩形整理)
                flag_body = data.iloc[i-self.min_pattern_length//2:i]
                if self._is_rectangular_consolidation(flag_body):
                    
                    pattern = self._create_flag_pattern(
                        data, i-self.min_pattern_length, i, 'bullish'
                    )
                    if pattern:
                        flags.append(pattern)
            
            # 檢測熊市旗型
            elif self._is_strong_downtrend(pre_trend):
                flag_body = data.iloc[i-self.min_pattern_length//2:i]
                if self._is_rectangular_consolidation(flag_body):
                    
                    pattern = self._create_flag_pattern(
                        data, i-self.min_pattern_length, i, 'bearish'
                    )
                    if pattern:
                        flags.append(pattern)
        
        return flags
    
    def detect_pennants(self, data: pd.DataFrame) -> List[PatternSignal]:
        """檢測三角旗形態"""
        pennants = []
        
        for i in range(self.min_pattern_length, len(data) - self.min_pattern_length):
            window = data.iloc[i-self.min_pattern_length:i+self.min_pattern_length]
            
            # 前期強勢趨勢
            pre_trend = data.iloc[i-self.min_pattern_length*2:i-self.min_pattern_length]
            
            if self._is_strong_uptrend(pre_trend) or self._is_strong_downtrend(pre_trend):
                # 檢測三角旗本體 (收斂三角形)
                pennant_body = data.iloc[i-self.min_pattern_length//2:i]
                if self._is_converging_triangle(pennant_body):
                    
                    direction = 'bullish' if self._is_strong_uptrend(pre_trend) else 'bearish'
                    pattern = self._create_pennant_pattern(
                        data, i-self.min_pattern_length, i, direction
                    )
                    if pattern:
                        pennants.append(pattern)
        
        return pennants
    
    def detect_wedges(self, data: pd.DataFrame) -> List[PatternSignal]:
        """檢測楔型形態"""
        wedges = []
        
        for i in range(self.min_pattern_length*2, len(data) - self.min_pattern_length):
            window = data.iloc[i-self.min_pattern_length*2:i]
            
            # 上升楔型 (看跌)
            if self._is_rising_wedge(window):
                pattern = self._create_wedge_pattern(window, i, 'bearish', 'rising_wedge')
                if pattern:
                    wedges.append(pattern)
            
            # 下降楔型 (看漲)
            elif self._is_falling_wedge(window):
                pattern = self._create_wedge_pattern(window, i, 'bullish', 'falling_wedge')
                if pattern:
                    wedges.append(pattern)
        
        return wedges
    
    def detect_triangles(self, data: pd.DataFrame) -> List[PatternSignal]:
        """檢測三角形形態"""
        triangles = []
        
        for i in range(self.min_pattern_length*2, len(data) - self.min_pattern_length):
            window = data.iloc[i-self.min_pattern_length*2:i]
            
            # 對稱三角形
            if self._is_symmetrical_triangle(window):
                pattern = self._create_triangle_pattern(window, i, 'neutral', 'symmetrical')
                if pattern:
                    triangles.append(pattern)
            
            # 上升三角形 (看漲)
            elif self._is_ascending_triangle(window):
                pattern = self._create_triangle_pattern(window, i, 'bullish', 'ascending')
                if pattern:
                    triangles.append(pattern)
            
            # 下降三角形 (看跌)
            elif self._is_descending_triangle(window):
                pattern = self._create_triangle_pattern(window, i, 'bearish', 'descending')
                if pattern:
                    triangles.append(pattern)
        
        return triangles
    
    def detect_channels(self, data: pd.DataFrame) -> List[PatternSignal]:
        """檢測通道形態"""
        channels = []
        
        for i in range(self.min_pattern_length*2, len(data) - self.min_pattern_length):
            window = data.iloc[i-self.min_pattern_length*2:i]
            
            # 上升通道
            if self._is_ascending_channel(window):
                pattern = self._create_channel_pattern(window, i, 'bullish', 'ascending_channel')
                if pattern:
                    channels.append(pattern)
            
            # 下降通道
            elif self._is_descending_channel(window):
                pattern = self._create_channel_pattern(window, i, 'bearish', 'descending_channel')
                if pattern:
                    channels.append(pattern)
        
        return channels
    
    def detect_cup_and_handle(self, data: pd.DataFrame) -> List[PatternSignal]:
        """檢測杯柄形態"""
        cups = []
        
        min_cup_length = self.min_pattern_length * 3
        
        for i in range(min_cup_length, len(data) - self.min_pattern_length):
            window = data.iloc[i-min_cup_length:i]
            
            if self._is_cup_and_handle(window):
                pattern = self._create_cup_handle_pattern(window, i)
                if pattern:
                    cups.append(pattern)
        
        return cups
    
    # 輔助方法 - 趨勢檢測
    def _is_strong_uptrend(self, data: pd.DataFrame, min_gain=0.05) -> bool:
        """檢測強勢上升趨勢"""
        if len(data) < 5:
            return False
        
        start_price = data['close'].iloc[0]
        end_price = data['close'].iloc[-1]
        gain = (end_price - start_price) / start_price
        
        # 檢查趨勢一致性
        prices = data['close'].values
        trend_consistency = np.corrcoef(np.arange(len(prices)), prices)[0, 1]
        
        return gain > min_gain and trend_consistency > 0.7
    
    def _is_strong_downtrend(self, data: pd.DataFrame, min_loss=0.05) -> bool:
        """檢測強勢下降趨勢"""
        if len(data) < 5:
            return False
        
        start_price = data['close'].iloc[0]
        end_price = data['close'].iloc[-1]
        loss = (start_price - end_price) / start_price
        
        # 檢查趨勢一致性
        prices = data['close'].values
        trend_consistency = np.corrcoef(np.arange(len(prices)), prices)[0, 1]
        
        return loss > min_loss and trend_consistency < -0.7
    
    def _is_rectangular_consolidation(self, data: pd.DataFrame, max_range_ratio=0.05) -> bool:
        """檢測矩形整理"""
        if len(data) < 5:
            return False
        
        high_prices = data['high'].values
        low_prices = data['low'].values
        
        price_range = (np.max(high_prices) - np.min(low_prices)) / np.mean(data['close'])
        
        # 檢查價格是否在相對狹窄的範圍內震盪
        return price_range < max_range_ratio
    
    def _is_converging_triangle(self, data: pd.DataFrame) -> bool:
        """檢測收斂三角形"""
        if len(data) < 8:
            return False
        
        highs = data['high'].values
        lows = data['low'].values
        
        # 計算高點和低點的趨勢線
        x = np.arange(len(data))
        
        # 高點趨勢 (應該下降)
        high_slope = np.polyfit(x, highs, 1)[0]
        # 低點趨勢 (應該上升)
        low_slope = np.polyfit(x, lows, 1)[0]
        
        # 收斂條件：高點下降，低點上升
        return high_slope < -0.001 and low_slope > 0.001
    
    def _is_rising_wedge(self, data: pd.DataFrame) -> bool:
        """檢測上升楔型"""
        if len(data) < 10:
            return False
        
        highs = data['high'].values
        lows = data['low'].values
        x = np.arange(len(data))
        
        # 高點和低點都上升，但低點上升更快
        high_slope = np.polyfit(x, highs, 1)[0]
        low_slope = np.polyfit(x, lows, 1)[0]
        
        return (high_slope > 0 and low_slope > 0 and 
                low_slope > high_slope * 1.5)
    
    def _is_falling_wedge(self, data: pd.DataFrame) -> bool:
        """檢測下降楔型"""
        if len(data) < 10:
            return False
        
        highs = data['high'].values
        lows = data['low'].values
        x = np.arange(len(data))
        
        # 高點和低點都下降，但高點下降更快
        high_slope = np.polyfit(x, highs, 1)[0]
        low_slope = np.polyfit(x, lows, 1)[0]
        
        return (high_slope < 0 and low_slope < 0 and 
                high_slope < low_slope * 1.5)
    
    def _is_symmetrical_triangle(self, data: pd.DataFrame) -> bool:
        """檢測對稱三角形"""
        if len(data) < 10:
            return False
        
        highs = data['high'].values
        lows = data['low'].values
        x = np.arange(len(data))
        
        high_slope = np.polyfit(x, highs, 1)[0]
        low_slope = np.polyfit(x, lows, 1)[0]
        
        # 高點下降，低點上升，且斜率相近
        slope_ratio = abs(high_slope / low_slope) if low_slope != 0 else 0
        
        return (high_slope < -0.001 and low_slope > 0.001 and 
                0.5 < slope_ratio < 2.0)
    
    def _is_ascending_triangle(self, data: pd.DataFrame) -> bool:
        """檢測上升三角形"""
        if len(data) < 10:
            return False
        
        highs = data['high'].values
        lows = data['low'].values
        x = np.arange(len(data))
        
        high_slope = np.polyfit(x, highs, 1)[0]
        low_slope = np.polyfit(x, lows, 1)[0]
        
        # 高點水平，低點上升
        return abs(high_slope) < 0.001 and low_slope > 0.002
    
    def _is_descending_triangle(self, data: pd.DataFrame) -> bool:
        """檢測下降三角形"""
        if len(data) < 10:
            return False
        
        highs = data['high'].values
        lows = data['low'].values
        x = np.arange(len(data))
        
        high_slope = np.polyfit(x, highs, 1)[0]
        low_slope = np.polyfit(x, lows, 1)[0]
        
        # 低點水平，高點下降
        return high_slope < -0.002 and abs(low_slope) < 0.001
    
    def _is_ascending_channel(self, data: pd.DataFrame) -> bool:
        """檢測上升通道"""
        if len(data) < 15:
            return False
        
        highs = data['high'].values
        lows = data['low'].values
        x = np.arange(len(data))
        
        high_slope = np.polyfit(x, highs, 1)[0]
        low_slope = np.polyfit(x, lows, 1)[0]
        
        # 高點和低點都上升，且斜率相近
        slope_diff = abs(high_slope - low_slope)
        return (high_slope > 0.002 and low_slope > 0.002 and 
                slope_diff < 0.001)
    
    def _is_descending_channel(self, data: pd.DataFrame) -> bool:
        """檢測下降通道"""
        if len(data) < 15:
            return False
        
        highs = data['high'].values
        lows = data['low'].values
        x = np.arange(len(data))
        
        high_slope = np.polyfit(x, highs, 1)[0]
        low_slope = np.polyfit(x, lows, 1)[0]
        
        # 高點和低點都下降，且斜率相近
        slope_diff = abs(high_slope - low_slope)
        return (high_slope < -0.002 and low_slope < -0.002 and 
                slope_diff < 0.001)
    
    def _is_cup_and_handle(self, data: pd.DataFrame) -> bool:
        """檢測杯柄形態"""
        if len(data) < 20:
            return False
        
        # 杯型：U型底部
        mid_point = len(data) // 2
        left_side = data.iloc[:mid_point]
        right_side = data.iloc[mid_point:]
        
        # 檢查U型特徵
        cup_bottom = data['low'].min()
        cup_start = data['high'].iloc[0]
        cup_end = data['high'].iloc[-1]
        
        # 杯深度適中 (10-50%)
        cup_depth = (cup_start - cup_bottom) / cup_start
        
        return (0.1 < cup_depth < 0.5 and 
                abs(cup_start - cup_end) / cup_start < 0.05)
    
    # 形態創建方法
    def _create_flag_pattern(self, data: pd.DataFrame, start_idx: int, end_idx: int, direction: str) -> Optional[PatternSignal]:
        """創建旗型形態"""
        pattern_data = data.iloc[start_idx:end_idx]
        
        if direction == 'bullish':
            breakout_level = pattern_data['high'].max()
            target_price = breakout_level * 1.1  # 旗桿高度投射
            stop_loss = pattern_data['low'].min()
        else:
            breakout_level = pattern_data['low'].min()
            target_price = breakout_level * 0.9
            stop_loss = pattern_data['high'].max()
        
        return PatternSignal(
            pattern_type='flag',
            pattern_name=f'{direction}_flag',
            start_date=pattern_data.index[0],
            end_date=pattern_data.index[-1],
            confidence=0.75,
            breakout_level=breakout_level,
            target_price=target_price,
            stop_loss=stop_loss,
            direction=direction,
            description=f'{direction.title()} flag pattern detected',
            key_points=[(pattern_data.index[0], pattern_data['close'].iloc[0]),
                       (pattern_data.index[-1], pattern_data['close'].iloc[-1])]
        )
    
    def _create_pennant_pattern(self, data: pd.DataFrame, start_idx: int, end_idx: int, direction: str) -> Optional[PatternSignal]:
        """創建三角旗形態"""
        pattern_data = data.iloc[start_idx:end_idx]
        
        if direction == 'bullish':
            breakout_level = pattern_data['high'].max()
            target_price = breakout_level * 1.08
            stop_loss = pattern_data['low'].min()
        else:
            breakout_level = pattern_data['low'].min()
            target_price = breakout_level * 0.92
            stop_loss = pattern_data['high'].max()
        
        return PatternSignal(
            pattern_type='pennant',
            pattern_name=f'{direction}_pennant',
            start_date=pattern_data.index[0],
            end_date=pattern_data.index[-1],
            confidence=0.7,
            breakout_level=breakout_level,
            target_price=target_price,
            stop_loss=stop_loss,
            direction=direction,
            description=f'{direction.title()} pennant pattern detected',
            key_points=[(pattern_data.index[0], pattern_data['close'].iloc[0]),
                       (pattern_data.index[-1], pattern_data['close'].iloc[-1])]
        )
    
    def _create_wedge_pattern(self, data: pd.DataFrame, end_idx: int, direction: str, wedge_type: str) -> Optional[PatternSignal]:
        """創建楔型形態"""
        if direction == 'bullish':  # 下降楔型
            breakout_level = data['high'].iloc[-5:].max()
            target_price = breakout_level * 1.12
            stop_loss = data['low'].min()
        else:  # 上升楔型
            breakout_level = data['low'].iloc[-5:].min()
            target_price = breakout_level * 0.88
            stop_loss = data['high'].max()
        
        return PatternSignal(
            pattern_type='wedge',
            pattern_name=wedge_type,
            start_date=data.index[0],
            end_date=data.index[-1],
            confidence=0.8,
            breakout_level=breakout_level,
            target_price=target_price,
            stop_loss=stop_loss,
            direction=direction,
            description=f'{wedge_type.replace("_", " ").title()} pattern detected',
            key_points=[(data.index[0], data['close'].iloc[0]),
                       (data.index[-1], data['close'].iloc[-1])]
        )
    
    def _create_triangle_pattern(self, data: pd.DataFrame, end_idx: int, direction: str, triangle_type: str) -> Optional[PatternSignal]:
        """創建三角形形態"""
        if direction == 'bullish':
            breakout_level = data['high'].iloc[-5:].max()
            target_price = breakout_level * 1.1
            stop_loss = data['low'].iloc[-5:].min()
        elif direction == 'bearish':
            breakout_level = data['low'].iloc[-5:].min()
            target_price = breakout_level * 0.9
            stop_loss = data['high'].iloc[-5:].max()
        else:  # neutral
            current_price = data['close'].iloc[-1]
            breakout_level = current_price
            target_price = current_price * 1.05  # 預設 5% 目標
            stop_loss = current_price * 0.95
        
        return PatternSignal(
            pattern_type='triangle',
            pattern_name=f'{triangle_type}_triangle',
            start_date=data.index[0],
            end_date=data.index[-1],
            confidence=0.65,
            breakout_level=breakout_level,
            target_price=target_price,
            stop_loss=stop_loss,
            direction=direction,
            description=f'{triangle_type.replace("_", " ").title()} triangle pattern detected',
            key_points=[(data.index[0], data['close'].iloc[0]),
                       (data.index[-1], data['close'].iloc[-1])]
        )
    
    def _create_channel_pattern(self, data: pd.DataFrame, end_idx: int, direction: str, channel_type: str) -> Optional[PatternSignal]:
        """創建通道形態"""
        if direction == 'bullish':
            breakout_level = data['high'].iloc[-5:].max()
            target_price = breakout_level * 1.08
            stop_loss = data['low'].iloc[-5:].min()
        else:
            breakout_level = data['low'].iloc[-5:].min()
            target_price = breakout_level * 0.92
            stop_loss = data['high'].iloc[-5:].max()
        
        return PatternSignal(
            pattern_type='channel',
            pattern_name=channel_type,
            start_date=data.index[0],
            end_date=data.index[-1],
            confidence=0.7,
            breakout_level=breakout_level,
            target_price=target_price,
            stop_loss=stop_loss,
            direction=direction,
            description=f'{channel_type.replace("_", " ").title()} pattern detected',
            key_points=[(data.index[0], data['close'].iloc[0]),
                       (data.index[-1], data['close'].iloc[-1])]
        )
    
    def _create_cup_handle_pattern(self, data: pd.DataFrame, end_idx: int) -> Optional[PatternSignal]:
        """創建杯柄形態"""
        breakout_level = data['high'].iloc[-10:].max()
        target_price = breakout_level * 1.15  # 杯深度投射
        stop_loss = data['low'].iloc[-10:].min()
        
        return PatternSignal(
            pattern_type='cup_and_handle',
            pattern_name='cup_and_handle',
            start_date=data.index[0],
            end_date=data.index[-1],
            confidence=0.85,
            breakout_level=breakout_level,
            target_price=target_price,
            stop_loss=stop_loss,
            direction='bullish',
            description='Cup and handle pattern detected',
            key_points=[(data.index[0], data['close'].iloc[0]),
                       (data.index[-1], data['close'].iloc[-1])]
        )