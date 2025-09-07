"""
用戶認證和訂閱系統的數據庫CRUD操作

提供對數據庫模型的標準CRUD操作
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func, extract
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import uuid
import hashlib
import secrets

from .models import User, UsageRecord, Subscription, Payment, FreeQuota
from .schemas import (
    UserCreate, UserCreateOAuth, UserUpdate, 
    SubscriptionCreate, PaymentCreate, UsageRecordCreate
)

# ========== 用戶相關 CRUD ==========

def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """通過ID獲取用戶"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """通過Email獲取用戶"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    """通過Google ID獲取用戶"""
    return db.query(User).filter(User.google_id == google_id).first()

def get_user_with_relations(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """獲取用戶及其關聯數據"""
    return db.query(User).options(
        joinedload(User.subscriptions),
        joinedload(User.free_quota),
        joinedload(User.usage_records)
    ).filter(User.id == user_id).first()

def create_user(db: Session, user_create: UserCreate) -> User:
    """創建Email註冊用戶"""
    # 生成密碼哈希
    password_hash = hash_password(user_create.password)
    
    # 生成郵箱驗證令牌
    verification_token = generate_verification_token()
    
    # 生成UUID
    user_id = str(uuid.uuid4())
    
    # 創建用戶
    db_user = User(
        id=user_id,
        email=user_create.email,
        password_hash=password_hash,
        full_name=user_create.full_name,
        verification_token=verification_token,
        email_verified=False
    )
    
    db.add(db_user)
    db.flush()  # 獲取用戶ID
    
    # 創建免費配額記錄
    create_free_quota(db, db_user.id)
    
    # 創建免費訂閱
    create_free_subscription(db, db_user.id)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def create_oauth_user(db: Session, user_create: UserCreateOAuth) -> User:
    """創建OAuth用戶"""
    db_user = User(
        email=user_create.email,
        google_id=user_create.google_id,
        full_name=user_create.full_name,
        avatar_url=user_create.avatar_url,
        email_verified=True,  # OAuth用戶默認已驗證
        password_hash=None
    )
    
    db.add(db_user)
    db.flush()
    
    # 創建免費配額記錄
    create_free_quota(db, db_user.id)
    
    # 創建免費訂閱
    create_free_subscription(db, db_user.id)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: uuid.UUID, user_update: UserUpdate) -> Optional[User]:
    """更新用戶信息"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_user_email(db: Session, verification_token: str) -> Optional[User]:
    """驗證用戶郵箱"""
    db_user = db.query(User).filter(User.verification_token == verification_token).first()
    if not db_user:
        return None
    
    db_user.email_verified = True
    db_user.verification_token = None
    db_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_login(db: Session, user_id: uuid.UUID):
    """更新用戶最後登入時間"""
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.last_login = datetime.utcnow()
        db.commit()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """驗證用戶密碼"""
    user = get_user_by_email(db, email)
    if not user or not user.password_hash:
        return None
    
    if verify_password(password, user.password_hash):
        return user
    return None

# ========== 訂閱相關 CRUD ==========

def get_user_active_subscription(db: Session, user_id: uuid.UUID) -> Optional[Subscription]:
    """獲取用戶當前有效訂閱"""
    return db.query(Subscription).filter(
        and_(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            or_(
                Subscription.expires_at.is_(None),
                Subscription.expires_at > datetime.utcnow()
            )
        )
    ).order_by(desc(Subscription.created_at)).first()

def create_subscription(db: Session, user_id: uuid.UUID, subscription_create: SubscriptionCreate) -> Subscription:
    """創建付費訂閱"""
    # 如果有舊的訂閱，標記為已取消
    old_subscription = get_user_active_subscription(db, user_id)
    if old_subscription:
        old_subscription.status = "cancelled"
        old_subscription.updated_at = datetime.utcnow()
    
    # 計算過期時間（月付）
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    db_subscription = Subscription(
        id=str(uuid.uuid4()),
        user_id=user_id,
        plan_type="premium",
        status="pending",  # 等待支付確認
        payment_method=subscription_create.payment_method,
        expires_at=expires_at
    )
    
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

