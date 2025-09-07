"""
用戶認證和訂閱系統的數據庫模型

包含：
- User: 用戶基本信息
- UsageRecord: 使用記錄
- Subscription: 訂閱信息  
- Payment: 支付記錄
- FreeQuota: 免費配額
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, JSON, Date, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from datetime import datetime, date, timedelta
from typing import Optional
from decimal import Decimal



Base = declarative_base()

class User(Base):
    """用戶表 - 存儲用戶基本信息和認證資料"""
    __tablename__ = "users"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # OAuth用戶可為空
    google_id = Column(String(255), nullable=True, unique=True)  # Google OAuth ID
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    usage_records = relationship("UsageRecord", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    free_quota = relationship("FreeQuota", back_populates="user", uselist=False, cascade="all, delete-orphan")
    redeemed_codes = relationship("RedemptionCode", back_populates="used_by_user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.full_name}')>"

class UsageRecord(Base):
    """使用記錄表 - 追踪用戶AI分析等功能使用情況"""
    __tablename__ = "usage_records"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False, index=True)  # ai_analysis, chart_view, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    extra_data = Column(JSON, nullable=True)  # 額外信息：股票代碼、分析類型等
    
    # Relationships
    user = relationship("User", back_populates="usage_records")
    
    def __repr__(self):
        return f"<UsageRecord(id={self.id}, user_id={self.user_id}, action='{self.action_type}')>"

class Subscription(Base):
    """訂閱表 - 管理用戶訂閱狀態和計費"""
    __tablename__ = "subscriptions"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    plan_type = Column(String(20), nullable=False, default="free")  # free, premium
    status = Column(String(20), nullable=False, default="active")  # active, cancelled, expired, pending
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # 可為空表示終身或免費用戶
    payment_method = Column(String(50), nullable=True)  # credit_card, ecpay, newebpay
    external_subscription_id = Column(String(255), nullable=True)  # Stripe/第三方訂閱ID
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")
    
    @property
    def is_active(self) -> bool:
        """檢查訂閱是否有效"""
        if self.status != "active":
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    @property
    def is_premium(self) -> bool:
        """檢查是否為付費訂閱"""
        return self.plan_type == "premium" and self.is_active
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan='{self.plan_type}', status='{self.status}')>"

class Payment(Base):
    """支付記錄表 - 記錄所有支付交易"""
    __tablename__ = "payments"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = Column(PG_UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)  # 支付金額
    currency = Column(String(3), nullable=False, default="USD")  # USD, TWD
    payment_method = Column(String(50), nullable=False)  # credit_card, ecpay_atm, newebpay_card, etc.
    payment_provider = Column(String(30), nullable=False)  # stripe, ecpay, newebpay
    external_transaction_id = Column(String(255), nullable=True)  # 第三方交易ID
    status = Column(String(20), nullable=False, default="pending")  # pending, completed, failed, refunded
    failure_reason = Column(Text, nullable=True)  # 失敗原因
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)  # 完成時間
    extra_data = Column(JSON, nullable=True)  # 額外支付信息
    
    # Relationships
    user = relationship("User", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount} {self.currency}, status='{self.status}')>"

class FreeQuota(Base):
    """免費配額表 - 管理用戶免費使用次數"""
    __tablename__ = "free_quotas"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    total_free_uses = Column(Integer, nullable=False, default=3)  # 新用戶總免費次數
    used_free_uses = Column(Integer, nullable=False, default=0)  # 已使用的免費次數
    bonus_credits = Column(Integer, nullable=False, default=0)  # 兌換碼獲得的額外AI分析次數
    used_bonus_credits = Column(Integer, nullable=False, default=0)  # 已使用的兌換次數
    daily_reset_date = Column(Date, nullable=False, default=date.today)  # 每日重置日期
    daily_used_count = Column(Integer, nullable=False, default=0)  # 今日已使用次數
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="free_quota")
    
    def can_use_ai_analysis(self) -> bool:
        """檢查用戶是否可以使用AI分析"""
        # 檢查每日配額重置
        self._reset_daily_quota_if_needed()
        
        # 優先使用兌換碼獲得的次數
        if self.used_bonus_credits < self.bonus_credits:
            return True
        
        # 新用戶3次免費配額
        if self.used_free_uses < self.total_free_uses:
            return True
        
        # 每日1次免費配額
        if self.daily_used_count < 1:
            return True
        
        return False
    
    def consume_quota(self) -> bool:
        """消耗配額，返回是否成功"""
        if not self.can_use_ai_analysis():
            return False
        
        # 檢查每日配額重置
        self._reset_daily_quota_if_needed()
        
        # 優先消耗兌換碼獲得的次數
        if self.used_bonus_credits < self.bonus_credits:
            self.used_bonus_credits += 1
        # 其次消耗新用戶配額
        elif self.used_free_uses < self.total_free_uses:
            self.used_free_uses += 1
        else:
            # 最後消耗每日配額
            self.daily_used_count += 1
        
        self.updated_at = datetime.utcnow()
        return True
    
    def add_bonus_credits(self, credits: int) -> None:
        """添加兌換碼獲得的額外次數"""
        self.bonus_credits += credits
        self.updated_at = datetime.utcnow()
    
    def _reset_daily_quota_if_needed(self):
        """重置每日配額（如果需要）"""
        today = date.today()
        
        # Ensure we are comparing date objects
        reset_date = self.daily_reset_date
        if isinstance(reset_date, datetime):
            reset_date = reset_date.date()

        if reset_date < today:
            self.daily_reset_date = today
            self.daily_used_count = 0
    
    @property
    def remaining_bonus_credits(self) -> int:
        """剩餘的兌換碼次數"""
        return max(0, self.bonus_credits - self.used_bonus_credits)
    
    @property
    def remaining_initial_quota(self) -> int:
        """剩餘的初始免費次數"""
        return max(0, self.total_free_uses - self.used_free_uses)
    
    @property
    def remaining_daily_quota(self) -> int:
        """剩餘的每日免費次數"""
        self._reset_daily_quota_if_needed()
        return max(0, 1 - self.daily_used_count)
    
    @property
    def total_remaining_quota(self) -> int:
        """總剩餘次數"""
        return self.remaining_bonus_credits + self.remaining_initial_quota + self.remaining_daily_quota
    
    def __repr__(self):
        return f"<FreeQuota(user_id={self.user_id}, bonus={self.remaining_bonus_credits}, free={self.used_free_uses}/{self.total_free_uses}, daily={self.daily_used_count}/1)>"


# 數據庫初始化函數
def create_tables(engine):
    """創建所有數據表"""
    Base.metadata.create_all(bind=engine)

def drop_tables(engine):
    """刪除所有數據表（慎用！）"""
    Base.metadata.drop_all(bind=engine)

# 預設訂閱計劃配置
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "免費方案",
        "name_en": "Free Plan",
        "price": 0,
        "currency": "USD",
        "features": [
            "新用戶3次免費AI分析",
            "每日1次免費AI分析",
            "基礎技術指標",
            "圖表瀏覽"
        ],
        "features_en": [
            "3 free AI analyses for new users",
            "1 daily free AI analysis",
            "Basic technical indicators",
            "Chart browsing"
        ]
    },
    "premium": {
        "name": "付費方案",
        "name_en": "Premium Plan",
        "price": 5.00,
        "currency": "USD",
        "billing_cycle": "monthly",
        "features": [
            "無限AI分析次數",
            "進階技術指標",
            "AI策略建議",
            "實時數據更新",
            "客戶支援"
        ],
        "features_en": [
            "Unlimited AI analyses",
            "Advanced technical indicators",
            "AI strategy recommendations",
            "Real-time data updates",
            "Customer support"
        ]
    }
}