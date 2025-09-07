"""
Google OAuth 認證模組

提供 Google OAuth 2.0 第三方登入功能
"""

import httpx
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import secrets
import logging

from config.settings import settings
from .schemas import UserCreateOAuth

logger = logging.getLogger(__name__)

class GoogleOAuth:
    """Google OAuth 2.0 處理器"""
    
    def __init__(self):
        self.client_id = settings.google_client_id
        self.client_secret = settings.google_client_secret
        
        # Google OAuth 端點
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        # OAuth 範圍
        self.scopes = ["openid", "email", "profile"]
        
        # 驗證配置
        if not self.client_id or not self.client_secret:
            logger.warning("Google OAuth credentials not configured")
    
    def is_configured(self) -> bool:
        """檢查 OAuth 是否已配置"""
        return bool(self.client_id and self.client_secret)
    
    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """
        生成 Google OAuth 授權 URL
        
        Args:
            redirect_uri: 回調 URL
            state: 狀態參數（可選，用於CSRF保護）
        
        Returns:
            授權 URL
        """
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google OAuth 未配置"
            )
        
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
            "access_type": "offline",  # 獲取refresh token
            "prompt": "select_account"  # 顯示帳號選擇
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"
    
    async def exchange_code_for_token(
        self, 
        code: str, 
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        使用授權碼交換訪問令牌
        
        Args:
            code: Google 授權碼
            redirect_uri: 回調 URL（必須與授權時相同）
        
        Returns:
            包含訪問令牌的字典
        """
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google OAuth 未配置"
            )
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.token_url, data=data)
                response.raise_for_status()
                
                token_data = response.json()
                
                if "error" in token_data:
                    logger.error(f"OAuth token exchange failed: {token_data}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"OAuth 授權失敗: {token_data.get('error_description', 'Unknown error')}"
                    )
                
                return token_data
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during token exchange: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="無法連接到 Google OAuth 服務"
            )
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        使用訪問令牌獲取用戶信息
        
        Args:
            access_token: Google 訪問令牌
        
        Returns:
            用戶信息字典
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.user_info_url, headers=headers)
                response.raise_for_status()
                
                user_data = response.json()
                
                if "error" in user_data:
                    logger.error(f"Failed to get user info: {user_data}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="無法獲取用戶信息"
                    )
                
                return user_data
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during user info fetch: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="無法連接到 Google 用戶信息服務"
            )
    
    def extract_user_data(self, google_user_info: Dict[str, Any]) -> UserCreateOAuth:
        """
        從 Google 用戶信息中提取用戶數據
        
        Args:
            google_user_info: Google API 返回的用戶信息
        
        Returns:
            用於創建用戶的數據對象
        """
        try:
            return UserCreateOAuth(
                email=google_user_info["email"],
                google_id=google_user_info["id"],
                full_name=google_user_info.get("name", ""),
                avatar_url=google_user_info.get("picture")
            )
        except KeyError as e:
            logger.error(f"Missing required field in Google user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google 用戶信息缺少必需字段: {e}"
            )

class OAuthStateManager:
    """OAuth 狀態管理器（簡單實現，生產環境建議使用 Redis）"""
    
    def __init__(self):
        self._states = {}  # 生產環境應使用 Redis 或其他持久化存儲
        self._used_states = set()  # 追蹤已使用的狀態，避免重複使用
        self._used_codes = set()  # 追蹤已使用的authorization codes
    
    def create_state(self, redirect_uri: str, extra_data: Dict[str, Any] = None) -> str:
        """創建並存儲 OAuth 狀態"""
        import time
        state = secrets.token_urlsafe(32)
        
        self._states[state] = {
            "redirect_uri": redirect_uri,
            "created_at": time.time(),  # 使用真實時間戳
            "extra_data": extra_data or {},
            "used": False  # 標記是否已使用
        }
        
        return state
    
    def verify_state(self, state: str) -> Optional[Dict[str, Any]]:
        """驗證並獲取 OAuth 狀態數據"""
        import time
        
        state_data = self._states.get(state, None)
        
        if not state_data:
            logger.warning(f"OAuth state not found: {state}")
            return None
        
        # 檢查是否已經使用過
        if state_data.get("used", False):
            logger.warning(f"OAuth state already used: {state}")
            # 允許短時間內的重複使用（處理瀏覽器重複請求）
            if time.time() - state_data["created_at"] < 30:  # 30秒內允許重用
                logger.info(f"Allowing state reuse within 30 seconds: {state}")
                return state_data
            return None
        
        # 檢查過期（10分鐘）
        if time.time() - state_data["created_at"] > 600:  # 10分鐘過期
            logger.warning(f"OAuth state expired: {state}")
            self._states.pop(state, None)
            return None
        
        # 標記為已使用，但不立即刪除
        state_data["used"] = True
        state_data["used_at"] = time.time()
        
        logger.info(f"OAuth state verified successfully: {state}")
        return state_data
    
    def cleanup_expired_states(self):
        """清理過期狀態（在生產環境中應定期調用）"""
        import time
        current_time = time.time()
        expired_keys = []
        
        # 清理過期的狀態（超過10分鐘）
        for key, state_data in self._states.items():
            if current_time - state_data["created_at"] > 600:  # 10分鐘過期
                expired_keys.append(key)
        
        # 清理已使用且超過1小時的狀態
        for key, state_data in list(self._states.items()):
            if (state_data.get("used", False) and 
                "used_at" in state_data and 
                current_time - state_data["used_at"] > 3600):  # 1小時後清理已使用的狀態
                expired_keys.append(key)
        
        # 移除過期狀態
        for key in set(expired_keys):
            self._states.pop(key, None)
            
        # 防止內存洩漏的緊急清理
        if len(self._states) > 1000:
            logger.warning("OAuth state manager has too many states, performing emergency cleanup")
            # 清理最舊的狀態
            sorted_states = sorted(
                self._states.items(), 
                key=lambda x: x[1]["created_at"]
            )
            keys_to_remove = [k for k, v in sorted_states[:len(sorted_states)//2]]
            for key in keys_to_remove:
                self._states.pop(key, None)
                
        logger.info(f"OAuth state cleanup completed. Removed {len(set(expired_keys))} expired states. Current state count: {len(self._states)}")
    
    def is_code_used(self, code: str) -> bool:
        """檢查authorization code是否已經被使用"""
        return code in self._used_codes
    
    def mark_code_used(self, code: str) -> None:
        """標記authorization code為已使用"""
        self._used_codes.add(code)
        # 防止內存洩漏，保持最多1000個已使用的codes
        if len(self._used_codes) > 1000:
            # 移除一半舊的codes（簡單實現，生產環境應使用時間戳）
            codes_list = list(self._used_codes)
            self._used_codes = set(codes_list[500:])  # 保留後500個

# OAuth 輔助函數
def validate_google_email(email: str) -> bool:
    """驗證 Google 郵箱格式"""
    if not email or "@" not in email:
        return False
    
    # 可以添加更嚴格的郵箱驗證
    return True

def generate_oauth_redirect_uri(base_url: str, endpoint: str = "/auth/google/callback") -> str:
    """生成 OAuth 回調 URI"""
    return f"{base_url.rstrip('/')}{endpoint}"

# 全局實例
google_oauth = GoogleOAuth()
oauth_state_manager = OAuthStateManager()

# 導出主要類別和函數
__all__ = [
    "GoogleOAuth",
    "OAuthStateManager", 
    "google_oauth",
    "oauth_state_manager",
    "validate_google_email",
    "generate_oauth_redirect_uri"
]