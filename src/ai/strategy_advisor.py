#!/usr/bin/env python3
"""
OpenAI驅動的股票策略顧問聊天室
提供智能的買進策略討論和分析建議
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import openai
from openai import OpenAI
from config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """聊天訊息"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    message_id: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class StrategyContext:
    """策略分析上下文"""
    symbol: str
    current_price: float
    pattern_signals: List[Dict[str, Any]]
    technical_indicators: Dict[str, Any]
    market_context: Dict[str, Any]
    recent_news: Optional[List[str]] = None

class StrategyAdvisor:
    """AI策略顧問 - 支援智能模型切換"""
    
    def __init__(self, api_key: Optional[str] = None, model_preference: Optional[str] = None):
        """
        初始化AI策略顧問
        
        Args:
            api_key: OpenAI API密鑰，如果未提供則從環境變量獲取
            model_preference: 模型偏好 ('basic', 'advanced', 'vision', None為自動選擇)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or settings.openai_api_key
        if not self.api_key:
            logger.warning("OpenAI API key not found. AI features will be disabled.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"OpenAI client initialization failed: {e}")
                self.client = None
        
        # 模型配置
        self.model_preference = model_preference
        self.models = {
            'basic': settings.ai_model_basic,
            'advanced': settings.ai_model_advanced, 
            'vision': settings.ai_model_vision
        }
        
        self.conversation_history: List[ChatMessage] = []
        self.system_prompt = self._create_system_prompt()
        
        logger.info(f"StrategyAdvisor initialized with models: {self.models}")
    
    def get_model_for_task(self, task_type: str = 'chat') -> str:
        """
        根據任務類型獲取最適合的模型
        
        Args:
            task_type: 任務類型 ('chat', 'backtest', 'analysis', 'vision')
            
        Returns:
            模型名稱
        """
        # 如果設定了固定偏好，使用該模型
        if self.model_preference and self.model_preference in self.models:
            return self.models[self.model_preference]
        
        # 如果關閉自動選擇，使用基礎模型
        if not settings.ai_auto_model_selection:
            return self.models['basic']
        
        # 根據任務自動選擇模型
        task_model_map = {
            'chat': 'basic',           # 一般對話使用基礎模型
            'backtest': 'advanced',    # 回測分析使用高級模型
            'analysis': 'advanced',    # 複雜分析使用高級模型
            'strategy': 'advanced',    # 策略規劃使用高級模型
            'vision': 'vision',        # 圖表分析使用視覺模型
            'optimization': 'advanced' # 優化建議使用高級模型
        }
        
        model_type = task_model_map.get(task_type, 'basic')
        selected_model = self.models[model_type]
        
        logger.info(f"Auto-selected model '{selected_model}' for task type '{task_type}'")
        return selected_model
    
    def set_model_preference(self, preference: str) -> bool:
        """
        設定模型偏好
        
        Args:
            preference: 模型偏好 ('basic', 'advanced', 'vision', 'auto')
            
        Returns:
            是否設定成功
        """
        if preference == 'auto':
            self.model_preference = None
            logger.info("Model preference set to auto-selection")
            return True
        elif preference in self.models:
            self.model_preference = preference
            logger.info(f"Model preference set to {preference} ({self.models[preference]})")
            return True
        else:
            logger.warning(f"Invalid model preference: {preference}")
            return False
        
    def _create_system_prompt(self) -> str:
        """創建系統提示詞"""
        return """你是一位專業的股票技術分析師和投資策略顧問。你的專長包括：

🎯 **核心能力**：
- 技術分析：形態識別（箱型、楔型、三角形、旗型等）
- 買進時機分析：風險評估、進場點位、停損設定
- 策略規劃：短期交易、中長期投資建議
- 回測分析：歷史績效評估、策略優化建議

📊 **分析方法**：
- 綜合技術指標（RSI、MACD、移動平均等）
- 形態學分析（突破、整理、反轉形態）
- 成交量分析與確認訊號
- 風險報酬比評估

💡 **回答風格**：
- 提供具體的數據支撐和邏輯分析
- 給出明確的買進建議：價位、停損、目標
- 分析不同時間週期的策略選擇
- 評估當前市場環境對策略的影響

⚠️ **風險提示**：
- 始終提醒投資風險，強調資金管理
- 不提供保證獲利的承諾
- 建議分散投資，設定合理停損