def create_free_subscription(db: Session, user_id: uuid.UUID) -> Subscription:
    """創建免費訂閱"""
    db_subscription = Subscription(
        id=str(uuid.uuid4()),
        user_id=user_id,
        plan_type="free",
        status="active",
        expires_at=None  # 免費訂閱不過期
    )
    
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

def activate_subscription(db: Session, subscription_id: uuid.UUID, external_id: str = None) -> Optional[Subscription]:
    """激活訂閱（支付成功後）"""
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        return None
    
    db_subscription.status = "active"
    db_subscription.external_subscription_id = external_id
    db_subscription.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

def cancel_subscription(db: Session, subscription_id: uuid.UUID) -> Optional[Subscription]:
    """取消訂閱"""
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        return None
    
    db_subscription.status = "cancelled"
    db_subscription.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

# ========== 支付相關 CRUD ==========

def create_payment(db: Session, user_id: uuid.UUID, payment_create: PaymentCreate) -> Payment:
    """創建支付記錄"""
    db_payment = Payment(
        id=str(uuid.uuid4()),
        user_id=user_id,
        subscription_id=payment_create.subscription_id,
        amount=5.00,  # 固定月費
        currency="USD",
        payment_method=payment_create.payment_method,
        payment_provider=payment_create.payment_provider.value,
        status="pending"
    )
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def update_payment_status(
    db: Session, 
    external_transaction_id: str, 
    status: str, 
    failure_reason: str = None
) -> Optional[Payment]:
    """更新支付狀態"""
    db_payment = db.query(Payment).filter(
        Payment.external_transaction_id == external_transaction_id
    ).first()
    
    if not db_payment:
        return None
    
    db_payment.status = status
    if failure_reason:
        db_payment.failure_reason = failure_reason
    
    if status == "completed":
        db_payment.completed_at = datetime.utcnow()
        # 如果支付成功，激活訂閱
        if db_payment.subscription_id:
            activate_subscription(db, db_payment.subscription_id, external_transaction_id)
    
    db.commit()
    db.refresh(db_payment)
    return db_payment

def get_payment_by_external_id(db: Session, external_transaction_id: str) -> Optional[Payment]:
    """通過外部交易ID獲取支付記錄"""
    return db.query(Payment).filter(
        Payment.external_transaction_id == external_transaction_id
    ).first()

# ========== 使用記錄相關 CRUD ==========

def create_usage_record(db: Session, user_id: uuid.UUID, usage_create: UsageRecordCreate) -> UsageRecord:
    """創建使用記錄"""
    db_usage = UsageRecord(
        id=str(uuid.uuid4()),
        user_id=user_id,
        action_type=usage_create.action_type.value,
        extra_data=usage_create.extra_data
    )
    
    db.add(db_usage)
    db.commit()
    db.refresh(db_usage)
    return db_usage

def get_user_usage_records(
    db: Session, 
    user_id: uuid.UUID, 
    action_type: str = None,
    limit: int = 50
) -> List[UsageRecord]:
    """獲取用戶使用記錄"""
    query = db.query(UsageRecord).filter(UsageRecord.user_id == user_id)
    
    if action_type:
        query = query.filter(UsageRecord.action_type == action_type)
    
    return query.order_by(desc(UsageRecord.created_at)).limit(limit).all()

def get_user_usage_stats(db: Session, user_id: uuid.UUID) -> Dict[str, int]:
    """獲取用戶使用統計"""
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # 總計使用次數
    total_ai = db.query(func.count(UsageRecord.id)).filter(
        and_(
            UsageRecord.user_id == user_id,
            UsageRecord.action_type == "ai_analysis"
        )
    ).scalar()
    
    total_chart = db.query(func.count(UsageRecord.id)).filter(
        and_(
            UsageRecord.user_id == user_id,
            UsageRecord.action_type == "chart_view"
        )
    ).scalar()
    
    # 本月使用次數
    month_ai = db.query(func.count(UsageRecord.id)).filter(
        and_(
            UsageRecord.user_id == user_id,
            UsageRecord.action_type == "ai_analysis",
            UsageRecord.created_at >= month_start
        )
    ).scalar()
    
    month_chart = db.query(func.count(UsageRecord.id)).filter(
        and_(
            UsageRecord.user_id == user_id,
            UsageRecord.action_type == "chart_view",
            UsageRecord.created_at >= month_start
        )
    ).scalar()
    
    return {
        "total_ai_analyses": total_ai or 0,
        "total_chart_views": total_chart or 0,
        "this_month_ai_analyses": month_ai or 0,
        "this_month_chart_views": month_chart or 0
    }

