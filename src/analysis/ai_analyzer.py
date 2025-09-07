import openai
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
import logging
import base64
from io import BytesIO
from datetime import datetime
import asyncio
import aiohttp

try:
    from PIL import Image
    import matplotlib.pyplot as plt
    import mplfinance as mpf
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    logging.warning("Plotting libraries not available. Chart analysis will be limited.")

from config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class AIAnalysisResult:
    symbol: str
    analysis_type: str
    timestamp: datetime
    confidence: float
    recommendation: str  # 'BUY', 'SELL', 'HOLD'
    reasoning: str
    key_factors: List[str]
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None
    risk_score: Optional[float] = None
    entry_price: Optional[float] = None  # New field for specific entry price

class OpenAIAnalyzer:
    """
    AI-powered trading analysis using OpenAI's GPT models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        
    async def analyze_technical_data(
        self, 
        symbol: str,
        data: pd.DataFrame,
        indicators: Dict[str, Any],
        patterns: Dict[str, List],
        context: Optional[str] = None,
        language: str = "en"
    ) -> AIAnalysisResult:
        """
        Analyze technical data using AI.
        
        Args:
            symbol: Stock symbol
            data: OHLCV DataFrame
            indicators: Technical indicators
            patterns: Detected patterns
            context: Additional context
            
        Returns:
            AI analysis result
        """
        # 強制打印到控制台來追踪
        print(f"🔍 [AI ANALYZER] Called analyze_technical_data for {symbol} with language: {language}")
        logger.info(f"🔍 [AI ANALYZER] Called analyze_technical_data for {symbol} with language: {language}")
        
        try:
            # Prepare data summary for AI
            print(f"🔄 [AI ANALYZER] Preparing technical summary for {symbol}...")
            data_summary = self._prepare_technical_summary(symbol, data, indicators, patterns)
            print(f"📊 [AI ANALYZER] Data summary keys: {list(data_summary.keys())}")
            
            # Create prompt with language parameter
            print(f"📝 [AI ANALYZER] Creating prompt with language: {language}")
            prompt = self._create_technical_analysis_prompt(data_summary, context, language)
            print(f"✉️ [AI ANALYZER] Prompt created, length: {len(prompt)} chars")
            print(f"🔤 [AI ANALYZER] Prompt preview: {prompt[:200]}...")
            
            # Get AI response
            print(f"🤖 [AI ANALYZER] Calling OpenAI API...")
            response = await self._get_ai_response(prompt, language)
            print(f"✅ [AI ANALYZER] OpenAI response received, length: {len(response)} chars")
            
            # Parse response
            print(f"🔍 [AI ANALYZER] Parsing AI response...")
            analysis = self._parse_ai_response(symbol, response, 'technical_analysis')
            print(f"✅ [AI ANALYZER] Analysis complete for {symbol}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI technical analysis: {str(e)}")
            return self._create_fallback_analysis(symbol, 'technical_analysis', language)
    
    async def analyze_chart_image(
        self, 
        symbol: str,
        chart_image: bytes,
        timeframe: str = "1D",
        context: Optional[str] = None
    ) -> AIAnalysisResult:
        """
        Analyze a chart image using OpenAI's vision capabilities.
        
        Args:
            symbol: Stock symbol
            chart_image: Chart image bytes
            timeframe: Chart timeframe
            context: Additional context
            
        Returns:
            AI analysis result
        """
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(chart_image).decode('utf-8')
            
            # Create vision prompt
            prompt = self._create_chart_analysis_prompt(symbol, timeframe, context)
            
            # Use GPT-4 Vision
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            # Parse response
            analysis = self._parse_ai_response(symbol, response.choices[0].message.content, 'chart_analysis')
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI chart analysis: {str(e)}")
            return self._create_fallback_analysis(symbol, 'chart_analysis')
    
    async def analyze_market_sentiment(
        self,
        symbol: str,
        news_headlines: List[str],
        social_sentiment: Optional[Dict] = None,
        earnings_data: Optional[Dict] = None,
        language: str = "en"
    ) -> AIAnalysisResult:
        """
        Analyze market sentiment using AI.
        
        Args:
            symbol: Stock symbol
            news_headlines: List of recent news headlines
            social_sentiment: Social media sentiment data
            earnings_data: Recent earnings information
            
        Returns:
            AI sentiment analysis result
        """
        try:
            # Prepare sentiment data
            sentiment_summary = self._prepare_sentiment_summary(
                symbol, news_headlines, social_sentiment, earnings_data
            )
            
            # Create prompt
            prompt = self._create_sentiment_analysis_prompt(sentiment_summary)
            
            # Get AI response
            response = await self._get_ai_response(prompt, language)
            
            # Parse response
            analysis = self._parse_ai_response(symbol, response, 'sentiment_analysis')
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI sentiment analysis: {str(e)}")
            return self._create_fallback_analysis(symbol, 'sentiment_analysis')
    
    async def generate_trading_strategy(
        self,
        symbol: str,
        technical_analysis: AIAnalysisResult,
        sentiment_analysis: AIAnalysisResult,
        risk_tolerance: str = "moderate",
        investment_horizon: str = "medium_term",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive trading strategy using AI.
        
        Args:
            symbol: Stock symbol
            technical_analysis: Technical analysis result
            sentiment_analysis: Sentiment analysis result
            risk_tolerance: Risk tolerance level
            investment_horizon: Investment time horizon
            
        Returns:
            Comprehensive trading strategy
        """
        try:
            # Combine analyses
            combined_data = {
                'symbol': symbol,
                'technical': {
                    'recommendation': technical_analysis.recommendation,
                    'confidence': technical_analysis.confidence,
                    'reasoning': technical_analysis.reasoning,
                    'key_factors': technical_analysis.key_factors
                },
                'sentiment': {
                    'recommendation': sentiment_analysis.recommendation,
                    'confidence': sentiment_analysis.confidence,
                    'reasoning': sentiment_analysis.reasoning,
                    'key_factors': sentiment_analysis.key_factors
                },
                'risk_tolerance': risk_tolerance,
                'investment_horizon': investment_horizon
            }
            
            # Create strategy prompt
            prompt = self._create_strategy_prompt(combined_data)
            
            # Get AI response
            response = await self._get_ai_response(prompt, language)
            
            # Parse strategy response
            strategy = self._parse_strategy_response(response)
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error generating trading strategy: {str(e)}")
            return self._create_fallback_strategy(symbol)
    
    def _prepare_technical_summary(
        self, 
        symbol: str, 
        data: pd.DataFrame, 
        indicators: Dict, 
        patterns: Dict
    ) -> Dict[str, Any]:
        """Prepare technical data summary for AI analysis."""
        if data.empty:
            logger.error(f"Data is empty for symbol {symbol}")
            return {}
        
        # Debug logging
        logger.info(f"DataFrame columns: {list(data.columns)}")
        logger.info(f"DataFrame shape: {data.shape}")
        
        try:
            latest = data.iloc[-1]
            prev_week = data.tail(5)
            
            # Check for required columns
            required_cols = ['close', 'volume']
            missing_cols = [col for col in required_cols if col not in data.columns]
            if missing_cols:
                logger.error(f"Missing columns {missing_cols} in data for {symbol}")
                return {}
            
            summary = {
                'symbol': symbol,
                'current_price': latest['close'],
                'price_change_1d': ((latest['close'] - data.iloc[-2]['close']) / data.iloc[-2]['close']) * 100 if len(data) > 1 else 0,
                'price_change_5d': ((latest['close'] - prev_week.iloc[0]['close']) / prev_week.iloc[0]['close']) * 100 if len(prev_week) >= 5 else 0,
                'volume_ratio': latest['volume'] / data['volume'].rolling(20).mean().iloc[-1] if len(data) >= 20 else 1,
                'indicators': {},
                'patterns': {}
            }
            
            # Add key indicators
            indicator_fields = ['rsi', 'macd', 'macd_signal', 'bb_upper', 'bb_lower', 'sma_20', 'sma_50']
            for field in indicator_fields:
                if field in data.columns and not pd.isna(latest.get(field)):
                    summary['indicators'][field] = latest[field]
            
            # Add patterns summary
            for pattern_type, pattern_list in patterns.items():
                if pattern_list:
                    summary['patterns'][pattern_type] = len(pattern_list)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error preparing technical summary for {symbol}: {str(e)}")
            return {}
    
    def _prepare_sentiment_summary(
        self,
        symbol: str,
        news_headlines: List[str],
        social_sentiment: Optional[Dict],
        earnings_data: Optional[Dict]
    ) -> Dict[str, Any]:
        """Prepare sentiment data summary for AI analysis."""
        summary = {
            'symbol': symbol,
            'news_headlines': news_headlines[:10],  # Limit to recent 10
            'social_sentiment': social_sentiment or {},
            'earnings_data': earnings_data or {}
        }
        return summary
    
    def _create_technical_analysis_prompt(self, data_summary: Dict, context: Optional[str], language: str = "en") -> str:
        """Create prompt for technical analysis with language specification."""
        
        # Language-specific instructions
        language_instructions = {
            "en": "Please respond in English.",
            "zh-TW": "請用繁體中文回答。",
            "zh-CN": "请用简体中文回答。"
        }
        
        lang_instruction = language_instructions.get(language, language_instructions["en"])
        
        prompt = f"""
        As an expert technical analyst following professional analyst strategies, analyze the following stock data and provide a trading recommendation.
        
        IMPORTANT: {lang_instruction}

        Stock: {data_summary.get('symbol', 'Unknown')}
        Current Price: ${data_summary.get('current_price', 0):.2f}
        1-Day Change: {data_summary.get('price_change_1d', 0):.2f}%
        5-Day Change: {data_summary.get('price_change_5d', 0):.2f}%
        Volume Ratio: {data_summary.get('volume_ratio', 1):.2f}x

        Technical Indicators:
        """
        
        for indicator, value in data_summary.get('indicators', {}).items():
            prompt += f"- {indicator.upper()}: {value:.2f}\n"
        
        prompt += "\nDetected Patterns:\n"
        for pattern_type, count in data_summary.get('patterns', {}).items():
            prompt += f"- {pattern_type.replace('_', ' ').title()}: {count} detected\n"
        
        if context:
            prompt += f"\nAdditional Context: {context}\n"
        
        # Add Analyst Wang's specific strategies
        indicators = data_summary.get('indicators', {})
        current_price = data_summary.get('current_price', 0)
        
        prompt += f"""

        🎯 分析師完整招數 (PROFESSIONAL ANALYST'S COMPLETE TRADING METHODS):
        
        1. 【看均線避免被「雙巴」- 分析師核心策略】:
        {f"   - 當前價格 ${current_price:.2f} vs 20日均線 ${indicators.get('sma_20', 0):.2f}" if 'sma_20' in indicators else ""}
        {"   - 🔍 關鍵檢查: 前高壓力是否轉為支撐？突破是否伴隨大量？"}
        {f"   - 📊 成交量判斷: 當前 {data_summary.get('volume_ratio', 1):.2f}x → {'低基期爆量=極大利多(否極泰來)' if data_summary.get('volume_ratio', 1) > 2 and current_price < indicators.get('sma_20', current_price) * 1.1 else '高基期爆量=兇多吉少' if data_summary.get('volume_ratio', 1) > 2 else '量能正常'}"}
        {"   - 📈 支撐壓力: 成交量大的高點=壓力，低點=支撐"}
        {"   - ⚠️ 套牢成本: 區間內大家套牢在高價位，壓力守不住則後勢堪憂"}
        {"   - 🎯 等幅上漲: 設定停利位置可根據等幅上漲判斷"}
        {"   - 📅 月均線扣抵值: 觀察月均線變化"}

        2. 【RSI進階運用 - 避免鈍化陷阱 (分析師精髓)】:
        {f"   - 當前RSI: {indicators.get('rsi', 'N/A')}" if 'rsi' in indicators else "   - RSI數據不可用"}
        {f"   - ⚡ RSI鈍化診斷: {'RSI已過熱鈍化' if indicators.get('rsi', 50) > 80 else 'RSI已超賣鈍化' if indicators.get('rsi', 50) < 20 else 'RSI正常範圍'}" if 'rsi' in indicators else ""}
        {f"   - 🚨 **分析師關鍵**: RSI鈍化時改看KD指標 ('羅威KD是歸鎳')" if 'rsi' in indicators and (indicators['rsi'] > 80 or indicators['rsi'] < 20) else ""}
        {f"   - 📉 高檔操作: RSI跌破80即賣出，勿等KD死叉！" if 'rsi' in indicators and indicators['rsi'] > 75 else ""}
        {f"   - 📈 低檔操作: RSI慣性跌破20表示過熱，反彈突破20應回補" if 'rsi' in indicators and indicators['rsi'] < 25 else ""}
        {"   - 🔄 RSI背離: 抓取轉折高低點，價格新高但RSI不創新高(頂背離)"}
        {"   - ⚖️ 5日均線配合: RSI鈍化時觀察5日均線，跌破即賣出"}

        3. 【羅威與分析師混搭策略 - 操作節奏】:
        {"   - 🎯 **核心節奏**: 站上10日均線買進，跌破5日均線賣出"}
        {"   - 🔄 均線糾結: 等待'三陽開泰'確認突破(糾結可能持續很久)"}
        {f"   - ✅ 波段訊號: 價格{'已站上' if current_price > indicators.get('sma_20', 0) * 0.98 else '未站上'}10日均線 → {'買進訊號' if current_price > indicators.get('sma_20', 0) * 0.98 else '等待時機'}" if 'sma_20' in indicators else ""}
        {"   - ⚡ 短線操作: 跌破5日均線立即賣出避免套牢 (分析師常用手法)"}
        {"   - 📊 RSI配合: RSI升至80過熱慣性跌破→賣出，等KD上勾(非金叉)再進"}
        {"   - 🔍 綜合工具: 配合趨勢線、區間、月均線扣抵避免被巴來巴去"}
        {"   - 📋 日線判斷: 若日線金叉但未破低=買進訊號；日線金叉+破低=等W底"}

        4. 【均線分級應用 - 分析師心法】:
        {"   - 🚀 噴出行情: 關注5日均線 (短線爆發)"}
        {"   - 📈 波段操作: 觀察10日均線 (中期趨勢)"}
        {"   - ⚡ 短線進出: 以5日均線為主要依據"}
        {"   - 🌅 三陽開泰: 連續三根陽線突破，多頭確立"}
        {"   - 🌃 三聲無奈: 連續三根陰線，空頭來臨"}
        {"   - ✨ 買進條件: 股價站上5、10、20日均線並出現糾結"}

        5. 【三角收斂突破策略 - 分析師招數】:
        {"   - 🟢 紅K突破: 紅K突破或跳空向上 → 趨勢朝上，可追價進場"}
        {"   - 🔴 黑K跌破: 黑K慣性跌破或跳空向下 → 趨勢轉弱，應避開"}
        {"   - 📊 量能確認: 收斂末端注意成交量放大確認突破"}
        {"   - 🎯 進場時機: 三角形突破配合量增為最佳訊號"}

        6. 【分析師風險控管心法】:
        {"   - 🛡️ 多重確認: RSI + 均線 + 成交量 + 型態 (絕不單一指標決策)"}
        {"   - 🎯 停損設定: 依據前波低點或關鍵支撐 (分析師式風控)"}
        {"   - 📊 量價健檢: 價漲量增=健康，價漲量縮=要小心"}
        {"   - ⚠️ 避免套牢: 寧可錯過不可做錯，保持靈活進出"}
        {"   - 🔄 積分概念: 積分多頭、週死叉時的日線操作策略"}

        **分析師策略核心理念**: 「站上均線買，跌破均線賣，配合RSI鈍化看KD，多重確認避免被巴」

        CRITICAL ANALYSIS REQUIREMENTS:
        {lang_instruction} 
        
        請嚴格按照分析師完整招數提供分析，具體說明:
        1. 整體建議 (BUY/SELL/HOLD) - 基於分析師六大策略綜合判斷
        2. 信心水準 (0-1) - 多重確認後的信心度
        3. 關鍵推理 - 明確說明應用了哪些分析師具體招數
        4. 策略因子 - 列出符合的分析師策略要點
        5. 具體買進價位 - 精確計算進場價格 (必須提供數值)
        6. 具體停損價位 - 分析師風險管理原則計算的確切停損價 (必須提供數值)
        7. 目標價位 - 基於等幅上漲或支撐壓力的獲利目標
        8. 風險評估 (0-1) - 綜合分析師多重確認後的風險判斷

        **價位計算方法** (請按照以下邏輯精確計算):
        - 買進價位: 如果BUY→當前價±3%內的支撐位或突破價；如果HOLD→關鍵支撐價位
        - 停損價位: 前波低點或5日均線下緣-2%的保護價位
        - 目標價位: 等幅上漲或下一阻力位，風報比至少1:2

        **必須包含精確數值**: 所有價位都要具體到小數點後2位 (例如: 102.50, 98.75)

        Format as JSON: {{
          "recommendation": "BUY/SELL/HOLD",
          "confidence": 0.XX,
          "reasoning": "詳細推理...",
          "key_factors": ["因子1", "因子2", ...],
          "entry_price": XX.XX,
          "stop_loss": XX.XX, 
          "price_target": XX.XX,
          "risk_score": 0.XX
        }}
        """
        
        return prompt
    
    def _create_chart_analysis_prompt(self, symbol: str, timeframe: str, context: Optional[str]) -> str:
        """Create prompt for chart image analysis."""
        prompt = f"""
        As an expert chart analyst, analyze this {timeframe} chart for {symbol}.

        Look for:
        1. Trend direction and strength
        2. Support and resistance levels
        3. Chart patterns (triangles, flags, head & shoulders, etc.)
        4. Volume patterns
        5. Potential breakout or breakdown signals
        6. Entry and exit points

        {f"Additional context: {context}" if context else ""}

        Provide a trading recommendation with reasoning. Format your response as JSON with keys:
        recommendation, confidence, reasoning, key_factors, price_target, stop_loss, risk_score
        """
        
        return prompt
    
    def _create_sentiment_analysis_prompt(self, sentiment_summary: Dict) -> str:
        """Create prompt for sentiment analysis."""
        prompt = f"""
        As a market sentiment expert, analyze the following information for {sentiment_summary['symbol']}:

        Recent News Headlines:
        """
        
        for headline in sentiment_summary['news_headlines']:
            prompt += f"- {headline}\n"
        
        if sentiment_summary['social_sentiment']:
            prompt += f"\nSocial Sentiment Data: {sentiment_summary['social_sentiment']}\n"
        
        if sentiment_summary['earnings_data']:
            prompt += f"\nEarnings Information: {sentiment_summary['earnings_data']}\n"
        
        prompt += """
        Analyze the overall market sentiment and provide:
        1. Sentiment-based recommendation (BUY/SELL/HOLD)
        2. Confidence level (0-1)
        3. Key sentiment drivers
        4. Risk factors from sentiment perspective

        Format as JSON with keys: recommendation, confidence, reasoning, key_factors, risk_score
        """
        
        return prompt
    
    def _create_strategy_prompt(self, combined_data: Dict) -> str:
        """Create prompt for strategy generation."""
        prompt = f"""
        Create a comprehensive trading strategy for {combined_data['symbol']} based on:

        Technical Analysis:
        - Recommendation: {combined_data['technical']['recommendation']}
        - Confidence: {combined_data['technical']['confidence']:.2f}
        - Reasoning: {combined_data['technical']['reasoning']}

        Sentiment Analysis:
        - Recommendation: {combined_data['sentiment']['recommendation']}
        - Confidence: {combined_data['sentiment']['confidence']:.2f}
        - Reasoning: {combined_data['sentiment']['reasoning']}

        Risk Tolerance: {combined_data['risk_tolerance']}
        Investment Horizon: {combined_data['investment_horizon']}

        Provide a detailed strategy including:
        1. Overall recommendation and rationale
        2. Position sizing recommendation
        3. Entry strategy
        4. Exit strategy
        5. Risk management rules
        6. Timeline and milestones

        Format as JSON with keys: recommendation, position_size, entry_strategy, exit_strategy, risk_management, timeline
        """
        
        return prompt
    
    async def _get_ai_response(self, prompt: str, language: str = "en") -> str:
        """Get response from OpenAI API with language support."""
        try:
            # 簡化系統提示，語言要求已在用戶提示中
            system_prompt = "You are an expert financial analyst and trader. Provide accurate, data-driven analysis."
            
            # Debug logging
            logger.info(f"🔍 AI Analysis Language: {language}")
            logger.info(f"📝 Prompt includes language instruction for: {language}")
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"✅ AI Response received, length: {len(ai_response)} chars")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"❌ Error getting AI response: {str(e)}")
            raise
    
    def _parse_ai_response(self, symbol: str, response: str, analysis_type: str) -> AIAnalysisResult:
        """Parse AI response into structured result."""
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                data = json.loads(response)
            else:
                # Extract JSON from text response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    data = json.loads(json_str)
                else:
                    # Fallback: parse manually
                    data = self._manual_parse_response(response)
            
            # Parse entry price from either 'entry_price' or 'price_target' for backwards compatibility
            entry_price = data.get('entry_price') or data.get('price_target')
            
            return AIAnalysisResult(
                symbol=symbol,
                analysis_type=analysis_type,
                timestamp=datetime.now(),
                confidence=float(data.get('confidence', 0.5)),
                recommendation=data.get('recommendation', 'HOLD').upper(),
                reasoning=data.get('reasoning', 'AI analysis performed'),
                key_factors=data.get('key_factors', []),
                price_target=data.get('price_target'),
                stop_loss=data.get('stop_loss'),
                risk_score=data.get('risk_score'),
                entry_price=entry_price
            )
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return self._create_fallback_analysis(symbol, analysis_type)
    
    def _manual_parse_response(self, response: str) -> Dict:
        """Manually parse response if JSON parsing fails."""
        data = {
            'confidence': 0.5,
            'recommendation': 'HOLD',
            'reasoning': response[:200],  # First 200 chars
            'key_factors': [],
            'risk_score': 0.5
        }
        
        # Extract recommendation
        response_upper = response.upper()
        if 'BUY' in response_upper and 'SELL' not in response_upper:
            data['recommendation'] = 'BUY'
        elif 'SELL' in response_upper:
            data['recommendation'] = 'SELL'
        
        return data
    
    def _parse_strategy_response(self, response: str) -> Dict[str, Any]:
        """Parse strategy response."""
        try:
            if response.strip().startswith('{'):
                return json.loads(response)
            else:
                # Extract JSON from text
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parsing strategy response: {str(e)}")
        
        # Fallback strategy
        return self._create_fallback_strategy("Unknown")
    
    def _create_fallback_analysis(self, symbol: str, analysis_type: str, language: str = "en") -> AIAnalysisResult:
        """Create fallback analysis when AI fails."""
        # Check if this is a demo environment
        is_demo = settings.openai_api_key.startswith('dummy_key') or 'demo' in settings.openai_api_key.lower()
        
        if is_demo:
            # Provide realistic demo analysis with language support
            if language == "zh-TW":
                demo_recommendations = {
                    'AAPL': {'rec': 'BUY', 'conf': 0.75, 'reasoning': '強勁的技術動量，RSI顯示超賣狀況。看漲形態正在形成。'},
                    'TSLA': {'rec': 'HOLD', 'conf': 0.65, 'reasoning': '混合信號 - 高波動性但基本面成長前景強勁。'},
                    'GOOGL': {'rec': 'BUY', 'conf': 0.70, 'reasoning': '基本面穩健，在AI領域有強勢定位，未來成長可期。'},
                    'MSFT': {'rec': 'BUY', 'conf': 0.80, 'reasoning': '雲端運算市場領導者，營收持續穩定成長。'},
                    '2330.TW': {'rec': 'BUY', 'conf': 0.72, 'reasoning': '領先的半導體製造商，全球需求強勁。'}
                }
            elif language == "zh-CN":
                demo_recommendations = {
                    'AAPL': {'rec': 'BUY', 'conf': 0.75, 'reasoning': '强劲的技术动量，RSI显示超卖状况。看涨形态正在形成。'},
                    'TSLA': {'rec': 'HOLD', 'conf': 0.65, 'reasoning': '混合信号 - 高波动性但基本面增长前景强劲。'},
                    'GOOGL': {'rec': 'BUY', 'conf': 0.70, 'reasoning': '基本面稳健，在AI领域有强势定位，未来增长可期。'},
                    'MSFT': {'rec': 'BUY', 'conf': 0.80, 'reasoning': '云计算市场领导者，营收持续稳定增长。'},
                    '2330.TW': {'rec': 'BUY', 'conf': 0.72, 'reasoning': '领先的半导体制造商，全球需求强劲。'}
                }
            else:
                demo_recommendations = {
                    'AAPL': {'rec': 'BUY', 'conf': 0.75, 'reasoning': 'Strong technical momentum with RSI showing oversold conditions. Bullish patterns emerging.'},
                    'TSLA': {'rec': 'HOLD', 'conf': 0.65, 'reasoning': 'Mixed signals - high volatility but strong fundamental growth prospects.'},
                    'GOOGL': {'rec': 'BUY', 'conf': 0.70, 'reasoning': 'Solid fundamentals with strong AI positioning for future growth.'},
                    'MSFT': {'rec': 'BUY', 'conf': 0.80, 'reasoning': 'Market leader in cloud computing with consistent revenue growth.'},
                    '2330.TW': {'rec': 'BUY', 'conf': 0.72, 'reasoning': 'Leading semiconductor manufacturer with strong global demand.'}
                }
            
            demo_data = demo_recommendations.get(symbol, {'rec': 'HOLD', 'conf': 0.60, 'reasoning': 'Awaiting stronger market signals for clear direction.'})
            
            return AIAnalysisResult(
                symbol=symbol,
                analysis_type=analysis_type,
                timestamp=datetime.now(),
                confidence=demo_data['conf'],
                recommendation=demo_data['rec'],
                reasoning=f"📊 DEMO MODE: {demo_data['reasoning']} (Set real OpenAI API Key for live AI analysis)",
                key_factors=[
                    'Technical analysis based on current market data',
                    'Pattern recognition algorithms active',
                    'Real-time data integration working',
                    'AI recommendations pending real API key'
                ],
                risk_score=0.4 if demo_data['rec'] == 'BUY' else 0.6,
                price_target=None,
                stop_loss=None,
                entry_price=None
            )
        else:
            # Original fallback for real API key failures with language support
            if language == "zh-TW":
                reasoning = '無法完成AI分析，請檢查您的OpenAI API密鑰配置。'
                key_factors = ['AI分析失敗 - API密鑰問題']
            elif language == "zh-CN":
                reasoning = '无法完成AI分析，请检查您的OpenAI API密钥配置。'
                key_factors = ['AI分析失败 - API密钥问题']
            else:
                reasoning = 'Unable to complete AI analysis. Please check your OpenAI API key configuration.'
                key_factors = ['AI analysis failed - API key issue']
                
            return AIAnalysisResult(
                symbol=symbol,
                analysis_type=analysis_type,
                timestamp=datetime.now(),
                confidence=0.3,
                recommendation='HOLD',
                reasoning=reasoning,
                key_factors=key_factors,
                risk_score=0.5,
                entry_price=None
            )
    
    def _create_fallback_strategy(self, symbol: str) -> Dict[str, Any]:
        """Create fallback strategy when AI fails."""
        return {
            'recommendation': 'HOLD',
            'position_size': 0.05,  # 5% of portfolio
            'entry_strategy': 'Wait for clearer signals',
            'exit_strategy': 'Review in 1 week',
            'risk_management': 'Use 2% stop loss',
            'timeline': '1-2 weeks for reassessment'
        }
    
    def create_chart_image(self, data: pd.DataFrame, symbol: str) -> Optional[bytes]:
        """
        Create a chart image for AI analysis.
        
        Args:
            data: OHLCV DataFrame
            symbol: Stock symbol
            
        Returns:
            Chart image as bytes or None if plotting not available
        """
        if not PLOTTING_AVAILABLE or data.empty:
            return None
        
        try:
            # Create candlestick chart
            fig, axes = mpf.plot(
                data.tail(50),  # Last 50 periods
                type='candle',
                style='charles',
                title=f'{symbol} - Stock Chart',
                ylabel='Price ($)',
                volume=True,
                returnfig=True,
                figsize=(12, 8)
            )
            
            # Save to bytes
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            chart_bytes = buffer.getvalue()
            buffer.close()
            
            return chart_bytes
            
        except Exception as e:
            logger.error(f"Error creating chart image: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_ai_analyzer():
        # Note: Requires valid OpenAI API key
        try:
            analyzer = OpenAIAnalyzer()
            
            # Create sample data
            dates = pd.date_range('2023-01-01', periods=50, freq='D')
            np.random.seed(42)
            
            close_prices = 100 + np.cumsum(np.random.randn(50) * 0.5)
            sample_data = pd.DataFrame({
                'open': close_prices + np.random.randn(50) * 0.3,
                'high': close_prices + np.random.rand(50) * 2,
                'low': close_prices - np.random.rand(50) * 2,
                'close': close_prices,
                'volume': np.random.randint(1000000, 5000000, 50)
            }, index=dates)
            
            # Mock indicators and patterns
            indicators = {'rsi': 65, 'macd': 0.5}
            patterns = {'breakouts': [], 'triangles': []}
            
            # Test technical analysis
            result = await analyzer.analyze_technical_data(
                'AAPL', sample_data, indicators, patterns
            )
            
            print(f"AI Analysis Result:")
            print(f"Recommendation: {result.recommendation}")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Reasoning: {result.reasoning}")
            
        except Exception as e:
            print(f"Test failed: {str(e)}")
    
    # Run test
    # asyncio.run(test_ai_analyzer())