請根據用戶提供的技術分析數據，給出專業、實用的投資建議。"""

    def start_conversation(self, context: StrategyContext) -> ChatMessage:
        """
        開始策略討論對話
        
        Args:
            context: 股票分析上下文
            
        Returns:
            AI的開場分析訊息
        """
        try:
            if not self.client:
                return self._create_fallback_message("AI服務目前不可用，請檢查API設定")
            
            # 重置對話歷史
            self.conversation_history = []
            
            # 創建上下文分析
            context_analysis = self._create_context_analysis(context)
            
            # 生成開場分析 - 使用高級模型進行策略分析
            response = self._call_openai([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"請分析以下股票數據並提供策略建議：\n\n{context_analysis}"}
            ], task_type='strategy')
            
            assistant_message = ChatMessage(
                role="assistant",
                content=response,
                timestamp=datetime.now(),
                message_id=self._generate_message_id(),
                metadata={"context": asdict(context)}
            )
            
            self.conversation_history.append(assistant_message)
            return assistant_message
            
        except Exception as e:
            logger.error(f"開始對話錯誤: {e}")
            return self._create_fallback_message(f"AI分析出錯: {str(e)}")
    
    def chat(self, user_message: str, context: Optional[StrategyContext] = None) -> ChatMessage:
        """
        處理用戶聊天訊息
        
        Args:
            user_message: 用戶訊息
            context: 可選的更新上下文
            
        Returns:
            AI回應訊息
        """
        try:
            if not self.client:
                return self._create_fallback_message("AI服務目前不可用")
            
            # 添加用戶訊息到歷史
            user_msg = ChatMessage(
                role="user",
                content=user_message,
                timestamp=datetime.now(),
                message_id=self._generate_message_id()
            )
            self.conversation_history.append(user_msg)
            
            # 構建對話歷史
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # 添加上下文（如果有新的）
            if context:
                context_info = self._create_context_analysis(context)
                messages.append({
                    "role": "system", 
                    "content": f"當前股票分析數據更新：\n{context_info}"
                })
            
            # 添加最近的對話歷史（最多10條）
            recent_history = self.conversation_history[-10:]
            for msg in recent_history:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # 獲取AI回應 - 一般對話使用基礎模型
            response = self._call_openai(messages, task_type='chat')
            
            assistant_message = ChatMessage(
                role="assistant",
                content=response,
                timestamp=datetime.now(),
                message_id=self._generate_message_id(),
                metadata={"user_question": user_message}
            )
            
            self.conversation_history.append(assistant_message)
            return assistant_message
            
        except Exception as e:
            logger.error(f"聊天處理錯誤: {e}")
            return self._create_fallback_message(f"AI回應出錯: {str(e)}")
    
    def analyze_strategy(self, strategy_request: str, context: StrategyContext) -> ChatMessage:
        """
        專門的策略分析
        
        Args:
            strategy_request: 策略分析請求
            context: 分析上下文
            
        Returns:
            策略分析結果
        """
        try:
            if not self.client:
                return self._create_fallback_message("AI策略分析服務不可用")
            
            # 創建專門的策略分析提示
            strategy_prompt = f"""
基於以下數據進行深度策略分析：

{self._create_context_analysis(context)}

用戶請求：{strategy_request}

請提供：
1. 🎯 **買進建議**：具體進場價位、理由
2. 🛡️ **風險管理**：停損點設定、資金配置
3. 📈 **目標設定**：短期/中期目標價、預期報酬
4. ⏰ **時機分析**：最佳進場時機判斷
5. 📊 **替代策略**：如果當前不適合，提供其他選擇
6. 🔄 **後續追蹤**：需要關注的關鍵指標

請提供具體、可執行的建議。
"""
            
            # 策略分析使用高級模型，獲得更精確的建議
            response = self._call_openai([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": strategy_prompt}
            ], task_type='strategy')
            
            return ChatMessage(
                role="assistant",
                content=response,
                timestamp=datetime.now(),
                message_id=self._generate_message_id(),
                metadata={
                    "analysis_type": "strategy_analysis",
                    "context": asdict(context),
                    "request": strategy_request
                }
            )
            
        except Exception as e:
            logger.error(f"策略分析錯誤: {e}")
            return self._create_fallback_message(f"策略分析出錯: {str(e)}")
    
    def analyze_backtest_results(self, backtest_data: Dict[str, Any]) -> ChatMessage:
        """
        分析回測結果
        
        Args:
            backtest_data: 回測結果數據
            
        Returns:
            回測分析結果
        """
        try:
            if not self.client:
                return self._create_fallback_message("AI回測分析服務不可用")
            
            backtest_summary = self._format_backtest_data(backtest_data)
            
            analysis_prompt = f"""
請分析以下回測結果並提供策略優化建議：

{backtest_summary}

請從以下角度進行分析：

1. 📈 **績效評估**：
   - 總報酬率表現如何？
   - 夏普比率是否合理？
   - 最大回撤是否可接受？

2. 🎯 **策略效果**：
   - 哪些市場環境下表現最好？
   - 勝率和平均獲利的平衡如何？
   - 風險調整後報酬是否理想？

