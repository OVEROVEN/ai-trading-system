#!/usr/bin/env python3
"""
AI 策略顧問 - 與 ChatGPT 討論交易策略和回測優化
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class StrategyDiscussion:
    """策略討論結果"""
    strategy_name: str
    market_analysis: str
    strategy_recommendation: str
    parameter_suggestions: Dict[str, Any]
    risk_assessment: str
    optimization_suggestions: List[str]
    backtesting_recommendations: str
    confidence_score: float
    discussion_summary: str

@dataclass
class BacktestOptimization:
    """回測優化建議"""
    current_performance: Dict[str, float]
    improvement_areas: List[str]
    parameter_adjustments: Dict[str, Any]
    risk_management_suggestions: List[str]
    market_condition_analysis: str
    optimization_confidence: float

class AIStrategyAdvisor:
    """AI 策略顧問"""
    
    def __init__(self):
        """初始化 AI 策略顧問"""
        self.client = None
        self.model = "gpt-3.5-turbo"  # 更快更便宜的模型，適合交易分析
        
        if OPENAI_AVAILABLE and settings.openai_api_key:
            try:
                self.client = OpenAI(api_key=settings.openai_api_key)
                logger.info("AI 策略顧問初始化成功")
            except Exception as e:
                logger.error(f"OpenAI 初始化失敗: {str(e)}")
        else:
            logger.warning("OpenAI 不可用，AI 策略顧問功能受限")
    
    async def discuss_strategy(self, 
                             symbol: str, 
                             market_data: pd.DataFrame,
                             technical_indicators: Dict[str, Any],
                             patterns: Dict[str, Any],
                             current_strategy: str = None,
                             user_question: str = None) -> StrategyDiscussion:
        """
        與 AI 討論交易策略
        
        Args:
            symbol: 股票代號
            market_data: 市場數據
            technical_indicators: 技術指標
            patterns: 檢測到的形態
            current_strategy: 當前策略名稱
            user_question: 用戶的具體問題
        """
        
        if not self.client:
            return self._create_fallback_discussion(symbol, current_strategy)
        
        try:
            # 準備市場分析數據
            market_summary = self._prepare_market_summary(symbol, market_data, technical_indicators, patterns)
            
            # 構建 AI 提示
            prompt = self._build_strategy_discussion_prompt(
                symbol, market_summary, current_strategy, user_question
            )
            
            # 調用 ChatGPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_strategy_advisor_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # 解析回應
            ai_response = response.choices[0].message.content
            return self._parse_strategy_discussion(ai_response, symbol, current_strategy)
            
        except Exception as e:
            logger.error(f"AI 策略討論失敗: {str(e)}")
            return self._create_fallback_discussion(symbol, current_strategy)
    
    async def optimize_backtest_results(self,
                                      symbol: str,
                                      strategy_name: str,
                                      backtest_results: Dict[str, Any],
                                      market_data: pd.DataFrame,
                                      strategy_parameters: Dict[str, Any]) -> BacktestOptimization:
        """
        基於回測結果優化策略
        
        Args:
            symbol: 股票代號
            strategy_name: 策略名稱
            backtest_results: 回測結果
            market_data: 市場數據
            strategy_parameters: 策略參數
        """
        
        if not self.client:
            return self._create_fallback_optimization(backtest_results)
        
        try:
            # 準備回測分析數據
            performance_summary = self._prepare_performance_summary(backtest_results, market_data)
            
            # 構建優化提示
            prompt = self._build_optimization_prompt(
                symbol, strategy_name, performance_summary, strategy_parameters
            )
            
            # 調用 ChatGPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_optimization_advisor_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            # 解析回應
            ai_response = response.choices[0].message.content
            return self._parse_optimization_response(ai_response, backtest_results)
            
        except Exception as e:
            logger.error(f"AI 回測優化失敗: {str(e)}")
            return self._create_fallback_optimization(backtest_results)
    
    async def answer_strategy_question(self,
                                     question: str,
                                     context: Dict[str, Any] = None) -> str:
        """
        回答策略相關問題
        
        Args:
            question: 用戶問題
            context: 上下文資訊 (股票數據、策略等)
        """
        
        if not self.client:
            return "抱歉，AI 顧問服務暫時不可用。請檢查 OpenAI API 設定。"
        
        try:
            # 構建問答提示
            context_str = self._format_context(context) if context else ""
            
            prompt = f"""
            用戶問題: {question}
            
            {context_str}
            
            請提供專業的交易策略建議和分析。
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_qa_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI 問答失敗: {str(e)}")
            return f"抱歉，處理您的問題時發生錯誤: {str(e)}"
    
    def _prepare_market_summary(self, symbol: str, data: pd.DataFrame, 
                               indicators: Dict[str, Any], patterns: Dict[str, Any]) -> str:
        """準備市場分析摘要"""
        
        if data.empty:
            return f"{symbol} 數據不足"
        
        latest = data.iloc[-1]
        price_change = ((latest['close'] - data['close'].iloc[0]) / data['close'].iloc[0]) * 100
        
        summary = f"""
        股票: {symbol}
        分析期間: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}
        當前價格: ${latest['close']:.2f}
        期間報酬: {price_change:.2f}%
        
        技術指標:
        - RSI: {indicators.get('rsi', 'N/A')}
        - MACD: {indicators.get('macd', 'N/A')}
        - 20日均線: ${indicators.get('sma_20', 'N/A')}
        - 50日均線: ${indicators.get('sma_50', 'N/A')}
        
        檢測到的形態:
        """
        
        for pattern_type, pattern_list in patterns.items():
            if pattern_list:
                summary += f"- {pattern_type}: {len(pattern_list)} 個\n"
        
        return summary
    
    def _prepare_performance_summary(self, results: Dict[str, Any], data: pd.DataFrame) -> str:
        """準備績效分析摘要"""
        
        perf = results.get('performance_metrics', {})
        trades = results.get('trade_statistics', {})
        
        summary = f"""
        回測績效摘要:
        
        報酬指標:
        - 總報酬率: {perf.get('total_return_pct', 0):.2f}%
        - 夏普比率: {perf.get('sharpe_ratio', 0):.2f}
        - 最大回撤: {perf.get('max_drawdown_pct', 0):.2f}%
        - 波動率: {perf.get('volatility', 0):.2f}%
        
        交易統計:
        - 總交易次數: {trades.get('total_trades', 0)}
        - 勝率: {trades.get('win_rate', 0):.1f}%
        - 獲利因子: {trades.get('profit_factor', 0):.2f}
        - 平均獲利: ${trades.get('avg_profit', 0):.2f}
        - 平均虧損: ${trades.get('avg_loss', 0):.2f}
        
        市場環境:
        - 分析期間: {len(data)} 個交易日
        - 市場波動: {data['close'].std() / data['close'].mean() * 100:.2f}%
        """
        
        return summary
    
    def _build_strategy_discussion_prompt(self, symbol: str, market_summary: str, 
                                        current_strategy: str, user_question: str) -> str:
        """構建策略討論提示"""
        
        prompt = f"""
        請基於以下市場分析，提供專業的交易策略建議：
        
        {market_summary}
        
        當前策略: {current_strategy or '尚未選定'}
        
        用戶問題: {user_question or '請提供策略建議'}
        
        請提供：
        1. 市場分析 (趨勢、支撐阻力、風險因子)
        2. 策略建議 (適合的策略類型、進出場時機)
        3. 參數建議 (具體的策略參數設定)
        4. 風險評估 (潛在風險和應對措施)
        5. 優化建議 (策略改進方向)
        6. 回測建議 (測試重點和注意事項)
        7. 信心評分 (1-10分)
        
        請用專業但易懂的方式回答，並提供具體可執行的建議。
        """
        
        return prompt
    
    def _build_optimization_prompt(self, symbol: str, strategy_name: str, 
                                 performance_summary: str, parameters: Dict[str, Any]) -> str:
        """構建優化提示"""
        
        prompt = f"""
        請基於以下回測結果，提供策略優化建議：
        
        股票: {symbol}
        策略: {strategy_name}
        當前參數: {json.dumps(parameters, indent=2)}
        
        {performance_summary}
        
        請分析：
        1. 當前績效評估 (優點和缺點)
        2. 主要改進領域 (哪些指標需要優化)
        3. 參數調整建議 (具體的參數修改)
        4. 風險管理建議 (停損停利、倉位管理)
        5. 市場適應性 (不同市況下的表現)
        6. 優化信心度 (改進的可能性)
        
        請提供具體、可執行的優化方案。
        """
        
        return prompt
    
    def _get_strategy_advisor_system_prompt(self) -> str:
        """獲取策略顧問系統提示"""
        return """
        你是一位專業的股票交易策略顧問，具有豐富的技術分析和量化交易經驗。
        
        你的專長包括：
        - 技術分析 (技術指標、圖表形態)
        - 量化策略 (回測、參數優化)
        - 風險管理 (停損停利、倉位管理)
        - 市場心理學 (情緒指標、市場週期)
        
        請提供：
        - 基於數據的客觀分析
        - 具體可執行的策略建議
        - 清晰的風險評估
        - 實用的優化建議
        
        回答要專業但易懂，並且務實可行。
        """
    
    def _get_optimization_advisor_system_prompt(self) -> str:
        """獲取優化顧問系統提示"""
        return """
        你是一位量化交易策略優化專家，擅長分析回測結果並提供改進建議。
        
        你的核心能力：
        - 績效指標分析 (報酬、風險、穩定性)
        - 參數優化 (過度擬合檢測、穩健性測試)
        - 風險控制 (回撤管理、風險調整報酬)
        - 策略改進 (訊號質量、進出場邏輯)
        
        請基於回測數據提供：
        - 客觀的績效評估
        - 具體的改進方案
        - 參數調整建議
        - 風險控制措施
        
        注重實用性和可執行性。
        """
    
    def _get_qa_system_prompt(self) -> str:
        """獲取問答系統提示"""
        return """
        你是一位專業的交易策略顧問，能夠回答各種股票交易和策略相關的問題。
        
        請提供：
        - 準確的專業知識
        - 實用的建議
        - 清晰的解釋
        - 風險提醒
        
        用繁體中文回答，保持專業且易懂。
        """
    
    def _parse_strategy_discussion(self, ai_response: str, symbol: str, strategy: str) -> StrategyDiscussion:
        """解析策略討論回應"""
        
        # 簡化的解析邏輯 - 實際可以更複雜
        lines = ai_response.split('\n')
        
        # 嘗試提取關鍵信息
        market_analysis = ""
        strategy_recommendation = ""
        optimization_suggestions = []
        
        current_section = ""
        for line in lines:
            line = line.strip()
            if '市場分析' in line or '市場' in line:
                current_section = "market"
            elif '策略建議' in line or '建議' in line:
                current_section = "strategy"
            elif '優化' in line:
                current_section = "optimization"
            elif line and current_section:
                if current_section == "market":
                    market_analysis += line + "\n"
                elif current_section == "strategy":
                    strategy_recommendation += line + "\n"
                elif current_section == "optimization":
                    optimization_suggestions.append(line)
        
        return StrategyDiscussion(
            strategy_name=strategy or "AI建議策略",
            market_analysis=market_analysis or ai_response[:200] + "...",
            strategy_recommendation=strategy_recommendation or ai_response[:200] + "...",
            parameter_suggestions={},
            risk_assessment="請參考 AI 完整回應",
            optimization_suggestions=optimization_suggestions or ["請參考 AI 完整回應"],
            backtesting_recommendations="建議進行3-6個月的回測驗證",
            confidence_score=0.75,
            discussion_summary=ai_response
        )
    
    def _parse_optimization_response(self, ai_response: str, results: Dict[str, Any]) -> BacktestOptimization:
        """解析優化回應"""
        
        return BacktestOptimization(
            current_performance=results.get('performance_metrics', {}),
            improvement_areas=["請參考 AI 完整分析"],
            parameter_adjustments={},
            risk_management_suggestions=["請參考 AI 建議"],
            market_condition_analysis=ai_response[:300] + "...",
            optimization_confidence=0.7
        )
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """格式化上下文"""
        if not context:
            return ""
        
        formatted = "相關資訊:\n"
        for key, value in context.items():
            formatted += f"- {key}: {value}\n"
        
        return formatted
    
    def _create_fallback_discussion(self, symbol: str, strategy: str) -> StrategyDiscussion:
        """創建備用討論結果"""
        return StrategyDiscussion(
            strategy_name=strategy or "基礎策略",
            market_analysis=f"{symbol} 市場分析需要 OpenAI API",
            strategy_recommendation="建議使用技術指標組合策略",
            parameter_suggestions={"rsi_period": 14, "macd_fast": 12, "macd_slow": 26},
            risk_assessment="中等風險，建議設定2%停損",
            optimization_suggestions=["優化參數", "增加確認信號", "改善風險管理"],
            backtesting_recommendations="建議進行至少6個月的回測",
            confidence_score=0.5,
            discussion_summary="AI 顧問暫時不可用，請檢查 OpenAI API 設定"
        )
    
    def _create_fallback_optimization(self, results: Dict[str, Any]) -> BacktestOptimization:
        """創建備用優化結果"""
        return BacktestOptimization(
            current_performance=results.get('performance_metrics', {}),
            improvement_areas=["需要 AI 分析"],
            parameter_adjustments={},
            risk_management_suggestions=["設定合理停損", "控制倉位大小"],
            market_condition_analysis="需要 OpenAI API 進行深度分析",
            optimization_confidence=0.5
        )