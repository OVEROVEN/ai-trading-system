"""
API配額管理系統
===============

這個模組實現了完整的用戶API配額管理，包括：
- 速率限制 (Rate Limiting)
- 配額檢查和扣除
- 使用量追蹤
- 成本計算
- 多層級計費策略

作者: Claude Code AI Assistant
日期: 2024
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
from functools import wraps

import aioredis
from sqlalchemy.orm import Session
from fastapi import HTTPException, Request, Depends
from pydantic import BaseModel

# ================================
# 數據模型和枚舉
# ================================

class PlanType(str, Enum):
    """用戶計劃類型"""
    FREE = "free"
    BASIC = "basic" 
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class QuotaType(str, Enum):
    """配額類型"""
    API_CALLS = "api_calls"
    AI_ANALYSIS = "ai_analysis"
    BACKTEST_RUNS = "backtest_runs"
    DATA_EXPORT = "data_export"
    CONCURRENT_REQUESTS = "concurrent_requests"

class AIModel(str, Enum):
    """AI模型類型"""
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    CLAUDE_HAIKU = "claude-3-haiku"
    CLAUDE_SONNET = "claude-3-sonnet"

@dataclass
class ModelCosts:
    """AI模型成本配置"""
    input_cost_per_1k: Decimal  # 每1000個input token的成本
    output_cost_per_1k: Decimal  # 每1000個output token的成本
    speed_tier: str  # fast, medium, slow
    
# AI模型成本表（美元/1000 tokens）
MODEL_COSTS = {
    AIModel.GPT_3_5_TURBO: ModelCosts(
        input_cost_per_1k=Decimal("0.0005"),
        output_cost_per_1k=Decimal("0.0015"),
        speed_tier="fast"
    ),
    AIModel.GPT_4O_MINI: ModelCosts(
        input_cost_per_1k=Decimal("0.00015"),
        output_cost_per_1k=Decimal("0.0006"),
        speed_tier="fast"
    ),
    AIModel.GPT_4O: ModelCosts(
        input_cost_per_1k=Decimal("0.005"),
        output_cost_per_1k=Decimal("0.015"),
        speed_tier="medium"
    )
}

@dataclass
class PlanLimits:
    """計劃限制配置"""
    monthly_api_calls: int
    daily_api_calls: int
    hourly_api_calls: int
    minute_api_calls: int
    concurrent_requests: int
    can_use_advanced_ai: bool
    can_use_vision_ai: bool
    can_export_data: bool
    backtest_runs_per_month: int
    max_symbols_per_request: int
    priority_queue: bool

# 計劃限制配置
PLAN_LIMITS = {
    PlanType.FREE: PlanLimits(
        monthly_api_calls=3,
        daily_api_calls=3, 
        hourly_api_calls=3,
        minute_api_calls=1,
        concurrent_requests=1,
        can_use_advanced_ai=False,
        can_use_vision_ai=False,
        can_export_data=False,
        backtest_runs_per_month=1,
        max_symbols_per_request=1,
        priority_queue=False
    ),
    PlanType.BASIC: PlanLimits(
        monthly_api_calls=100,
        daily_api_calls=10,
        hourly_api_calls=5,
        minute_api_calls=2,
        concurrent_requests=3,
        can_use_advanced_ai=False,
        can_use_vision_ai=False,
        can_export_data=True,
        backtest_runs_per_month=50,
        max_symbols_per_request=5,
        priority_queue=False
    ),
    PlanType.PREMIUM: PlanLimits(
        monthly_api_calls=500,
        daily_api_calls=50,
        hourly_api_calls=25,
        minute_api_calls=5,
        concurrent_requests=10,
        can_use_advanced_ai=True,
        can_use_vision_ai=False,
        can_export_data=True,
        backtest_runs_per_month=200,
        max_symbols_per_request=20,
        priority_queue=True
    ),
    PlanType.ENTERPRISE: PlanLimits(
        monthly_api_calls=2000,
        daily_api_calls=200,
        hourly_api_calls=100,
        minute_api_calls=20,
        concurrent_requests=50,
        can_use_advanced_ai=True,
        can_use_vision_ai=True,
        can_export_data=True,
        backtest_runs_per_month=1000,
        max_symbols_per_request=100,
        priority_queue=True
    )
}

class QuotaUsage(BaseModel):
    """配額使用情況"""
    user_id: int
    quota_type: QuotaType
    current_usage: int
    limit: int
    remaining: int
    reset_time: datetime
    percentage_used: float

class RateLimitResult(BaseModel):
    """速率限制檢查結果"""
    allowed: bool
    retry_after: Optional[int] = None
    current_usage: int
    limit: int
    window_type: str  # minute, hour, day, month

# ================================
# Redis配額管理器
# ================================

class RedisQuotaManager:
    """基於Redis的配額管理器"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        
    async def check_rate_limit(
        self,
        user_id: int,
        window: str,  # "minute", "hour", "day", "month"
        limit: int,
        increment: bool = True
    ) -> RateLimitResult:
        """
        檢查速率限制
        
        Args:
            user_id: 用戶ID
            window: 時間窗口
            limit: 限制次數
            increment: 是否增加計數
            
        Returns:
            RateLimitResult: 速率限制結果
        """
        # 生成Redis鍵
        current_time = datetime.now()
        
        if window == "minute":
            window_key = current_time.strftime("%Y-%m-%d:%H:%M")
            window_seconds = 60
        elif window == "hour":
            window_key = current_time.strftime("%Y-%m-%d:%H")
            window_seconds = 3600
        elif window == "day":
            window_key = current_time.strftime("%Y-%m-%d")
            window_seconds = 86400
        elif window == "month":
            window_key = current_time.strftime("%Y-%m")
            window_seconds = 30 * 86400
        else:
            raise ValueError(f"Invalid window: {window}")
            
        redis_key = f"rate_limit:{user_id}:{window}:{window_key}"
        
        # 獲取當前使用量
        current_usage = await self.redis.get(redis_key)
        current_usage = int(current_usage) if current_usage else 0
        
        # 檢查是否超過限制
        if current_usage >= limit:
            return RateLimitResult(
                allowed=False,
                retry_after=window_seconds,
                current_usage=current_usage,
                limit=limit,
                window_type=window
            )
        
        # 如果需要增加計數
        if increment:
            pipe = self.redis.pipeline()
            pipe.incr(redis_key)
            pipe.expire(redis_key, window_seconds)
            await pipe.execute()
            current_usage += 1
        
        return RateLimitResult(
            allowed=True,
            current_usage=current_usage,
            limit=limit,
            window_type=window
        )
    
    async def get_quota_usage(
        self,
        user_id: int,
        quota_type: QuotaType,
        window: str = "month"
    ) -> int:
        """獲取配額使用量"""
        current_time = datetime.now()
        
        if window == "month":
            window_key = current_time.strftime("%Y-%m")
        elif window == "day":
            window_key = current_time.strftime("%Y-%m-%d")
        else:
            window_key = current_time.strftime("%Y-%m-%d:%H")
            
        redis_key = f"quota:{user_id}:{quota_type.value}:{window}:{window_key}"
        usage = await self.redis.get(redis_key)
        return int(usage) if usage else 0
    
    async def increment_quota_usage(
        self,
        user_id: int,
        quota_type: QuotaType,
        amount: int = 1,
        window: str = "month"
    ) -> int:
        """增加配額使用量"""
        current_time = datetime.now()
        
        if window == "month":
            window_key = current_time.strftime("%Y-%m")
            expire_seconds = 30 * 86400
        elif window == "day":
            window_key = current_time.strftime("%Y-%m-%d")
            expire_seconds = 86400
        else:
            window_key = current_time.strftime("%Y-%m-%d:%H")
            expire_seconds = 3600
            
        redis_key = f"quota:{user_id}:{quota_type.value}:{window}:{window_key}"
        
        pipe = self.redis.pipeline()
        pipe.incrby(redis_key, amount)
        pipe.expire(redis_key, expire_seconds)
        results = await pipe.execute()
        
        return results[0]

