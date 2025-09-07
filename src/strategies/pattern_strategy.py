#!/usr/bin/env python3
"""
形態學交易策略 - 基於旗型、楔型、三角形等形態的交易策略
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from src.backtesting.backtest_engine import TradingStrategy
from src.analysis.advanced_patterns import AdvancedPatternRecognizer, PatternSignal
import logging

logger = logging.getLogger(__name__)

class PatternTradingStrategy(TradingStrategy):
    """
    形態學交易策略
    
    基於以下形態進行交易：
    - 旗型 (Flags): 延續型態
    - 三角旗 (Pennants): 延續型態  
    - 楔型 (Wedges): 反轉型態
    - 三角形 (Triangles): 突破型態
    - 通道 (Channels): 趨勢型態
    - 杯柄 (Cup & Handle): 反轉型態
    """
    
    def __init__(self, 
                 pattern_confidence_threshold=0.6,
                 enable_flags=True,
                 enable_pennants=True,
                 enable_wedges=True,
                 enable_triangles=True,
                 enable_channels=True,
                 enable_cup_handle=True,
                 risk_reward_ratio=2.0,
                 max_positions=3):
        """
        初始化形態學策略
        
        Args:
            pattern_confidence_threshold: 形態信心度閾值
            enable_*: 各種形態的啟用開關
            risk_reward_ratio: 風險報酬比
            max_positions: 最大持倉數
        """
        self.pattern_confidence_threshold = pattern_confidence_threshold
        self.enable_flags = enable_flags
        self.enable_pennants = enable_pennants
        self.enable_wedges = enable_wedges
        self.enable_triangles = enable_triangles
        self.enable_channels = enable_channels
        self.enable_cup_handle = enable_cup_handle
        self.risk_reward_ratio = risk_reward_ratio
        self.max_positions = max_positions
        
        # 初始化形態識別器
        self.pattern_recognizer = AdvancedPatternRecognizer()
        
        # 形態權重設定 (基於可靠性)
        self.pattern_weights = {
            'flags': 0.9,           # 旗型可靠性高
            'pennants': 0.8,        # 三角旗次之
            'wedges': 0.85,         # 楔型可靠性高
            'triangles': 0.7,       # 三角形中等
            'channels': 0.75,       # 通道中等
            'cup_and_handle': 0.95  # 杯柄最可靠
        }
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成基於形態學的交易訊號
        
        Args:
            data: 包含 OHLCV 和技術指標的 DataFrame
            
        Returns:
            添加訊號欄位的 DataFrame
        """
        df = data.copy()
        
        # 初始化訊號欄位
        df['signal'] = 0
        df['signal_strength'] = 0.0
        df['signal_source'] = ''
        df['pattern_type'] = ''
        df['breakout_level'] = np.nan
        df['target_price'] = np.nan
        df['stop_loss_level'] = np.nan
        
        # 檢測所有形態
        logger.info("開始形態識別...")
        all_patterns = self.pattern_recognizer.analyze_all_patterns(data)
        
        # 處理每種形態類型
        pattern_signals = []
        
        if self.enable_flags and 'flags' in all_patterns:
            pattern_signals.extend(self._process_pattern_type(all_patterns['flags'], 'flags'))
        
        if self.enable_pennants and 'pennants' in all_patterns:
            pattern_signals.extend(self._process_pattern_type(all_patterns['pennants'], 'pennants'))
        
        if self.enable_wedges and 'wedges' in all_patterns:
            pattern_signals.extend(self._process_pattern_type(all_patterns['wedges'], 'wedges'))
        
        if self.enable_triangles and 'triangles' in all_patterns:
            pattern_signals.extend(self._process_pattern_type(all_patterns['triangles'], 'triangles'))
        
        if self.enable_channels and 'channels' in all_patterns:
            pattern_signals.extend(self._process_pattern_type(all_patterns['channels'], 'channels'))
        
        if self.enable_cup_handle and 'cup_and_handle' in all_patterns:
            pattern_signals.extend(self._process_pattern_type(all_patterns['cup_and_handle'], 'cup_and_handle'))
        
        # 將形態訊號應用到 DataFrame
        df = self._apply_pattern_signals(df, pattern_signals)
        
        # 添加確認訊號 (突破確認)
        df = self._add_breakout_confirmation(df)
        
        logger.info(f"形態識別完成，共發現 {len(pattern_signals)} 個有效形態")
        
        return df
    
    def _process_pattern_type(self, patterns: List[PatternSignal], pattern_type: str) -> List[Dict[str, Any]]:
        """處理特定類型的形態"""
        processed_signals = []
        
        for pattern in patterns:
            # 檢查信心度
            if pattern.confidence < self.pattern_confidence_threshold:
                continue
            
            # 計算調整後的信心度 (結合形態權重)
            adjusted_confidence = pattern.confidence * self.pattern_weights.get(pattern_type, 0.7)
            
            # 計算風險報酬比
            if pattern.direction == 'bullish':
                risk = abs(pattern.breakout_level - pattern.stop_loss)
                reward = abs(pattern.target_price - pattern.breakout_level)
            else:
                risk = abs(pattern.stop_loss - pattern.breakout_level)
                reward = abs(pattern.breakout_level - pattern.target_price)
            
            risk_reward = reward / risk if risk > 0 else 0
            
            # 檢查風險報酬比
            if risk_reward < self.risk_reward_ratio:
                continue
            
            signal_info = {
                'pattern': pattern,
                'pattern_type': pattern_type,
                'adjusted_confidence': adjusted_confidence,
                'risk_reward_ratio': risk_reward,
                'end_date': pattern.end_date
            }
            
            processed_signals.append(signal_info)
        
        return processed_signals
    
    def _apply_pattern_signals(self, df: pd.DataFrame, pattern_signals: List[Dict[str, Any]]) -> pd.DataFrame:
        """將形態訊號應用到 DataFrame"""
        
        for signal_info in pattern_signals:
            pattern = signal_info['pattern']
            pattern_type = signal_info['pattern_type']
            confidence = signal_info['adjusted_confidence']
            
            # 找到形態結束點附近的索引
            end_date = pattern.end_date
            
            try:
                # 找到最接近的日期索引
                nearest_idx = df.index.get_indexer([end_date], method='nearest')[0]
                
                if nearest_idx >= 0 and nearest_idx < len(df):
                    # 檢查是否已經有訊號 (避免重複)
                    if df.iloc[nearest_idx]['signal'] == 0:
                        # 設定交易訊號
                        signal_direction = 1 if pattern.direction == 'bullish' else -1
                        
                        df.iloc[nearest_idx, df.columns.get_loc('signal')] = signal_direction
                        df.iloc[nearest_idx, df.columns.get_loc('signal_strength')] = confidence
                        df.iloc[nearest_idx, df.columns.get_loc('signal_source')] = f"{pattern_type}_{pattern.pattern_name}"
                        df.iloc[nearest_idx, df.columns.get_loc('pattern_type')] = pattern.pattern_name
                        df.iloc[nearest_idx, df.columns.get_loc('breakout_level')] = pattern.breakout_level
                        df.iloc[nearest_idx, df.columns.get_loc('target_price')] = pattern.target_price
                        df.iloc[nearest_idx, df.columns.get_loc('stop_loss_level')] = pattern.stop_loss
                        
            except (IndexError, KeyError) as e:
                logger.warning(f"無法應用形態訊號: {str(e)}")
                continue
        
        return df
    
    def _add_breakout_confirmation(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加突破確認訊號"""
        
        # 為了簡化，這裡使用基本的價格突破確認
        # 實際應用中可以加入成交量確認、時間確認等
        
        for i in range(1, len(df)):
            if df.iloc[i]['signal'] != 0:
                current_price = df.iloc[i]['close']
                breakout_level = df.iloc[i]['breakout_level']
                
                if not pd.isna(breakout_level):
                    signal_direction = df.iloc[i]['signal']
                    
                    # 檢查價格是否真正突破
                    if signal_direction == 1:  # 買入訊號
                        if current_price <= breakout_level:
                            # 沒有突破，降低信心度
                            df.iloc[i, df.columns.get_loc('signal_strength')] *= 0.7
                    else:  # 賣出訊號
                        if current_price >= breakout_level:
                            # 沒有突破，降低信心度
                            df.iloc[i, df.columns.get_loc('signal_strength')] *= 0.7
        
        return df
    
    def get_strategy_name(self) -> str:
        """返回策略名稱"""
        enabled_patterns = []
        if self.enable_flags: enabled_patterns.append('flags')
        if self.enable_pennants: enabled_patterns.append('pennants')
        if self.enable_wedges: enabled_patterns.append('wedges')
        if self.enable_triangles: enabled_patterns.append('triangles')
        if self.enable_channels: enabled_patterns.append('channels')
        if self.enable_cup_handle: enabled_patterns.append('cup_handle')
        
        patterns_str = '_'.join(enabled_patterns)
        return f"Pattern_Strategy_{patterns_str}_{self.pattern_confidence_threshold}"
    
    def get_pattern_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """獲取形態分析摘要"""
        all_patterns = self.pattern_recognizer.analyze_all_patterns(data)
        
        summary = {
            'total_patterns': 0,
            'pattern_breakdown': {},
            'recent_patterns': [],
            'active_signals': []
        }
        
        for pattern_type, patterns in all_patterns.items():
            if patterns:
                summary['total_patterns'] += len(patterns)
                summary['pattern_breakdown'][pattern_type] = {
                    'count': len(patterns),
                    'avg_confidence': np.mean([p.confidence for p in patterns]),
                    'bullish_count': len([p for p in patterns if p.direction == 'bullish']),
                    'bearish_count': len([p for p in patterns if p.direction == 'bearish'])
                }
                
                # 最近的形態
                recent = sorted(patterns, key=lambda x: x.end_date, reverse=True)[:3]
                for pattern in recent:
                    summary['recent_patterns'].append({
                        'type': pattern.pattern_name,
                        'direction': pattern.direction,
                        'confidence': pattern.confidence,
                        'end_date': pattern.end_date.isoformat(),
                        'target_price': pattern.target_price
                    })
        
        return summary

class EnhancedPatternStrategy(PatternTradingStrategy):
    """
    增強版形態策略 - 結合技術指標確認
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.require_volume_confirmation = kwargs.get('require_volume_confirmation', True)
        self.require_rsi_confirmation = kwargs.get('require_rsi_confirmation', True)
        self.rsi_oversold = kwargs.get('rsi_oversold', 30)
        self.rsi_overbought = kwargs.get('rsi_overbought', 70)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """增強版訊號生成 - 加入技術指標確認"""
        
        # 先使用基礎形態策略生成訊號
        df = super().generate_signals(data)
        
        # 添加技術指標確認
        df = self._add_indicator_confirmation(df)
        
        return df
    
    def _add_indicator_confirmation(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加技術指標確認"""
        
        for i in range(len(df)):
            if df.iloc[i]['signal'] != 0:
                signal_strength = df.iloc[i]['signal_strength']
                signal_direction = df.iloc[i]['signal']
                
                # 成交量確認
                if self.require_volume_confirmation:
                    if 'volume_ratio' in df.columns:
                        volume_ratio = df.iloc[i]['volume_ratio']
                        if pd.notna(volume_ratio) and volume_ratio > 1.2:
                            signal_strength *= 1.1  # 成交量放大，增強訊號
                        elif pd.notna(volume_ratio) and volume_ratio < 0.8:
                            signal_strength *= 0.8  # 成交量萎縮，減弱訊號
                
                # RSI 確認
                if self.require_rsi_confirmation:
                    if 'rsi' in df.columns:
                        rsi = df.iloc[i]['rsi']
                        if pd.notna(rsi):
                            if signal_direction == 1:  # 買入訊號
                                if rsi < 50:  # RSI 支持買入
                                    signal_strength *= 1.1
                                elif rsi > 70:  # RSI 過熱
                                    signal_strength *= 0.7
                            else:  # 賣出訊號
                                if rsi > 50:  # RSI 支持賣出
                                    signal_strength *= 1.1
                                elif rsi < 30:  # RSI 超賣
                                    signal_strength *= 0.7
                
                # 更新訊號強度
                df.iloc[i, df.columns.get_loc('signal_strength')] = min(signal_strength, 1.0)
        
        return df