3. 🔧 **優化建議**：
   - 參數調整建議
   - 進出場條件優化
   - 資金管理改善

4. ⚠️ **風險提醒**：
   - 主要風險點識別
   - 市場環境適應性
   - 實際交易注意事項

5. 📊 **策略改進**：
   - 具體的改進方向
   - 可能的組合策略
   - 下一步測試建議

請提供專業、實用的分析意見。
"""
            
            # 回測分析使用高級模型，確保分析品質和準確性
            response = self._call_openai([
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": analysis_prompt}
            ], task_type='backtest')
            
            return ChatMessage(
                role="assistant",
                content=response,
                timestamp=datetime.now(),
                message_id=self._generate_message_id(),
                metadata={
                    "analysis_type": "backtest_analysis",
                    "backtest_data": backtest_data
                }
            )
            
        except Exception as e:
            logger.error(f"回測分析錯誤: {e}")
            return self._create_fallback_message(f"回測分析出錯: {str(e)}")
    
    def _create_context_analysis(self, context: StrategyContext) -> str:
        """創建上下文分析文本"""
        try:
            analysis_parts = [
                f"📊 **股票代號**: {context.symbol}",
                f"💰 **當前價格**: ${context.current_price:.2f}",
                ""
            ]
            
            # 形態訊號分析
            if context.pattern_signals:
                analysis_parts.append("🔍 **技術形態訊號**:")
                for signal in context.pattern_signals[:3]:  # 最多顯示3個訊號
                    pattern_type = signal.get('pattern_type', '未知')
                    confidence = signal.get('confidence', 0)
                    description = signal.get('description', '')
                    target = signal.get('target_price', 0)
                    stop_loss = signal.get('stop_loss', 0)
                    
                    analysis_parts.append(f"- {description} (信心度: {confidence}%)")
                    analysis_parts.append(f"  目標價: ${target:.2f}, 停損: ${stop_loss:.2f}")
                analysis_parts.append("")
            
            # 技術指標分析
            if context.technical_indicators:
                analysis_parts.append("📈 **技術指標**:")
                
                # RSI分析
                if 'rsi' in context.technical_indicators:
                    rsi_data = context.technical_indicators['rsi']
                    analysis_parts.append(f"- RSI: {rsi_data.get('value', 'N/A')} ({rsi_data.get('signal', '中性')})")
                
                # 移動平均分析
                if 'moving_average' in context.technical_indicators:
                    ma_data = context.technical_indicators['moving_average']
                    analysis_parts.append(f"- 移動平均: MA20=${ma_data.get('ma20', 0):.2f}, MA50=${ma_data.get('ma50', 0):.2f} ({ma_data.get('signal', '中性')})")
                
                # 成交量分析
                if 'volume' in context.technical_indicators:
                    vol_data = context.technical_indicators['volume']
                    analysis_parts.append(f"- 成交量: {vol_data.get('signal', '正常')} (近期均量: {vol_data.get('recent_avg', 0):,})")
                
                # 價格趨勢
                if 'price_trend' in context.technical_indicators:
                    trend_data = context.technical_indicators['price_trend']
                    short_term = trend_data.get('short_term', {})
                    medium_term = trend_data.get('medium_term', {})
                    analysis_parts.append(f"- 短期趨勢: {short_term.get('direction', '持平')} ({short_term.get('change_pct', 0)}%)")
                    analysis_parts.append(f"- 中期趨勢: {medium_term.get('direction', '持平')} ({medium_term.get('change_pct', 0)}%)")
                
                analysis_parts.append("")
            
            # 市場環境
            if context.market_context:
                analysis_parts.append("🌍 **市場環境**:")
                for key, value in context.market_context.items():
                    analysis_parts.append(f"- {key}: {value}")
                analysis_parts.append("")
            
            # 相關新聞
            if context.recent_news:
                analysis_parts.append("📰 **相關新聞**:")
                for news in context.recent_news[:3]:
                    analysis_parts.append(f"- {news}")
                analysis_parts.append("")
            
            return "\n".join(analysis_parts)
            
        except Exception as e:
            logger.error(f"創建上下文分析錯誤: {e}")
            return f"上下文分析數據: {context.symbol} - ${context.current_price:.2f}"
    
    def _format_backtest_data(self, backtest_data: Dict[str, Any]) -> str:
        """格式化回測數據"""
        try:
            formatted_parts = ["📊 **回測結果摘要**:", ""]
            
            # 基本績效指標
            total_return = backtest_data.get('total_return', 0)
            annual_return = backtest_data.get('annual_return', 0)
            max_drawdown = backtest_data.get('max_drawdown', 0)
            sharpe_ratio = backtest_data.get('sharpe_ratio', 0)
            win_rate = backtest_data.get('win_rate', 0)
            
            formatted_parts.extend([
                f"💰 **總報酬率**: {total_return:.2%}",
                f"📈 **年化報酬率**: {annual_return:.2%}",
                f"📉 **最大回撤**: {max_drawdown:.2%}",
                f"⚖️ **夏普比率**: {sharpe_ratio:.2f}",
                f"🎯 **勝率**: {win_rate:.1%}",
                ""
            ])
            
            # 交易統計
            total_trades = backtest_data.get('total_trades', 0)
            avg_trade = backtest_data.get('avg_trade_return', 0)
            
            formatted_parts.extend([
                f"🔄 **總交易次數**: {total_trades}",
                f"📊 **平均單次報酬**: {avg_trade:.2%}",
                ""
            ])
            
            # 時間區間
            start_date = backtest_data.get('start_date', 'N/A')
            end_date = backtest_data.get('end_date', 'N/A')
            
            formatted_parts.extend([
                f"📅 **回測區間**: {start_date} 至 {end_date}",
                ""
            ])
            
            # 策略參數
            if 'strategy_params' in backtest_data:
                formatted_parts.append("⚙️ **策略參數**:")
                for key, value in backtest_data['strategy_params'].items():
                    formatted_parts.append(f"- {key}: {value}")
                formatted_parts.append("")
            
            return "\n".join(formatted_parts)
            
        except Exception as e:
            logger.error(f"格式化回測數據錯誤: {e}")
            return f"回測數據: {json.dumps(backtest_data, indent=2, ensure_ascii=False)}"
    
    def _call_openai(self, messages: List[Dict[str, str]], task_type: str = 'chat') -> str:
        """
        調用OpenAI API - 支援智能模型選擇
        
        Args:
            messages: 對話訊息列表
            task_type: 任務類型，用於選擇最適合的模型
            
        Returns:
            AI回應內容
        """
        try:
            # 根據任務類型選擇最適合的模型
            selected_model = self.get_model_for_task(task_type)
            
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=messages,
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            logger.info(f"OpenAI API call successful using model: {selected_model}")
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API調用錯誤 (model: {selected_model}): {e}")
            raise
    
    def _create_fallback_message(self, content: str) -> ChatMessage:
        """創建備用訊息"""
        return ChatMessage(
            role="assistant",
            content=f"⚠️ {content}\n\n📝 **備用建議**: 請根據技術分析數據自行判斷，或稍後重試AI分析功能。",
            timestamp=datetime.now(),
            message_id=self._generate_message_id(),
            metadata={"fallback": True}
        )
    
    def _generate_message_id(self) -> str:
        """生成訊息ID"""
        return f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.now()) % 10000:04d}"
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """獲取對話歷史"""
        return [asdict(msg) for msg in self.conversation_history]
    
    def clear_conversation(self):
        """清除對話歷史"""
        self.conversation_history = []
        logger.info("對話歷史已清除")
    
    def export_conversation(self) -> Dict[str, Any]:
        """導出對話內容"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_messages": len(self.conversation_history),
            "conversation": self.get_conversation_history()
        }