def record_ai_usage(db: Session, user_id: uuid.UUID, action_type: str) -> UsageRecord:
    """記錄用戶AI使用"""
    # 創建使用記錄
    usage_record = UsageRecord(
        user_id=user_id,
        action_type=action_type,
        extra_data={"resource_type": "ai_analysis", "timestamp": datetime.utcnow().isoformat()}
    )
    
    db.add(usage_record)
    
    # 更新配額
    quota = get_user_quota(db, user_id)
    if quota:
        quota.consume_quota()
    
    db.commit()
    db.refresh(usage_record)
    return usage_record

# ========== 免費配額相關 CRUD ==========

def create_free_quota(db: Session, user_id: uuid.UUID) -> FreeQuota:
    """創建免費配額記錄"""
    db_quota = FreeQuota(
        id=str(uuid.uuid4()),
        user_id=user_id,
        total_free_uses=3,
        used_free_uses=0,
        daily_used_count=0
    )
    
    db.add(db_quota)
    db.commit()
    db.refresh(db_quota)
    return db_quota

def get_user_quota(db: Session, user_id: uuid.UUID) -> Optional[FreeQuota]:
    """獲取用戶配額信息"""
    return db.query(FreeQuota).filter(FreeQuota.user_id == user_id).first()

def consume_user_quota(db: Session, user_id: uuid.UUID) -> bool:
    """消耗用戶配額"""
    quota = get_user_quota(db, user_id)
    if not quota:
        return False
    
    if quota.consume_quota():
        db.commit()
        return True
    
    return False

def check_user_can_use_ai(db: Session, user_id: uuid.UUID) -> bool:
    """檢查用戶是否可以使用AI分析"""
    # 檢查是否為付費用戶
    subscription = get_user_active_subscription(db, user_id)
    if subscription and subscription.is_premium:
        return True
    
    # 檢查免費配額
    quota = get_user_quota(db, user_id)
    if quota:
        return quota.can_use_ai_analysis()
    
    return False

# ========== 輔助函數 ==========

def hash_password(password: str) -> str:
    """生成密碼哈希"""
    salt = secrets.token_hex(32)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${password_hash.hex()}"

def verify_password(password: str, password_hash: str) -> bool:
    """驗證密碼"""
    try:
        salt, hash_hex = password_hash.split('$')
        hash_bytes = bytes.fromhex(hash_hex)
        password_bytes = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return hash_bytes == password_bytes
    except ValueError:
        return False

def generate_verification_token() -> str:
    """生成郵箱驗證令牌"""
    return secrets.token_urlsafe(32)

def generate_reset_token() -> str:
    """生成密碼重置令牌"""
    return secrets.token_urlsafe(32)

# ========== 管理員功能 ==========

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """獲取所有用戶（管理員功能）"""
    return db.query(User).offset(skip).limit(limit).all()

def get_users_count(db: Session) -> int:
    """獲取用戶總數"""
    return db.query(func.count(User.id)).scalar()

def get_premium_users_count(db: Session) -> int:
    """獲取付費用戶數"""
    return db.query(func.count(Subscription.id)).filter(
        and_(
            Subscription.plan_type == "premium",
            Subscription.status == "active"
        )
    ).scalar()

def get_monthly_revenue(db: Session, year: int = None, month: int = None) -> float:
    """獲取月度收入"""
    if not year:
        year = datetime.utcnow().year
    if not month:
        month = datetime.utcnow().month
    
    revenue = db.query(func.sum(Payment.amount)).filter(
        and_(
            Payment.status == "completed",
            extract('year', Payment.completed_at) == year,
            extract('month', Payment.completed_at) == month
        )
    ).scalar()
    
    return float(revenue) if revenue else 0.0