"""
用戶認證和訂閱系統的Pydantic Schemas

用於API請求驗證和響應序列化
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import uuid

# Enums for better type safety
class UserRole(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentProvider(str, Enum):
    STRIPE = "stripe"
    ECPAY = "ecpay"
    NEWEBPAY = "newebpay"

class ActionType(str, Enum):
    AI_ANALYSIS = "ai_analysis"
    CHART_VIEW = "chart_view"
    PATTERN_ANALYSIS = "pattern_analysis"
    BACKTEST = "backtest"

# ========== 用戶相關 Schemas ==========

class UserBase(BaseModel):
    """用戶基礎信息"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)

class UserCreate(UserBase):
    """創建用戶請求"""
    password: str = Field(..., min_length=6, max_length=128)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密碼至少需要6個字符')
        return v

class UserCreateOAuth(UserBase):
    """OAuth創建用戶請求"""
    google_id: str = Field(..., max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=512)

class UserLogin(BaseModel):
    """用戶登入請求"""
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """更新用戶信息請求"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=512)

class UserResponse(UserBase):
    """用戶信息響應"""
    id: uuid.UUID
    avatar_url: Optional[str] = None
    email_verified: bool = False
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    
    # 訂閱信息
    current_subscription: Optional['SubscriptionResponse'] = None
    is_premium: bool = False
    
    # 配額信息
    remaining_initial_quota: int = 0
    remaining_daily_quota: int = 0
    
    class Config:
        from_attributes = True

# ========== 認證相關 Schemas ==========

class Token(BaseModel):
    """JWT Token響應"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 過期時間（秒）
    user: UserResponse

class TokenPayload(BaseModel):
    """JWT Token載荷"""
    user_id: uuid.UUID
    email: str
    subscription_status: str = "free"
    exp: int
    iat: int

class PasswordReset(BaseModel):
    """重置密碼請求"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """確認重置密碼請求"""
    token: str
    new_password: str = Field(..., min_length=6, max_length=128)

class EmailVerification(BaseModel):
    """郵箱驗證請求"""
    token: str

# ========== 訂閱相關 Schemas ==========

class SubscriptionCreate(BaseModel):
    """創建訂閱請求"""
    plan_type: str = Field(default="premium")
    payment_method: str = Field(..., description="credit_card, ecpay, newebpay")

class SubscriptionResponse(BaseModel):
    """訂閱信息響應"""
    id: uuid.UUID
    plan_type: str
    status: SubscriptionStatus
    started_at: datetime
    expires_at: Optional[datetime] = None
    payment_method: Optional[str] = None
    is_active: bool
    is_premium: bool
    
    class Config:
        from_attributes = True

class SubscriptionPlan(BaseModel):
    """訂閱計劃信息"""
    plan_id: str
    name: str
    name_en: str
    price: Decimal
    currency: str
    billing_cycle: Optional[str] = None
    features: List[str]
    features_en: List[str]

# ========== 支付相關 Schemas ==========

class PaymentCreate(BaseModel):
    """創建支付請求"""
    subscription_id: uuid.UUID
    payment_method: str
    payment_provider: PaymentProvider
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None

class PaymentResponse(BaseModel):
    """支付信息響應"""
    id: uuid.UUID
    amount: Decimal
    currency: str
    payment_method: str
    payment_provider: str
    status: PaymentStatus
    external_transaction_id: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    # 支付URL（重定向到第三方支付頁面）
    payment_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class PaymentWebhook(BaseModel):
    """支付Webhook通知"""
    provider: PaymentProvider
    external_transaction_id: str
    status: PaymentStatus
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

# ========== 使用記錄相關 Schemas ==========

class UsageRecordCreate(BaseModel):
    """創建使用記錄請求"""
    action_type: ActionType
    extra_data: Optional[Dict[str, Any]] = None

class UsageRecordResponse(BaseModel):
    """使用記錄響應"""
    id: uuid.UUID
    action_type: str
    created_at: datetime
    extra_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class UsageStats(BaseModel):
    """使用統計響應"""
    total_ai_analyses: int = 0
    total_chart_views: int = 0
    this_month_ai_analyses: int = 0
    this_month_chart_views: int = 0
    remaining_initial_quota: int = 0
    remaining_daily_quota: int = 0

# ========== 免費配額相關 Schemas ==========

class QuotaResponse(BaseModel):
    """配額信息響應"""
    total_free_uses: int
    used_free_uses: int
    remaining_initial_quota: int
    daily_used_count: int
    remaining_daily_quota: int
    can_use_ai_analysis: bool
    
    class Config:
        from_attributes = True

# ========== Google OAuth Schemas ==========

class GoogleAuthRequest(BaseModel):
    """Google認證請求"""
    id_token: str  # Google ID Token

class GoogleUserInfo(BaseModel):
    """Google用戶信息"""
    google_id: str
    email: str
    name: str
    picture: Optional[str] = None
    email_verified: bool = False

# ========== API響應包裝 Schemas ==========

class APIResponse(BaseModel):
    """統一API響應格式"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    """錯誤響應格式"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# ========== 儀表板相關 Schemas ==========

class DashboardStats(BaseModel):
    """用戶儀表板統計"""
    user: UserResponse
    subscription: Optional[SubscriptionResponse] = None
    usage_stats: UsageStats
    quota_info: QuotaResponse
    recent_activities: List[UsageRecordResponse] = []

# 更新前向引用
UserResponse.model_rebuild()