"""
Enhanced AI Trading Analyzer with Professional Technical Analysis
專業AI交易分析器，提供量化數據和精確進出場點分析
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from .ai_analyzer import OpenAIAnalyzer, AIAnalysisResult
from .technical_indicators import TechnicalIndicators
from .pattern_recognition import PatternRecognition

logger = logging.getLogger(__name__)

@dataclass
class QuantitativeMetrics:
    """量化指標數據"""
    volatility: float
    volume_ratio: float
    price_momentum: float
    trend_strength: float
    support_levels: List[float]
    resistance_levels: List[float]
    risk_score: float

@dataclass
class EntryExitPoints:
    """進出場點分析"""
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    position_size_pct: float
    confidence: float
    reasoning: str

@dataclass
class EnhancedAIAnalysis:
    """增強版AI分析結果"""
    symbol: str
    timestamp: datetime
    overall_recommendation: str  # BUY/SELL/HOLD
    confidence: float
    
    # 技術分析
    pattern_analysis: Dict[str, Any]
    quantitative_metrics: QuantitativeMetrics
    entry_exit_points: EntryExitPoints
    
    # AI專業建議
    market_context: str
    risk_assessment: str
    timeframe_analysis: Dict[str, str]  # 短期/中期/長期展望
    key_levels: Dict[str, float]  # 關鍵支撐阻力位

class EnhancedAIAnalyzer:
    """增強版AI分析器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.ai_analyzer = OpenAIAnalyzer(api_key)
        self.technical_indicators = TechnicalIndicators()
        self.pattern_recognition = PatternRecognition()
    
    async def analyze_stock_comprehensive(
        self,
        symbol: str,
        data: pd.DataFrame,
        period: str = "3mo"
    ) -> EnhancedAIAnalysis:
        """
        綜合股票分析 - 結合技術指標、型態識別和AI智能分析
        """
        try:
            # 1. 計算技術指標
            indicators = await self._calculate_comprehensive_indicators(data)
            
            # 2. 識別圖表型態
            patterns = await self._identify_patterns(data)
            
            # 3. 計算量化指標
            quant_metrics = await self._calculate_quantitative_metrics(data)
            
            # 4. 計算進出場點
            entry_exit = await self._calculate_entry_exit_points(data, indicators, quant_metrics)
            
            # 5. 生成AI專業分析
            ai_analysis = await self._generate_professional_analysis(
                symbol, data, indicators, patterns, quant_metrics, entry_exit
            )
            
            # 6. 組合最終分析結果
            enhanced_analysis = EnhancedAIAnalysis(
                symbol=symbol,
                timestamp=datetime.now(),
                overall_recommendation=ai_analysis.get('recommendation', 'HOLD'),
                confidence=ai_analysis.get('confidence', 0.6),
                pattern_analysis=patterns,
                quantitative_metrics=quant_metrics,
                entry_exit_points=entry_exit,
                market_context=ai_analysis.get('market_context', ''),
                risk_assessment=ai_analysis.get('risk_assessment', ''),
                timeframe_analysis=ai_analysis.get('timeframe_analysis', {}),
                key_levels=ai_analysis.get('key_levels', {})
            )
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Enhanced AI analysis failed for {symbol}: {str(e)}")
            return self._create_fallback_analysis(symbol)
    
    async def _calculate_comprehensive_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """計算全面技術指標"""
        if data.empty:
            return {}
        
        # 基礎指標
        indicators = {}
        
        # RSI
        rsi_14 = self.technical_indicators.calculate_rsi(data['close'], period=14)
        rsi_21 = self.technical_indicators.calculate_rsi(data['close'], period=21)
        
        # MACD
        macd_line, macd_signal, macd_histogram = self.technical_indicators.calculate_macd(data['close'])
        
        # 布林帶
        bb_upper, bb_middle, bb_lower = self.technical_indicators.calculate_bollinger_bands(data['close'])
        
        # 移動平均線
        sma_20 = data['close'].rolling(window=20).mean()
        sma_50 = data['close'].rolling(window=50).mean()
        ema_12 = data['close'].ewm(span=12).mean()
        ema_26 = data['close'].ewm(span=26).mean()
        
        # KDJ指標
        k_percent, d_percent = self._calculate_kdj(data)
        
        # 威廉指標
        williams_r = self._calculate_williams_r(data)
        
        # 成交量指標
        volume_sma = data['volume'].rolling(window=20).mean()
        
        indicators.update({
            'rsi_14': rsi_14.iloc[-1] if not rsi_14.empty else 50,
            'rsi_21': rsi_21.iloc[-1] if not rsi_21.empty else 50,
            'macd_line': macd_line.iloc[-1] if not macd_line.empty else 0,
            'macd_signal': macd_signal.iloc[-1] if not macd_signal.empty else 0,
            'macd_histogram': macd_histogram.iloc[-1] if not macd_histogram.empty else 0,
            'bb_upper': bb_upper.iloc[-1] if not bb_upper.empty else data['close'].iloc[-1] * 1.02,
            'bb_middle': bb_middle.iloc[-1] if not bb_middle.empty else data['close'].iloc[-1],
            'bb_lower': bb_lower.iloc[-1] if not bb_lower.empty else data['close'].iloc[-1] * 0.98,
            'sma_20': sma_20.iloc[-1] if not sma_20.empty else data['close'].iloc[-1],
            'sma_50': sma_50.iloc[-1] if not sma_50.empty else data['close'].iloc[-1],
            'ema_12': ema_12.iloc[-1] if not ema_12.empty else data['close'].iloc[-1],
            'ema_26': ema_26.iloc[-1] if not ema_26.empty else data['close'].iloc[-1],
            'k_percent': k_percent.iloc[-1] if not k_percent.empty else 50,
            'd_percent': d_percent.iloc[-1] if not d_percent.empty else 50,
            'williams_r': williams_r.iloc[-1] if not williams_r.empty else -50,
            'volume_ratio': data['volume'].iloc[-1] / volume_sma.iloc[-1] if not volume_sma.empty else 1.0
        })
        
        return indicators
    
    async def _identify_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """識別圖表型態"""
        patterns = {}
        
        try:
            # 使用現有的型態識別
            breakouts = self.pattern_recognition.detect_breakouts(data)
            triangles = self.pattern_recognition.detect_triangles(data)
            
            # 添加更多型態識別
            support_resistance = self._identify_support_resistance(data)
            trend_lines = self._identify_trend_lines(data)
            
            patterns.update({
                'breakouts': len(breakouts) if breakouts else 0,
                'triangles': len(triangles) if triangles else 0,
                'support_resistance': support_resistance,
                'trend_lines': trend_lines,
                'primary_pattern': self._determine_primary_pattern(data),
                'pattern_strength': self._calculate_pattern_strength(data)
            })
            
        except Exception as e:
            logger.error(f"Pattern identification failed: {str(e)}")
        
        return patterns
    
    async def _calculate_quantitative_metrics(self, data: pd.DataFrame) -> QuantitativeMetrics:
        """計算量化指標"""
        if data.empty:
            return QuantitativeMetrics(0, 0, 0, 0, [], [], 0.5)
        
        # 波動率計算
        returns = data['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100  # 年化波動率
        
        # 成交量比率
        volume_sma = data['volume'].rolling(window=20).mean()
        volume_ratio = data['volume'].iloc[-1] / volume_sma.iloc[-1] if not volume_sma.empty else 1.0
        
        # 價格動量
        price_momentum = (data['close'].iloc[-1] - data['close'].iloc[-20]) / data['close'].iloc[-20] * 100 if len(data) >= 20 else 0
        
        # 趨勢強度
        trend_strength = self._calculate_trend_strength(data)
        
        # 支撐阻力位
        support_levels = self._calculate_support_levels(data)
        resistance_levels = self._calculate_resistance_levels(data)
        
        # 風險評分
        risk_score = self._calculate_risk_score(volatility, volume_ratio, trend_strength)
        
        return QuantitativeMetrics(
            volatility=volatility,
            volume_ratio=volume_ratio,
            price_momentum=price_momentum,
            trend_strength=trend_strength,
            support_levels=support_levels,
            resistance_levels=resistance_levels,
            risk_score=risk_score
        )
    
    async def _calculate_entry_exit_points(
        self,
        data: pd.DataFrame,
        indicators: Dict[str, Any],
        quant_metrics: QuantitativeMetrics
    ) -> EntryExitPoints:
        """計算精確進出場點"""
        current_price = data['close'].iloc[-1]
        
        # 根據技術指標計算進場點
        entry_price = self._calculate_optimal_entry(current_price, indicators, quant_metrics)
        
        # 計算停損點
        stop_loss = self._calculate_stop_loss(entry_price, quant_metrics.support_levels, quant_metrics.volatility)
        
        # 計算目標價
        take_profit = self._calculate_take_profit(entry_price, quant_metrics.resistance_levels, indicators)
        
        # 風險報酬比
        risk_reward_ratio = (take_profit - entry_price) / (entry_price - stop_loss) if entry_price != stop_loss else 1.0
        
        # 建議倉位大小
        position_size_pct = self._calculate_position_size(quant_metrics.risk_score, risk_reward_ratio)
        
        # 信心度評估
        confidence = self._calculate_entry_confidence(indicators, quant_metrics, risk_reward_ratio)
        
        # 推理說明
        reasoning = self._generate_entry_reasoning(indicators, quant_metrics, risk_reward_ratio)
        
        return EntryExitPoints(
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=risk_reward_ratio,
            position_size_pct=position_size_pct,
            confidence=confidence,
            reasoning=reasoning
        )
    
    async def _generate_professional_analysis(
        self,
        symbol: str,
        data: pd.DataFrame,
        indicators: Dict[str, Any],
        patterns: Dict[str, Any],
        quant_metrics: QuantitativeMetrics,
        entry_exit: EntryExitPoints
    ) -> Dict[str, Any]:
        """生成專業AI分析"""
        
        # 準備綜合數據摘要
        analysis_data = {
            'symbol': symbol,
            'current_price': data['close'].iloc[-1],
            'indicators': indicators,
            'patterns': patterns,
            'quantitative': {
                'volatility': quant_metrics.volatility,
                'volume_ratio': quant_metrics.volume_ratio,
                'price_momentum': quant_metrics.price_momentum,
                'trend_strength': quant_metrics.trend_strength,
                'risk_score': quant_metrics.risk_score
            },
            'entry_exit': {
                'entry_price': entry_exit.entry_price,
                'stop_loss': entry_exit.stop_loss,
                'take_profit': entry_exit.take_profit,
                'risk_reward_ratio': entry_exit.risk_reward_ratio
            }
        }
        
        # 創建專業分析提示
        prompt = self._create_professional_analysis_prompt(analysis_data)
        
        try:
            # 獲取AI分析
            response = await self.ai_analyzer._get_ai_response(prompt)
            
            # 解析回應
            analysis = self._parse_professional_response(response)
            
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return self._create_fallback_ai_analysis(symbol)
    
    def _create_professional_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """創建專業分析提示"""
        return f"""
作為專業量化分析師，請基於以下數據提供深度技術分析：

股票代碼: {data['symbol']}
當前價格: ${data['current_price']:.2f}

技術指標:
- RSI(14): {data['indicators'].get('rsi_14', 50):.1f}
- MACD: {data['indicators'].get('macd_line', 0):.3f}
- 布林帶位置: 當前價格相對於中軌的位置
- KD指標: K={data['indicators'].get('k_percent', 50):.1f}, D={data['indicators'].get('d_percent', 50):.1f}

量化數據:
- 年化波動率: {data['quantitative']['volatility']:.1f}%
- 成交量比率: {data['quantitative']['volume_ratio']:.2f}倍
- 價格動量: {data['quantitative']['price_momentum']:.2f}%
- 趨勢強度: {data['quantitative']['trend_strength']:.2f}

進出場分析:
- 建議進場價: ${data['entry_exit']['entry_price']:.2f}
- 停損點: ${data['entry_exit']['stop_loss']:.2f}
- 目標價: ${data['entry_exit']['take_profit']:.2f}
- 風險報酬比: {data['entry_exit']['risk_reward_ratio']:.2f}

請提供專業分析，包含：
1. 總體建議 (BUY/SELL/HOLD)
2. 信心度評估 (0.0-1.0)
3. 市場背景分析
4. 風險評估
5. 短期/中期/長期展望
6. 關鍵支撐阻力位

請以JSON格式回應，包含所有必要欄位。
"""
    
    def _calculate_kdj(self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """計算KDJ指標"""
        if len(data) < k_period:
            return pd.Series([50] * len(data), index=data.index), pd.Series([50] * len(data), index=data.index)
        
        low_min = data['low'].rolling(window=k_period).min()
        high_max = data['high'].rolling(window=k_period).max()
        
        rsv = (data['close'] - low_min) / (high_max - low_min) * 100
        k_percent = rsv.ewm(alpha=1/d_period).mean()
        d_percent = k_percent.ewm(alpha=1/d_period).mean()
        
        return k_percent, d_percent
    
    def _calculate_williams_r(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """計算威廉指標"""
        if len(data) < period:
            return pd.Series([-50] * len(data), index=data.index)
        
        high_max = data['high'].rolling(window=period).max()
        low_min = data['low'].rolling(window=period).min()
        
        williams_r = (high_max - data['close']) / (high_max - low_min) * -100
        return williams_r
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """計算趨勢強度"""
        if len(data) < 20:
            return 0.5
        
        # 使用ADX概念計算趨勢強度
        high_diff = data['high'].diff()
        low_diff = -data['low'].diff()
        
        plus_dm = np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0)
        minus_dm = np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0)
        
        tr = np.maximum(data['high'] - data['low'], 
                       np.maximum(abs(data['high'] - data['close'].shift(1)),
                                 abs(data['low'] - data['close'].shift(1))))
        
        plus_di = 100 * (pd.Series(plus_dm).rolling(14).mean() / pd.Series(tr).rolling(14).mean())
        minus_di = 100 * (pd.Series(minus_dm).rolling(14).mean() / pd.Series(tr).rolling(14).mean())
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(14).mean()
        
        return adx.iloc[-1] / 100.0 if not adx.empty else 0.5
    
    def _calculate_support_levels(self, data: pd.DataFrame, periods: List[int] = [20, 50]) -> List[float]:
        """計算支撐位"""
        support_levels = []
        
        for period in periods:
            if len(data) >= period:
                low_min = data['low'].rolling(window=period).min()
                support_levels.append(low_min.iloc[-1])
        
        # 添加近期低點
        recent_lows = data['low'].tail(10)
        local_min = recent_lows.min()
        support_levels.append(local_min)
        
        return sorted(list(set([round(level, 2) for level in support_levels if level > 0])))
    
    def _calculate_resistance_levels(self, data: pd.DataFrame, periods: List[int] = [20, 50]) -> List[float]:
        """計算阻力位"""
        resistance_levels = []
        
        for period in periods:
            if len(data) >= period:
                high_max = data['high'].rolling(window=period).max()
                resistance_levels.append(high_max.iloc[-1])
        
        # 添加近期高點
        recent_highs = data['high'].tail(10)
        local_max = recent_highs.max()
        resistance_levels.append(local_max)
        
        return sorted(list(set([round(level, 2) for level in resistance_levels if level > 0])), reverse=True)
    
    def _calculate_risk_score(self, volatility: float, volume_ratio: float, trend_strength: float) -> float:
        """計算風險評分 (0-1, 1為最高風險)"""
        # 波動率風險 (正常波動率約20-30%)
        vol_risk = min(volatility / 50.0, 1.0)
        
        # 成交量風險 (異常成交量可能表示風險)
        vol_ratio_risk = abs(volume_ratio - 1.0) / 2.0
        vol_ratio_risk = min(vol_ratio_risk, 1.0)
        
        # 趨勢風險 (弱趨勢風險較高)
        trend_risk = 1.0 - trend_strength
        
        # 綜合風險評分
        total_risk = (vol_risk * 0.4 + vol_ratio_risk * 0.3 + trend_risk * 0.3)
        return min(max(total_risk, 0.0), 1.0)
    
    def _calculate_optimal_entry(self, current_price: float, indicators: Dict, quant_metrics: QuantitativeMetrics) -> float:
        """計算最佳進場價"""
        # 基於多個指標計算建議進場價
        entry_signals = []
        
        # 布林帶中軌作為參考
        bb_middle = indicators.get('bb_middle', current_price)
        entry_signals.append(bb_middle)
        
        # 20日均線
        sma_20 = indicators.get('sma_20', current_price)
        entry_signals.append(sma_20)
        
        # 支撐位附近
        if quant_metrics.support_levels:
            nearest_support = max([s for s in quant_metrics.support_levels if s <= current_price * 1.02], 
                                default=current_price * 0.98)
            entry_signals.append(nearest_support)
        
        # 當前價格也考慮進去
        entry_signals.append(current_price)
        
        # 取平均值作為建議進場價
        optimal_entry = np.mean(entry_signals)
        
        # 確保進場價合理（不超過當前價格的±3%）
        max_entry = current_price * 1.03
        min_entry = current_price * 0.97
        
        return max(min_entry, min(optimal_entry, max_entry))
    
    def _calculate_stop_loss(self, entry_price: float, support_levels: List[float], volatility: float) -> float:
        """計算停損點"""
        # 方法1: 基於支撐位
        support_stop = None
        if support_levels:
            nearby_supports = [s for s in support_levels if s < entry_price * 0.95]
            if nearby_supports:
                support_stop = max(nearby_supports)
        
        # 方法2: 基於ATR/波動率
        atr_stop = entry_price * (1 - min(volatility / 100 * 2, 0.15))  # 最多15%停損
        
        # 方法3: 固定百分比停損
        fixed_stop = entry_price * 0.92  # 8%停損
        
        # 選擇最保守的停損點
        stop_candidates = [s for s in [support_stop, atr_stop, fixed_stop] if s is not None]
        
        if stop_candidates:
            return max(stop_candidates)
        else:
            return entry_price * 0.92  # 默認8%停損
    
    def _calculate_take_profit(self, entry_price: float, resistance_levels: List[float], indicators: Dict) -> float:
        """計算目標價"""
        # 方法1: 基於阻力位
        resistance_target = None
        if resistance_levels:
            nearby_resistance = [r for r in resistance_levels if r > entry_price * 1.05]
            if nearby_resistance:
                resistance_target = min(nearby_resistance)
        
        # 方法2: 基於布林帶上軌
        bb_upper = indicators.get('bb_upper', entry_price * 1.1)
        bb_target = bb_upper if bb_upper > entry_price * 1.02 else entry_price * 1.08
        
        # 方法3: 固定風險報酬比目標
        fixed_target = entry_price * 1.15  # 15%獲利目標
        
        # 選擇最合理的目標價
        target_candidates = [t for t in [resistance_target, bb_target, fixed_target] if t is not None]
        
        if target_candidates:
            return min(target_candidates)  # 選擇最保守的目標
        else:
            return entry_price * 1.1  # 默認10%獲利目標
    
    def _calculate_position_size(self, risk_score: float, risk_reward_ratio: float) -> float:
        """計算建議倉位大小 (百分比)"""
        # 基礎倉位
        base_position = 0.1  # 10%
        
        # 根據風險評分調整
        risk_adjustment = 1.0 - risk_score  # 風險越高，倉位越小
        
        # 根據風險報酬比調整
        rr_adjustment = min(risk_reward_ratio / 2.0, 1.5)  # 最多1.5倍調整
        
        # 計算最終倉位
        position_size = base_position * risk_adjustment * rr_adjustment
        
        # 限制在1%-25%之間
        return max(0.01, min(position_size, 0.25))
    
    def _calculate_entry_confidence(self, indicators: Dict, quant_metrics: QuantitativeMetrics, risk_reward_ratio: float) -> float:
        """計算進場信心度"""
        confidence_factors = []
        
        # RSI信心度
        rsi = indicators.get('rsi_14', 50)
        if 30 <= rsi <= 70:
            confidence_factors.append(0.8)
        elif 20 <= rsi <= 80:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.4)
        
        # 趨勢強度信心度
        confidence_factors.append(quant_metrics.trend_strength)
        
        # 風險報酬比信心度
        rr_confidence = min(risk_reward_ratio / 3.0, 1.0)  # 3:1以上為滿分
        confidence_factors.append(rr_confidence)
        
        # 成交量信心度
        vol_confidence = min(quant_metrics.volume_ratio / 2.0, 1.0)
        confidence_factors.append(vol_confidence)
        
        # 平均信心度
        return np.mean(confidence_factors)
    
    def _generate_entry_reasoning(self, indicators: Dict, quant_metrics: QuantitativeMetrics, risk_reward_ratio: float) -> str:
        """生成進場推理說明"""
        reasoning_parts = []
        
        # RSI分析
        rsi = indicators.get('rsi_14', 50)
        if rsi < 30:
            reasoning_parts.append("RSI顯示超賣，可能出現反彈")
        elif rsi > 70:
            reasoning_parts.append("RSI顯示超買，需謹慎進場")
        else:
            reasoning_parts.append("RSI處於健康區間")
        
        # 趨勢分析
        if quant_metrics.trend_strength > 0.6:
            reasoning_parts.append("趨勢強勁，順勢操作機會佳")
        elif quant_metrics.trend_strength < 0.3:
            reasoning_parts.append("趨勢較弱，建議觀望")
        
        # 風險報酬比
        if risk_reward_ratio >= 2.0:
            reasoning_parts.append(f"風險報酬比{risk_reward_ratio:.1f}:1，具有良好的投資價值")
        else:
            reasoning_parts.append("風險報酬比偏低，需要謹慎評估")
        
        # 成交量
        if quant_metrics.volume_ratio > 1.5:
            reasoning_parts.append("成交量放大，顯示市場關注度提升")
        
        return "；".join(reasoning_parts)
    
    def _identify_support_resistance(self, data: pd.DataFrame) -> Dict[str, List[float]]:
        """識別支撐阻力位"""
        return {
            'support': self._calculate_support_levels(data),
            'resistance': self._calculate_resistance_levels(data)
        }
    
    def _identify_trend_lines(self, data: pd.DataFrame) -> Dict[str, Any]:
        """識別趨勢線"""
        # 簡單的趨勢線識別
        if len(data) < 20:
            return {'direction': 'sideways', 'strength': 0.5}
        
        recent_data = data.tail(20)
        price_change = (recent_data['close'].iloc[-1] - recent_data['close'].iloc[0]) / recent_data['close'].iloc[0]
        
        if price_change > 0.05:
            return {'direction': 'uptrend', 'strength': min(abs(price_change) * 10, 1.0)}
        elif price_change < -0.05:
            return {'direction': 'downtrend', 'strength': min(abs(price_change) * 10, 1.0)}
        else:
            return {'direction': 'sideways', 'strength': 0.3}
    
    def _determine_primary_pattern(self, data: pd.DataFrame) -> str:
        """判斷主要型態"""
        if len(data) < 20:
            return "數據不足"
        
        # 簡單型態識別邏輯
        recent_highs = data['high'].tail(10)
        recent_lows = data['low'].tail(10)
        
        high_trend = recent_highs.iloc[-1] - recent_highs.iloc[0]
        low_trend = recent_lows.iloc[-1] - recent_lows.iloc[0]
        
        if high_trend > 0 and low_trend > 0:
            return "上升通道"
        elif high_trend < 0 and low_trend < 0:
            return "下降通道"
        elif high_trend > 0 and low_trend < 0:
            return "擴散三角形"
        elif high_trend < 0 and low_trend > 0:
            return "收斂三角形"
        else:
            return "橫盤整理"
    
    def _calculate_pattern_strength(self, data: pd.DataFrame) -> float:
        """計算型態強度"""
        if len(data) < 10:
            return 0.5
        
        # 基於價格波動和成交量計算型態強度
        price_volatility = data['close'].tail(10).std() / data['close'].tail(10).mean()
        volume_consistency = 1.0 - (data['volume'].tail(10).std() / data['volume'].tail(10).mean())
        
        pattern_strength = (1.0 - price_volatility) * 0.6 + volume_consistency * 0.4
        return max(0.0, min(pattern_strength, 1.0))
    
    def _parse_professional_response(self, response: str) -> Dict[str, Any]:
        """解析專業AI回應"""
        try:
            # 嘗試解析JSON
            if '{' in response and '}' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                
                import json
                return json.loads(json_str)
        except:
            pass
        
        # 備用解析
        return self._create_fallback_ai_analysis("Unknown")
    
    def _create_fallback_analysis(self, symbol: str) -> EnhancedAIAnalysis:
        """創建備用分析結果"""
        current_time = datetime.now()
        
        return EnhancedAIAnalysis(
            symbol=symbol,
            timestamp=current_time,
            overall_recommendation="HOLD",
            confidence=0.5,
            pattern_analysis={'primary_pattern': '數據不足', 'pattern_strength': 0.3},
            quantitative_metrics=QuantitativeMetrics(25.0, 1.0, 0.0, 0.5, [], [], 0.5),
            entry_exit_points=EntryExitPoints(100.0, 95.0, 110.0, 2.0, 0.05, 0.5, "系統分析異常"),
            market_context="暫時無法取得市場分析",
            risk_assessment="中等風險",
            timeframe_analysis={'短期': '觀望', '中期': '持有', '長期': '待評估'},
            key_levels={'support': 95.0, 'resistance': 110.0}
        )
    
    def _create_fallback_ai_analysis(self, symbol: str) -> Dict[str, Any]:
        """創建備用AI分析"""
        return {
            'recommendation': 'HOLD',
            'confidence': 0.5,
            'market_context': '系統暫時無法進行深度分析',
            'risk_assessment': '建議謹慎操作，風險中等',
            'timeframe_analysis': {
                '短期': '觀望為主',
                '中期': '持有策略',
                '長期': '待後續評估'
            },
            'key_levels': {
                'support': 0.0,
                'resistance': 0.0
            }
        }