# ================================
# 配額管理器核心類
# ================================

class QuotaManager:
    """配額管理器核心類"""
    
    def __init__(
        self,
        redis_client: aioredis.Redis,
        db_session: Session
    ):
        self.redis_quota = RedisQuotaManager(redis_client)
        self.db = db_session
        
    async def check_user_limits(
        self,
        user_id: int,
        endpoint: str,
        request_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        檢查用戶是否可以執行請求
        
        Returns:
            Tuple[bool, Optional[str]]: (是否允許, 錯誤消息)
        """
        # 獲取用戶計劃
        user_plan = await self._get_user_plan(user_id)
        if not user_plan:
            return False, "用戶計劃未找到"
            
        plan_limits = PLAN_LIMITS[user_plan.plan_type]
        
        # 1. 檢查並發請求限制
        concurrent_check = await self._check_concurrent_limit(
            user_id, 
            plan_limits.concurrent_requests
        )
        if not concurrent_check[0]:
            return concurrent_check
        
        # 2. 檢查速率限制（分鐘級）
        minute_limit = await self.redis_quota.check_rate_limit(
            user_id=user_id,
            window="minute",
            limit=plan_limits.minute_api_calls,
            increment=False
        )
        if not minute_limit.allowed:
            return False, f"超過每分鐘API調用限制（{plan_limits.minute_api_calls}次）"
        
        # 3. 檢查小時級限制
        hour_limit = await self.redis_quota.check_rate_limit(
            user_id=user_id,
            window="hour", 
            limit=plan_limits.hourly_api_calls,
            increment=False
        )
        if not hour_limit.allowed:
            return False, f"超過每小時API調用限制（{plan_limits.hourly_api_calls}次）"
        
        # 4. 檢查日級限制
        day_limit = await self.redis_quota.check_rate_limit(
            user_id=user_id,
            window="day",
            limit=plan_limits.daily_api_calls,
            increment=False
        )
        if not day_limit.allowed:
            return False, f"超過每日API調用限制（{plan_limits.daily_api_calls}次）"
        
        # 5. 檢查月級限制
        month_usage = await self.redis_quota.get_quota_usage(
            user_id=user_id,
            quota_type=QuotaType.API_CALLS,
            window="month"
        )
        if month_usage >= plan_limits.monthly_api_calls:
            return False, f"超過每月API調用限制（{plan_limits.monthly_api_calls}次）"
        
        # 6. 檢查功能特定限制
        feature_check = await self._check_feature_limits(
            endpoint, user_plan, request_data
        )
        if not feature_check[0]:
            return feature_check
            
        return True, None
    
    async def consume_quota(
        self,
        user_id: int,
        endpoint: str,
        ai_model_used: Optional[str] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        processing_time_ms: int = 0
    ) -> Dict[str, Any]:
        """
        消費用戶配額並記錄使用量
        
        Returns:
            Dict: 消費結果和成本信息
        """
        # 獲取用戶計劃
        user_plan = await self._get_user_plan(user_id)
        plan_limits = PLAN_LIMITS[user_plan.plan_type]
        
        # 計算成本
        cost_usd = Decimal("0")
        if ai_model_used and ai_model_used in MODEL_COSTS:
            model_cost = MODEL_COSTS[AIModel(ai_model_used)]
            input_cost = (Decimal(input_tokens) / 1000) * model_cost.input_cost_per_1k
            output_cost = (Decimal(output_tokens) / 1000) * model_cost.output_cost_per_1k
            cost_usd = input_cost + output_cost
        
        # 更新各級別使用量
        await self.redis_quota.check_rate_limit(
            user_id=user_id, window="minute", 
            limit=plan_limits.minute_api_calls, increment=True
        )
        await self.redis_quota.check_rate_limit(
            user_id=user_id, window="hour",
            limit=plan_limits.hourly_api_calls, increment=True
        )
        await self.redis_quota.check_rate_limit(
            user_id=user_id, window="day",
            limit=plan_limits.daily_api_calls, increment=True
        )
        await self.redis_quota.increment_quota_usage(
            user_id=user_id,
            quota_type=QuotaType.API_CALLS,
            window="month"
        )
        
        # 記錄到數據庫
        usage_record = {
            "user_id": user_id,
            "endpoint": endpoint,
            "ai_model_used": ai_model_used,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": float(cost_usd),
            "processing_time_ms": processing_time_ms,
            "quota_deducted": True,
            "request_time": datetime.now()
        }
        
        # 這裡應該插入到 api_usage 表
        # await self._save_usage_record(usage_record)
        
        return {
            "quota_consumed": 1,
            "cost_usd": float(cost_usd),
            "remaining_quota": plan_limits.monthly_api_calls - await self.redis_quota.get_quota_usage(
                user_id, QuotaType.API_CALLS, "month"
            ),
            "usage_record": usage_record
        }
    
    async def get_user_quota_status(self, user_id: int) -> Dict[str, QuotaUsage]:
        """獲取用戶配額狀態"""
        user_plan = await self._get_user_plan(user_id)
        if not user_plan:
            return {}
            
        plan_limits = PLAN_LIMITS[user_plan.plan_type]
        current_time = datetime.now()
        
        # 獲取各時間窗口的使用量
        quotas = {}
        
        # 月度配額
        monthly_usage = await self.redis_quota.get_quota_usage(
            user_id, QuotaType.API_CALLS, "month"
        )
        quotas["monthly"] = QuotaUsage(
            user_id=user_id,
            quota_type=QuotaType.API_CALLS,
            current_usage=monthly_usage,
            limit=plan_limits.monthly_api_calls,
            remaining=max(0, plan_limits.monthly_api_calls - monthly_usage),
            reset_time=datetime(current_time.year, current_time.month + 1, 1),
            percentage_used=round((monthly_usage / plan_limits.monthly_api_calls) * 100, 2)
        )
        
        # 日度配額
        daily_limit = await self.redis_quota.check_rate_limit(
            user_id, "day", plan_limits.daily_api_calls, increment=False
        )
        quotas["daily"] = QuotaUsage(
            user_id=user_id,
            quota_type=QuotaType.API_CALLS,
            current_usage=daily_limit.current_usage,
            limit=daily_limit.limit,
            remaining=max(0, daily_limit.limit - daily_limit.current_usage),
            reset_time=current_time.replace(hour=0, minute=0, second=0) + timedelta(days=1),
            percentage_used=round((daily_limit.current_usage / daily_limit.limit) * 100, 2)
        )
        
        return quotas
    
    # ================================
    # 內部輔助方法
    # ================================
    
    async def _get_user_plan(self, user_id: int):
        """獲取用戶計劃（模擬，實際應查詢數據庫）"""
        # 這裡應該從數據庫查詢用戶的實際計劃
        from dataclasses import dataclass
        
        @dataclass
        class UserPlan:
            plan_type: PlanType
            status: str
            
        # 模擬返回，實際應該查詢 user_plans 表
        return UserPlan(plan_type=PlanType.BASIC, status="active")
    
    async def _check_concurrent_limit(self, user_id: int, limit: int) -> Tuple[bool, Optional[str]]:
        """檢查並發請求限制"""
        concurrent_key = f"concurrent:{user_id}"
        current_concurrent = await self.redis_quota.redis.get(concurrent_key)
        current_concurrent = int(current_concurrent) if current_concurrent else 0
        
        if current_concurrent >= limit:
            return False, f"超過並發請求限制（{limit}個）"
            
        return True, None
    
    async def _check_feature_limits(
        self, 
        endpoint: str, 
        user_plan, 
        request_data: Optional[Dict]
    ) -> Tuple[bool, Optional[str]]:
        """檢查功能特定限制"""
        plan_limits = PLAN_LIMITS[user_plan.plan_type]
        
        # 檢查高級AI功能
        if "/ai/advanced" in endpoint and not plan_limits.can_use_advanced_ai:
            return False, "當前計劃不支援高級AI功能"
        
        # 檢查視覺AI功能  
        if "/ai/vision" in endpoint and not plan_limits.can_use_vision_ai:
            return False, "當前計劃不支援視覺AI功能"
        
        # 檢查數據導出功能
        if "/export" in endpoint and not plan_limits.can_export_data:
            return False, "當前計劃不支援數據導出功能"
            
        # 檢查符號數量限制
        if request_data and "symbols" in request_data:
            symbols = request_data["symbols"]
            if isinstance(symbols, list) and len(symbols) > plan_limits.max_symbols_per_request:
                return False, f"超過單次請求符號數量限制（{plan_limits.max_symbols_per_request}個）"
        
        return True, None

# ================================
# FastAPI 中介軟體和依賴
# ================================

def quota_required(quota_type: QuotaType = QuotaType.API_CALLS):
    """配額檢查裝飾器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # 從請求中獲取用戶ID（實際應該從JWT token中獲取）
            user_id = getattr(request.state, "user_id", None)
            if not user_id:
                raise HTTPException(status_code=401, detail="未授權")
            
            # 初始化配額管理器
            redis_client = request.app.state.redis
            quota_manager = QuotaManager(redis_client, None)
            
            # 檢查配額
            endpoint = str(request.url.path)
            can_proceed, error_msg = await quota_manager.check_user_limits(
                user_id=user_id,
                endpoint=endpoint,
                request_data=dict(request.query_params) if request.method == "GET" else None
            )
            
            if not can_proceed:
                raise HTTPException(status_code=429, detail=error_msg)
            
            # 執行原函數
            try:
                # 記錄並發請求
                concurrent_key = f"concurrent:{user_id}"
                await redis_client.incr(concurrent_key)
                await redis_client.expire(concurrent_key, 300)  # 5分鐘過期
                
                start_time = time.time()
                result = await func(request, *args, **kwargs)
                end_time = time.time()
                processing_time_ms = int((end_time - start_time) * 1000)
                
                # 消費配額
                await quota_manager.consume_quota(
                    user_id=user_id,
                    endpoint=endpoint,
                    processing_time_ms=processing_time_ms
                )
                
                return result
                
            finally:
                # 釋放並發請求計數
                await redis_client.decr(concurrent_key)
        
        return wrapper
    return decorator

async def get_quota_manager(
    request: Request,
    db: Session = Depends()
) -> QuotaManager:
    """獲取配額管理器依賴"""
    redis_client = request.app.state.redis
    return QuotaManager(redis_client, db)

# ================================
# API端點示例
# ================================

from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/api/quota/status")
async def get_quota_status(
    request: Request,
    quota_manager: QuotaManager = Depends(get_quota_manager)
):
    """獲取用戶配額狀態"""
    user_id = getattr(request.state, "user_id", 1)  # 從JWT中獲取
    status = await quota_manager.get_user_quota_status(user_id)
    return {"status": "success", "data": status}

@app.get("/api/plans/limits")
async def get_plan_limits():
    """獲取所有計劃的限制配置"""
    return {
        "plans": {
            plan.value: asdict(limits) 
            for plan, limits in PLAN_LIMITS.items()
        },
        "model_costs": {
            model.value: {
                "input_cost_per_1k": float(cost.input_cost_per_1k),
                "output_cost_per_1k": float(cost.output_cost_per_1k),
                "speed_tier": cost.speed_tier
            }
            for model, cost in MODEL_COSTS.items()
        }
    }

@app.post("/api/analyze/{symbol}")
@quota_required(QuotaType.AI_ANALYSIS)
async def analyze_stock(
    symbol: str,
    request: Request,
    quota_manager: QuotaManager = Depends(get_quota_manager)
):
    """股票分析端點（需要配額）"""
    # 這裡實現實際的股票分析邏輯
    return {"symbol": symbol, "analysis": "模擬分析結果"}

# ================================
# 配額重置任務
# ================================

import asyncio
from datetime import datetime

class QuotaResetTask:
    """配額重置定時任務"""
    
    def __init__(self, redis_client: aioredis.Redis, db_session):
        self.redis = redis_client
        self.db = db_session
    
    async def reset_monthly_quotas(self):
        """重置月度配額"""
        current_date = datetime.now()
        if current_date.day == 1:  # 每月1號重置
            pattern = "quota:*:month:*"
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            print(f"已重置 {len(keys)} 個月度配額")
    
    async def cleanup_expired_limits(self):
        """清理過期的速率限制鍵"""
        patterns = [
            "rate_limit:*:minute:*",
            "rate_limit:*:hour:*", 
            "concurrent:*"
        ]
        
        for pattern in patterns:
            keys = await self.redis.keys(pattern)
            if keys:
                # 檢查TTL，清理已過期但未自動刪除的鍵
                pipe = self.redis.pipeline()
                for key in keys:
                    pipe.ttl(key)
                ttls = await pipe.execute()
                
                expired_keys = [
                    key for key, ttl in zip(keys, ttls) 
                    if ttl == -1  # TTL為-1表示沒有過期時間但鍵存在
                ]
                
                if expired_keys:
                    await self.redis.delete(*expired_keys)
                    print(f"清理了 {len(expired_keys)} 個過期鍵")

# ================================
# 使用示例和測試
# ================================

if __name__ == "__main__":
    # 這裡可以放置測試代碼
    pass