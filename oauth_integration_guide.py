"""
第三方登入整合指南
==================

包含Google、Facebook等OAuth2整合的完整實現

作者: Claude Code AI Assistant  
日期: 2024
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import secrets
import hashlib
import urllib.parse
from dataclasses import dataclass
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
import httpx
import jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

# ================================
# OAuth提供商配置
# ================================

class OAuthProvider(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook" 
    GITHUB = "github"

@dataclass
class OAuthConfig:
    """OAuth配置類"""
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: List[str]
    auth_url: str
    token_url: str
    user_info_url: str

# OAuth配置字典
OAUTH_CONFIGS = {
    OAuthProvider.GOOGLE: OAuthConfig(
        client_id="your_google_client_id.apps.googleusercontent.com",
        client_secret="your_google_client_secret",
        redirect_uri="https://yourdomain.com/auth/google/callback",
        scope=["openid", "email", "profile"],
        auth_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        user_info_url="https://www.googleapis.com/oauth2/v2/userinfo"
    ),
    OAuthProvider.FACEBOOK: OAuthConfig(
        client_id="your_facebook_app_id",
        client_secret="your_facebook_app_secret",
        redirect_uri="https://yourdomain.com/auth/facebook/callback",
        scope=["email", "public_profile"],
        auth_url="https://www.facebook.com/v18.0/dialog/oauth",
        token_url="https://graph.facebook.com/v18.0/oauth/access_token",
        user_info_url="https://graph.facebook.com/v18.0/me"
    ),
    OAuthProvider.GITHUB: OAuthConfig(
        client_id="your_github_client_id",
        client_secret="your_github_client_secret", 
        redirect_uri="https://yourdomain.com/auth/github/callback",
        scope=["user:email", "read:user"],
        auth_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        user_info_url="https://api.github.com/user"
    )
}

# ================================
# 數據模型
# ================================

class OAuthUserInfo(BaseModel):
    """OAuth用戶資訊"""
    provider_user_id: str
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    locale: Optional[str] = None
    verified_email: bool = False

class OAuthState(BaseModel):
    """OAuth狀態參數"""
    state: str
    redirect_to: Optional[str] = None
    created_at: datetime

class LoginResult(BaseModel):
    """登入結果"""
    success: bool
    user_id: Optional[int] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    is_new_user: bool = False
    error: Optional[str] = None

# ================================
# OAuth管理器
# ================================

class OAuthManager:
    """OAuth管理器"""
    
    def __init__(self, db: Session, redis_client):
        self.db = db
        self.redis = redis_client
        
    def generate_authorization_url(
        self, 
        provider: OAuthProvider,
        redirect_to: Optional[str] = None
    ) -> str:
        """生成OAuth授權URL"""
        
        config = OAUTH_CONFIGS[provider]
        
        # 生成state參數用於CSRF保護
        state = secrets.token_urlsafe(32)
        
        # 儲存state到Redis（10分鐘過期）
        state_data = OAuthState(
            state=state,
            redirect_to=redirect_to,
            created_at=datetime.now()
        )
        
        asyncio.create_task(
            self.redis.setex(
                f"oauth_state:{state}",
                600,  # 10分鐘
                state_data.json()
            )
        )
        
        # 構建授權URL
        params = {
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scope": " ".join(config.scope),
            "state": state,
            "response_type": "code"
        }
        
        # 添加提供商特定參數
        if provider == OAuthProvider.GOOGLE:
            params["access_type"] = "offline"
            params["prompt"] = "consent"
        elif provider == OAuthProvider.FACEBOOK:
            params["display"] = "popup"
        
        query_string = urllib.parse.urlencode(params)
        return f"{config.auth_url}?{query_string}"
    
    async def handle_callback(
        self,
        provider: OAuthProvider,
        code: str,
        state: str
    ) -> LoginResult:
        """處理OAuth回調"""
        
        # 驗證state參數
        state_data = await self._validate_state(state)
        if not state_data:
            return LoginResult(success=False, error="無效的狀態參數")
        
        try:
            # 交換授權碼獲取access token
            tokens = await self._exchange_code_for_tokens(provider, code)
            if not tokens:
                return LoginResult(success=False, error="獲取access token失敗")
            
            # 獲取用戶資訊
            user_info = await self._get_user_info(provider, tokens["access_token"])
            if not user_info:
                return LoginResult(success=False, error="獲取用戶資訊失敗")
            
            # 創建或更新用戶
            user_id, is_new_user = await self._create_or_update_user(
                provider, user_info, tokens
            )
            
            # 生成JWT tokens
            access_token, refresh_token = self._generate_jwt_tokens(user_id)
            
            return LoginResult(
                success=True,
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                is_new_user=is_new_user
            )
            
        except Exception as e:
            return LoginResult(success=False, error=str(e))
    
    async def _validate_state(self, state: str) -> Optional[OAuthState]:
        """驗證OAuth state參數"""
        try:
            state_json = await self.redis.get(f"oauth_state:{state}")
            if not state_json:
                return None
            
            state_data = OAuthState.parse_raw(state_json)
            
            # 檢查是否過期（雙重保險）
            if datetime.now() - state_data.created_at > timedelta(minutes=10):
                return None
            
            # 刪除使用過的state
            await self.redis.delete(f"oauth_state:{state}")
            
            return state_data
            
        except Exception:
            return None
    
    async def _exchange_code_for_tokens(
        self, 
        provider: OAuthProvider, 
        code: str
    ) -> Optional[Dict[str, Any]]:
        """交換授權碼獲取tokens"""
        
        config = OAUTH_CONFIGS[provider]
        
        data = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": code,
            "redirect_uri": config.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            # Facebook需要特殊處理
            if provider == OAuthProvider.FACEBOOK:
                response = await client.get(config.token_url, params=data)
            else:
                response = await client.post(
                    config.token_url,
                    data=data,
                    headers={"Accept": "application/json"}
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Token exchange failed: {response.text}")
                return None
    
    async def _get_user_info(
        self,
        provider: OAuthProvider,
        access_token: str
    ) -> Optional[OAuthUserInfo]:
        """獲取用戶資訊"""
        
        config = OAUTH_CONFIGS[provider]
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            if provider == OAuthProvider.FACEBOOK:
                # Facebook需要指定返回字段
                url = f"{config.user_info_url}?fields=id,name,email,picture"
                response = await client.get(url, headers=headers)
            elif provider == OAuthProvider.GITHUB:
                # GitHub需要額外請求獲取email
                response = await client.get(config.user_info_url, headers=headers)
                if response.status_code == 200:
                    user_data = response.json()
                    # 獲取email
                    email_response = await client.get(
                        "https://api.github.com/user/emails", 
                        headers=headers
                    )
                    if email_response.status_code == 200:
                        emails = email_response.json()
                        primary_email = next(
                            (e["email"] for e in emails if e["primary"]), 
                            None
                        )
                        if primary_email:
                            user_data["email"] = primary_email
            else:
                response = await client.get(config.user_info_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_user_info(provider, data)
            else:
                print(f"Get user info failed: {response.text}")
                return None
    
    def _parse_user_info(
        self, 
        provider: OAuthProvider, 
        data: Dict[str, Any]
    ) -> OAuthUserInfo:
        """解析用戶資訊"""
        
        if provider == OAuthProvider.GOOGLE:
            return OAuthUserInfo(
                provider_user_id=data["id"],
                email=data["email"],
                name=data["name"],
                avatar_url=data.get("picture"),
                locale=data.get("locale"),
                verified_email=data.get("verified_email", False)
            )
        elif provider == OAuthProvider.FACEBOOK:
            return OAuthUserInfo(
                provider_user_id=data["id"],
                email=data.get("email", ""),
                name=data["name"],
                avatar_url=data.get("picture", {}).get("data", {}).get("url"),
                verified_email=True  # Facebook只返回已驗證的email
            )
        elif provider == OAuthProvider.GITHUB:
            return OAuthUserInfo(
                provider_user_id=str(data["id"]),
                email=data.get("email", ""),
                name=data.get("name") or data.get("login"),
                avatar_url=data.get("avatar_url"),
                locale=data.get("locale"),
                verified_email=True
            )
    
    async def _create_or_update_user(
        self,
        provider: OAuthProvider,
        user_info: OAuthUserInfo,
        tokens: Dict[str, Any]
    ) -> tuple[int, bool]:
        """創建或更新用戶"""
        
        # 檢查是否已存在OAuth記錄
        from src.database.models import User, UserOAuth
        
        oauth_record = self.db.query(UserOAuth).filter(
            UserOAuth.provider == provider.value,
            UserOAuth.provider_user_id == user_info.provider_user_id
        ).first()
        
        if oauth_record:
            # 更新現有記錄
            oauth_record.access_token = tokens.get("access_token")
            oauth_record.refresh_token = tokens.get("refresh_token")
            oauth_record.token_expires_at = self._calculate_token_expiry(tokens)
            oauth_record.last_used_at = datetime.now()
            oauth_record.provider_email = user_info.email
            oauth_record.provider_name = user_info.name
            oauth_record.provider_avatar = user_info.avatar_url
            
            self.db.commit()
            return oauth_record.user_id, False
        
        else:
            # 檢查是否存在相同email的用戶
            existing_user = None
            if user_info.email:
                existing_user = self.db.query(User).filter(
                    User.email == user_info.email
                ).first()
            
            if existing_user:
                user_id = existing_user.id
                is_new_user = False
            else:
                # 創建新用戶
                new_user = User(
                    username=self._generate_username(user_info.name, user_info.email),
                    email=user_info.email,
                    full_name=user_info.name,
                    avatar_url=user_info.avatar_url,
                    registration_method=provider.value,
                    is_verified=user_info.verified_email,
                    registration_date=datetime.now()
                )
                
                self.db.add(new_user)
                self.db.flush()  # 獲取ID但不提交
                user_id = new_user.id
                is_new_user = True
            
            # 創建OAuth記錄
            oauth_record = UserOAuth(
                user_id=user_id,
                provider=provider.value,
                provider_user_id=user_info.provider_user_id,
                provider_email=user_info.email,
                provider_name=user_info.name,
                provider_avatar=user_info.avatar_url,
                access_token=tokens.get("access_token"),
                refresh_token=tokens.get("refresh_token"),
                token_expires_at=self._calculate_token_expiry(tokens),
                is_primary=True,
                created_at=datetime.now()
            )
            
            self.db.add(oauth_record)
            self.db.commit()
            
            return user_id, is_new_user
    
    def _generate_username(self, name: str, email: str) -> str:
        """生成用戶名"""
        # 從name或email生成用戶名
        if name:
            base_username = name.lower().replace(" ", "_")
        else:
            base_username = email.split("@")[0] if email else "user"
        
        # 確保用戶名唯一
        from src.database.models import User
        
        counter = 1
        username = base_username
        while self.db.query(User).filter(User.username == username).first():
            username = f"{base_username}_{counter}"
            counter += 1
            
        return username
    
    def _calculate_token_expiry(self, tokens: Dict[str, Any]) -> Optional[datetime]:
        """計算token過期時間"""
        expires_in = tokens.get("expires_in")
        if expires_in:
            return datetime.now() + timedelta(seconds=int(expires_in))
        return None
    
    def _generate_jwt_tokens(self, user_id: int) -> tuple[str, str]:
        """生成JWT tokens"""
        from config.settings import settings
        
        # Access token (15分鐘)
        access_payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "iat": datetime.utcnow()
        }
        access_token = jwt.encode(
            access_payload, 
            settings.jwt_secret_key, 
            algorithm="HS256"
        )
        
        # Refresh token (7天)
        refresh_payload = {
            "sub": str(user_id),
            "type": "refresh", 
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow()
        }
        refresh_token = jwt.encode(
            refresh_payload,
            settings.jwt_secret_key,
            algorithm="HS256"
        )
        
        return access_token, refresh_token

# ================================
# FastAPI端點實現
# ================================

app = FastAPI()
oauth_manager = None  # 初始化時設置

@app.get("/auth/{provider}")
async def oauth_login(
    provider: OAuthProvider,
    request: Request,
    redirect_to: Optional[str] = None
):
    """開始OAuth登入流程"""
    try:
        auth_url = oauth_manager.generate_authorization_url(
            provider, 
            redirect_to
        )
        return RedirectResponse(url=auth_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/auth/{provider}/callback")
async def oauth_callback(
    provider: OAuthProvider,
    code: str,
    state: str,
    error: Optional[str] = None
):
    """處理OAuth回調"""
    
    if error:
        # 用戶拒絕授權
        return RedirectResponse(
            url=f"/login?error={urllib.parse.quote(error)}"
        )
    
    try:
        result = await oauth_manager.handle_callback(provider, code, state)
        
        if result.success:
            # 設置JWT cookies
            response = RedirectResponse(
                url="/dashboard" if not result.is_new_user else "/welcome"
            )
            
            # 設置安全的HTTP-only cookies
            response.set_cookie(
                key="access_token",
                value=result.access_token,
                max_age=15 * 60,  # 15分鐘
                httponly=True,
                secure=True,
                samesite="lax"
            )
            
            response.set_cookie(
                key="refresh_token", 
                value=result.refresh_token,
                max_age=7 * 24 * 60 * 60,  # 7天
                httponly=True,
                secure=True,
                samesite="lax"
            )
            
            return response
        else:
            return RedirectResponse(
                url=f"/login?error={urllib.parse.quote(result.error)}"
            )
            
    except Exception as e:
        return RedirectResponse(
            url=f"/login?error={urllib.parse.quote(str(e))}"
        )

@app.post("/auth/unlink/{provider}")
async def unlink_oauth_account(
    provider: OAuthProvider,
    current_user: dict = Depends()  # 從JWT獲取
):
    """解除OAuth帳號綁定"""
    try:
        from src.database.models import UserOAuth
        
        oauth_record = oauth_manager.db.query(UserOAuth).filter(
            UserOAuth.user_id == current_user["id"],
            UserOAuth.provider == provider.value
        ).first()
        
        if not oauth_record:
            raise HTTPException(status_code=404, detail="未找到OAuth綁定記錄")
        
        # 檢查是否為唯一登入方式
        oauth_count = oauth_manager.db.query(UserOAuth).filter(
            UserOAuth.user_id == current_user["id"]
        ).count()
        
        user_has_password = oauth_manager.db.query(User).filter(
            User.id == current_user["id"],
            User.password_hash.isnot(None)
        ).first()
        
        if oauth_count == 1 and not user_has_password:
            raise HTTPException(
                status_code=400,
                detail="無法解除綁定，這是您唯一的登入方式。請先設置密碼。"
            )
        
        oauth_manager.db.delete(oauth_record)
        oauth_manager.db.commit()
        
        return {"success": True, "message": "OAuth帳號綁定已解除"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ================================
# 安全建議和最佳實踐
# ================================

"""
安全最佳實踐：

1. State參數驗證
   - 每次OAuth流程都生成唯一state
   - 在Redis中存儲state並設置過期時間
   - 回調時驗證state並立即刪除

2. Token安全
   - JWT使用強密鑰簽名
   - Access token短期有效（15分鐘）
   - Refresh token相對長期（7天）
   - 使用HTTP-only cookies存儲

3. 用戶資料驗證
   - 驗證OAuth提供商返回的email
   - 檢查用戶資料完整性
   - 處理重複email的情況

4. 錯誤處理
   - 不暴露敏感錯誤信息
   - 記錄安全相關事件
   - 提供用戶友好的錯誤頁面

5. HTTPS強制
   - 所有OAuth端點必須使用HTTPS
   - redirect_uri必須使用HTTPS
   - 設置Secure cookie標誌

6. 速率限制
   - 對OAuth端點實施速率限制
   - 防止暴力破解和濫用
   - 監控異常活動

配置檢查清單：
□ 獲取OAuth應用憑證
□ 配置正確的redirect URI
□ 設置適當的權限範圍
□ 配置安全的JWT密鑰
□ 設置Redis用於state存儲
□ 配置HTTPS證書
□ 測試完整的OAuth流程
□ 監控和日誌記錄
"""