class StrategyChat:
    """策略聊天室管理器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.advisor = StrategyAdvisor(api_key)
        self.active_sessions: Dict[str, StrategyAdvisor] = {}
    
    def create_session(self, session_id: str, context: StrategyContext) -> ChatMessage:
        """創建新的聊天會話"""
        try:
            advisor = StrategyAdvisor(self.advisor.api_key)
            welcome_message = advisor.start_conversation(context)
            self.active_sessions[session_id] = advisor
            
            logger.info(f"創建聊天會話: {session_id}")
            return welcome_message
            
        except Exception as e:
            logger.error(f"創建會話錯誤: {e}")
            return self.advisor._create_fallback_message(f"會話創建失敗: {str(e)}")
    
    def send_message(self, session_id: str, message: str, context: Optional[StrategyContext] = None) -> ChatMessage:
        """發送訊息到指定會話"""
        try:
            if session_id not in self.active_sessions:
                return self.advisor._create_fallback_message("會話不存在，請重新開始對話")
            
            advisor = self.active_sessions[session_id]
            return advisor.chat(message, context)
            
        except Exception as e:
            logger.error(f"發送訊息錯誤: {e}")
            return self.advisor._create_fallback_message(f"訊息處理失敗: {str(e)}")
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """獲取會話歷史"""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id].get_conversation_history()
        return []
    
    def close_session(self, session_id: str):
        """關閉會話"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"關閉聊天會話: {session_id}")

# 確保環境變量已加載
from dotenv import load_dotenv
load_dotenv()

# 全局實例
strategy_chat = StrategyChat()

def get_strategy_chat() -> StrategyChat:
    """獲取策略聊天實例"""
    return strategy_chat