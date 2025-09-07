"""
JWT認證和權限控制系統

提供JWT token生成、驗證和權限檢查功能
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt import PyJWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid

from config.settings import settings
from src.database.connection import get_db_session
from .models import User
from .schemas import TokenPayload, UserResponse
from . import crud

# JWT配置
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Security scheme
security = HTTPBearer()

class JWTHandler:
    """JWT Token處理器"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """創建JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow()
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenPayload]:
        """驗證JWT token並返回payload"""
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
            
            # 檢查必需字段
            user_id: str = payload.get("user_id")
            if user_id is None:
                return None
            
            # 轉換為TokenPayload對象
            token_data = TokenPayload(
                user_id=uuid.UUID(user_id),
                email=payload.get("email", ""),
                subscription_status=payload.get("subscription_status", "free"),
                exp=payload.get("exp", 0),
                iat=payload.get("iat", 0)
            )
            
            return token_data
            
        except PyJWTError:
            return None
    
    @staticmethod
    def create_user_token(user: User, subscription_status: str = "free") -> str:
        """為用戶創建JWT token"""
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "subscription_status": subscription_status
        }
        
        return JWTHandler.create_access_token(token_data)

# 依賴注入函數
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session)
) -> User:
    """獲取當前認證用戶"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 提取token
        token = credentials.credentials
        
        # 驗證token
        payload = JWTHandler.verify_token(token)
        if payload is None:
            raise credentials_exception
        
        # 獲取用戶
        user = crud.get_user_by_id(db, payload.user_id)
        if user is None:
            raise credentials_exception
        
        # 檢查用戶是否活躍
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用戶帳戶已被停用"
            )
        
        return user
        
    except PyJWTError:
        raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """獲取當前活躍用戶"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="用戶帳戶已停用"
        )
    return current_user

async def get_current_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """獲取當前已驗證郵箱的用戶"""
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="請先驗證您的郵箱地址"
        )
    return current_user

class PermissionChecker:
    """權限檢查器"""
    
    def __init__(self, required_premium: bool = False):
        self.required_premium = required_premium
    
    async def __call__(
        self, 
        current_user: User = Depends(get_current_verified_user),
        db: Session = Depends(get_db_session)
    ) -> User:
        """檢查用戶權限"""
        
        if self.required_premium:
            # 檢查是否為付費用戶
            subscription = crud.get_user_active_subscription(db, current_user.id)
            if not subscription or not subscription.is_premium:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="此功能需要付費訂閱，請升級您的帳戶"
                )
        
        return current_user

class AIUsageChecker:
    """AI使用配額檢查器"""
    
    async def __call__(
        self,
        current_user: User = Depends(get_current_verified_user),
        db: Session = Depends(get_db_session)
    ) -> User:
        """檢查用戶是否可以使用AI分析"""
        
        # 檢查是否可以使用AI分析
        if not crud.check_user_can_use_ai(db, current_user.id):
            # 獲取配額信息用於錯誤提示
            quota = crud.get_user_quota(db, current_user.id)
            subscription = crud.get_user_active_subscription(db, current_user.id)
            
            if subscription and subscription.is_premium:
                # 付費用戶不應該到這裡，可能是系統錯誤
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="付費用戶配額檢查錯誤，請聯繫客服"
                )
            
            # 免費用戶配額用盡
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
        
        return current_user

# 便捷權限檢查函數
require_premium = PermissionChecker(required_premium=True)
check_ai_usage = AIUsageChecker()

# 可選認證依賴（用於允許未登入用戶訪問的端點）
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db_session)
) -> Optional[User]:
    """獲取可選的當前用戶（可能為None）"""
    
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = JWTHandler.verify_token(token)
        if payload is None:
            return None
        
        user = crud.get_user_by_id(db, payload.user_id)
        if user and user.is_active:
            return user
    except:
        pass
    
    return None

def create_user_response_with_subscription(user: User, db: Session) -> UserResponse:
    """創建包含訂閱信息的用戶響應"""
    # 獲取當前訂閱
    subscription = crud.get_user_active_subscription(db, user.id)
    
    # 獲取配額信息
    quota = crud.get_user_quota(db, user.id)
    
    # 構建響應
    user_response = UserResponse.from_orm(user)
    
    # 添加訂閱信息
    if subscription:
        user_response.current_subscription = subscription
        user_response.is_premium = subscription.is_premium
    
    # 添加配額信息
    if quota:
        user_response.remaining_initial_quota = quota.remaining_initial_quota
        user_response.remaining_daily_quota = quota.remaining_daily_quota
    
    return user_response

# 速率限制裝飾器（可擴展）
class RateLimiter:
    """速率限制器（基礎實現）"""
    
    def __init__(self, max_requests: int = 100, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.requests = {}  # 簡單內存存儲，生產環境建議使用Redis
    
    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """檢查速率限制"""
        # 這裡可以實現更複雜的速率限制邏輯
        # 目前僅返回用戶，實際限制邏輯待實現
        return current_user

# 創建不同的速率限制實例
api_rate_limiter = RateLimiter(max_requests=100, window_minutes=60)
ai_rate_limiter = RateLimiter(max_requests=10, window_minutes=60)

# 密碼強度檢查
def validate_password_strength(password: str) -> bool:
    """檢查密碼強度"""
    if len(password) < 6:
        return False
    
    # 可以添加更多密碼強度檢查規則
    # 例如：包含大小寫字母、數字、特殊字符等
    
    return True

# 郵箱域名白名單（可選）
ALLOWED_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    # 可以添加更多允許的域名
]

def validate_email_domain(email: str) -> bool:
    """驗證郵箱域名（可選功能）"""
    if not ALLOWED_EMAIL_DOMAINS:
        return True  # 如果沒有限制，則允許所有域名
    
    domain = email.split("@")[-1].lower()
    return domain in ALLOWED_EMAIL_DOMAINS

# OAuth相關輔助函數
def generate_state_parameter() -> str:
    """生成OAuth state參數"""
    import secrets
    return secrets.token_urlsafe(32)

def verify_state_parameter(state: str, stored_state: str) -> bool:
    """驗證OAuth state參數"""
    return state == stored_state

# 會話管理（可選，用於更高級的會話控制）
class SessionManager:
    """會話管理器"""
    
    def __init__(self):
        self.active_sessions = {}  # 生產環境建議使用Redis
    
    def create_session(self, user_id: uuid.UUID, token: str, expires_at: datetime):
        """創建會話記錄"""
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
        return session_id
    
    def invalidate_session(self, session_id: str):
        """廢除會話"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def invalidate_user_sessions(self, user_id: uuid.UUID):
        """廢除用戶所有會話"""
        to_remove = []
        for session_id, session_data in self.active_sessions.items():
            if session_data["user_id"] == user_id:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.active_sessions[session_id]

# 全局會話管理器實例
session_manager = SessionManager()