# 使用範例
if __name__ == "__main__":
    async def test_enhanced_analyzer():
        analyzer = EnhancedAIAnalyzer()
        
        # 創建測試數據
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range('2024-01-01', periods=60, freq='D')
        np.random.seed(42)
        
        close_prices = 100 + np.cumsum(np.random.randn(60) * 0.5)
        test_data = pd.DataFrame({
            'open': close_prices + np.random.randn(60) * 0.3,
            'high': close_prices + np.random.rand(60) * 2,
            'low': close_prices - np.random.rand(60) * 2,
            'close': close_prices,
            'volume': np.random.randint(1000000, 5000000, 60)
        }, index=dates)
        
        # 執行增強分析
        analysis = await analyzer.analyze_stock_comprehensive('AAPL', test_data)
        
        print(f"Enhanced Analysis for {analysis.symbol}:")
        print(f"Recommendation: {analysis.overall_recommendation}")
        print(f"Confidence: {analysis.confidence:.2f}")
        print(f"Entry Price: ${analysis.entry_exit_points.entry_price:.2f}")
        print(f"Stop Loss: ${analysis.entry_exit_points.stop_loss:.2f}")
        print(f"Take Profit: ${analysis.entry_exit_points.take_profit:.2f}")
        print(f"Risk-Reward Ratio: {analysis.entry_exit_points.risk_reward_ratio:.2f}")
    
    # 運行測試
    # asyncio.run(test_enhanced_analyzer())