"""
使用次數追蹤系統

提供AI功能使用次數的自動追蹤和配額管理
"""

from functools import wraps
from typing import Optional, Callable, Any
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from src.database.connection import get_db_session
from src.database.models import User
from .auth import get_current_user, get_optional_user
from .schemas import UsageRecordCreate, ActionType
from . import crud

logger = logging.getLogger(__name__)

class UsageTracker:
    """使用次數追蹤器"""
    
    def __init__(self):
        self.action_types = {
            "ai_analysis": ActionType.ai_analysis,
            "chart_view": ActionType.chart_view,
            "strategy_discussion": ActionType.ai_analysis,  # 策略討論也算作AI分析
            "backtest_optimization": ActionType.ai_analysis,  # 回測優化也算作AI分析
            "ai_question": ActionType.ai_analysis  # AI問答也算作AI分析
        }
    
    def track_usage(
        self, 
        action_type: str = "ai_analysis",
        required_login: bool = True,
        consume_quota: bool = True
    ):
        """
        使用次數追蹤裝飾器
        
        Args:
            action_type: 動作類型 ("ai_analysis", "chart_view", "strategy_discussion", 等)
            required_login: 是否需要登入
            consume_quota: 是否消耗配額
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 提取依賴注入的參數
                db = None
                current_user = None
                
                # 從kwargs中查找數據庫會話和用戶
                for key, value in kwargs.items():
                    if isinstance(value, Session):
                        db = value
                    elif hasattr(value, 'id') and hasattr(value, 'email'):
                        current_user = value
                
                # 如果沒有找到db，嘗試創建
                if not db:
                    from src.database.connection import get_db_session
                    db_gen = get_db_session()
                    db = next(db_gen)
                    try:
                        result = await self._track_and_execute(
                            func, args, kwargs, db, current_user, 
                            action_type, required_login, consume_quota
                        )
                        return result
                    finally:
                        try:
                            db.close()
                        except:
                            pass
                else:
                    return await self._track_and_execute(
                        func, args, kwargs, db, current_user, 
                        action_type, required_login, consume_quota
                    )
            
            return wrapper
        return decorator
    
    async def _track_and_execute(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        db: Session,
        current_user: Optional[User],
        action_type: str,
        required_login: bool,
        consume_quota: bool
    ):
        """執行追蹤邏輯並調用原函數"""
        
        # 檢查登入要求
        if required_login and not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="此功能需要登入"
            )
        
        # 如果需要消耗配額且用戶已登入，檢查配額
        if consume_quota and current_user:
            can_use = crud.check_user_can_use_ai(db, current_user.id)
            if not can_use:
                quota = crud.get_user_quota(db, current_user.id)
                subscription = crud.get_user_active_subscription(db, current_user.id)
                
                error_detail = "您的免費AI分析次數已用完。"
                if quota:
                    if quota.remaining_initial_quota > 0:
                        error_detail += f"剩餘新用戶配額：{quota.remaining_initial_quota}次，"
                    if quota.remaining_daily_quota > 0:
                        error_detail += f"今日剩餘配額：{quota.remaining_daily_quota}次。"
                    else:
                        error_detail += "請明天再試或升級為付費用戶以獲得無限使用。"
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=error_detail,
                    headers={"X-RateLimit-Type": "quota"}
                )
        
        # 執行原函數
        try:
            # 記錄開始時間
            start_time = datetime.utcnow()
            
            result = await func(*args, **kwargs)
            
            # 記錄結束時間
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # 函數執行成功後記錄使用情況
            if current_user:
                # 消耗配額
                if consume_quota and action_type in ["ai_analysis", "strategy_discussion", "backtest_optimization", "ai_question"]:
                    quota_consumed = crud.consume_user_quota(db, current_user.id)
                    logger.info(f"User {current_user.id} quota consumed: {quota_consumed}")
                
                # 記錄使用記錄
                self._record_usage(
                    db, current_user.id, action_type, 
                    {"duration": duration, "success": True}
                )
            
            return result
            
        except Exception as e:
            # 函數執行失敗，記錄錯誤但不消耗配額
            if current_user:
                self._record_usage(
                    db, current_user.id, action_type,
                    {"success": False, "error": str(e)[:200]}
                )
            raise e
    
    def _record_usage(
        self, 
        db: Session, 
        user_id: str, 
        action_type: str, 
        extra_data: dict = None
    ):
        """記錄使用情況"""
        try:
            mapped_action_type = self.action_types.get(action_type, ActionType.ai_analysis)
            usage_record = UsageRecordCreate(
                action_type=mapped_action_type,
                extra_data=extra_data or {}
            )
            crud.create_usage_record(db, user_id, usage_record)
            logger.debug(f"Usage recorded: user={user_id}, action={action_type}")
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")

# 全局追蹤器實例
usage_tracker = UsageTracker()

# 便捷的裝飾器函數
def track_ai_usage(required_login: bool = True):
    """追蹤AI分析使用次數的裝飾器"""
    return usage_tracker.track_usage("ai_analysis", required_login, consume_quota=True)

def track_chart_usage(required_login: bool = False):
    """追蹤圖表查看使用次數的裝飾器（不消耗配額）"""
    return usage_tracker.track_usage("chart_view", required_login, consume_quota=False)

def track_strategy_usage(required_login: bool = True):
    """追蹤策略討論使用次數的裝飾器"""
    return usage_tracker.track_usage("strategy_discussion", required_login, consume_quota=True)

def track_backtest_usage(required_login: bool = True):
    """追蹤回測優化使用次數的裝飾器"""
    return usage_tracker.track_usage("backtest_optimization", required_login, consume_quota=True)

def track_ai_question_usage(required_login: bool = True):
    """追蹤AI問答使用次數的裝飾器"""
    return usage_tracker.track_usage("ai_question", required_login, consume_quota=True)

# 手動使用記錄函數
async def record_manual_usage(
    db: Session,
    user_id: str,
    action_type: str,
    success: bool = True,
    extra_data: dict = None
):
    """手動記錄使用情況（用於無法使用裝飾器的場景）"""
    try:
        mapped_action_type = usage_tracker.action_types.get(action_type, ActionType.ai_analysis)
        usage_data = extra_data or {}
        usage_data["success"] = success
        
        usage_record = UsageRecordCreate(
            action_type=mapped_action_type,
            extra_data=usage_data
        )
        crud.create_usage_record(db, user_id, usage_record)
        logger.debug(f"Manual usage recorded: user={user_id}, action={action_type}")
    except Exception as e:
        logger.error(f"Failed to record manual usage: {e}")

# 配額檢查函數
async def check_quota_before_use(user: User, db: Session, action_type: str = "ai_analysis"):
    """
    在使用AI功能前檢查配額
    
    Returns:
        tuple: (can_use: bool, quota_info: dict)
    """
    try:
        # 檢查是否可以使用
        can_use = crud.check_user_can_use_ai(db, user.id)
        
        # 獲取配額信息
        quota = crud.get_user_quota(db, user.id)
        subscription = crud.get_user_active_subscription(db, user.id)
        
        quota_info = {
            "can_use": can_use,
            "is_premium": subscription and subscription.is_premium if subscription else False,
            "remaining_initial_quota": quota.remaining_initial_quota if quota else 0,
            "remaining_daily_quota": quota.remaining_daily_quota if quota else 0,
            "used_today": quota.daily_used_count if quota else 0,
            "total_used": quota.used_free_uses if quota else 0
        }
        
        return can_use, quota_info
        
    except Exception as e:
        logger.error(f"Error checking quota: {e}")
        return False, {"error": str(e)}

# 批量操作函數
async def get_user_usage_summary(user_id: str, db: Session, days: int = 30):
    """獲取用戶使用情況摘要"""
    try:
        # 獲取基本統計
        stats = crud.get_user_usage_stats(db, user_id)
        
        # 獲取近期記錄
        recent_records = crud.get_user_usage_records(db, user_id, limit=days * 5)
        
        # 計算使用趨勢
        ai_usage_trend = []
        chart_usage_trend = []
        
        for record in recent_records:
            date_str = record.created_at.strftime("%Y-%m-%d")
            if record.action_type == "ai_analysis":
                ai_usage_trend.append({"date": date_str, "count": 1})
            elif record.action_type == "chart_view":
                chart_usage_trend.append({"date": date_str, "count": 1})
        
        return {
            "basic_stats": stats,
            "recent_records_count": len(recent_records),
            "ai_usage_trend": ai_usage_trend[:7],  # 最近7天
            "chart_usage_trend": chart_usage_trend[:7]
        }
        
    except Exception as e:
        logger.error(f"Error getting usage summary: {e}")
        return {"error": str(e)}

# 導出主要函數和類
__all__ = [
    "UsageTracker",
    "usage_tracker",
    "track_ai_usage",
    "track_chart_usage", 
    "track_strategy_usage",
    "track_backtest_usage",
    "track_ai_question_usage",
    "record_manual_usage",
    "check_quota_before_use",
    "get_user_usage_summary"
]