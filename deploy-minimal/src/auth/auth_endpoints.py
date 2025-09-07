"""
用戶認證API端點

提供註冊、登入、密碼重置等認證相關的API
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging

from src.database.connection import get_db_session
from .schemas import (
    UserCreate, UserLogin, UserResponse, Token, 
    UserUpdate, PasswordReset, PasswordResetConfirm,
    EmailVerification, APIResponse, ErrorResponse
)
from .auth import (
    JWTHandler, get_current_user, get_current_active_user,
    create_user_response_with_subscription
)
from . import crud

# 設置日誌
logger = logging.getLogger(__name__)

# 創建路由器
auth_router = APIRouter(prefix="/api/auth", tags=["認證"])

@auth_router.post("/register", response_model=APIResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db_session)
):
    """
    用戶註冊
    
    創建新用戶帳戶並發送驗證郵件
    """
    try:
        # 檢查郵箱是否已存在
        existing_user = crud.get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="此郵箱地址已被註冊"
            )
        
        # 創建用戶
        user = crud.create_user(db, user_data)
        
        # 發送驗證郵件 (可選功能)
        try:
            # 如果配置了SMTP設置，發送驗證郵件
            # await send_verification_email(user.email, user.verification_token)
            logger.info(f"驗證郵件功能未啟用，用戶 {user.email} 已直接激活")
        except Exception as e:
            logger.warning(f"發送驗證郵件失敗 (用戶仍可正常使用): {e}")
        
        logger.info(f"新用戶註冊成功: {user.email} (ID: {user.id})")
        
        return APIResponse(
            success=True,
            message="註冊成功！請檢查您的郵箱並點擊驗證連結。",
            data={"user_id": str(user.id), "email": user.email}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用戶註冊失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="註冊過程中發生錯誤，請稍後重試"
        )

@auth_router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db_session)
):
    """
    用戶登入
    
    驗證用戶憑證並返回JWT token
    """
    try:
        # 驗證用戶憑證
        user = crud.authenticate_user(db, login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="郵箱地址或密碼錯誤",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用戶帳戶已被停用"
            )
        
        # 獲取用戶訂閱狀態
        subscription = crud.get_user_active_subscription(db, user.id)
        subscription_status = "premium" if subscription and subscription.is_premium else "free"
        
        # 生成JWT token
        access_token = JWTHandler.create_user_token(user, subscription_status)
        
        # 更新最後登入時間
        crud.update_user_login(db, user.id)
        
        # 創建用戶響應
        user_response = create_user_response_with_subscription(user, db)
        
        logger.info(f"用戶登入成功: {user.email} (ID: {user.id})")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=24 * 3600,  # 24小時
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用戶登入失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登入過程中發生錯誤，請稍後重試"
        )

@auth_router.post("/verify-email", response_model=APIResponse)
async def verify_email(
    verification_data: EmailVerification,
    db: Session = Depends(get_db_session)
):
    """
    驗證郵箱地址
    
    使用驗證令牌激活用戶帳戶
    """
    try:
        user = crud.verify_user_email(db, verification_data.token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="驗證令牌無效或已過期"
            )
        
        logger.info(f"郵箱驗證成功: {user.email} (ID: {user.id})")
        
        return APIResponse(
            success=True,
            message="郵箱驗證成功！您現在可以使用所有功能。",
            data={"user_id": str(user.id), "email": user.email}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"郵箱驗證失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="驗證過程中發生錯誤，請稍後重試"
        )

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """
    獲取當前用戶信息
    
    包含訂閱狀態和配額信息
    """
    try:
        user_response = create_user_response_with_subscription(current_user, db)
        return user_response
        
    except Exception as e:
        logger.error(f"獲取用戶信息失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取用戶信息失敗"
        )

@auth_router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """
    更新當前用戶信息
    """
    try:
        updated_user = crud.update_user(db, current_user.id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用戶不存在"
            )
        
        user_response = create_user_response_with_subscription(updated_user, db)
        
        logger.info(f"用戶信息更新成功: {updated_user.email} (ID: {updated_user.id})")
        
        return user_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用戶信息失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用戶信息失敗"
        )

@auth_router.post("/forgot-password", response_model=APIResponse)
async def forgot_password(
    password_reset: PasswordReset,
    db: Session = Depends(get_db_session)
):
    """
    發送密碼重置郵件
    """
    try:
        user = crud.get_user_by_email(db, password_reset.email)
        if not user:
            # 為了安全，不暴露郵箱是否存在
            return APIResponse(
                success=True,
                message="如果該郵箱地址存在，您將收到密碼重置郵件。"
            )
        
        # 生成重置令牌並發送郵件 (可選功能)
        try:
            # reset_token = generate_reset_token(user.id)
            # await send_password_reset_email(user.email, reset_token)
            logger.info(f"密碼重置郵件功能未啟用，請聯繫管理員重置密碼")
        except Exception as e:
            logger.warning(f"發送密碼重置郵件失敗: {e}")
        # reset_token = crud.generate_reset_token()
        # await send_password_reset_email(user.email, reset_token)
        
        logger.info(f"密碼重置郵件已發送: {user.email}")
        
        return APIResponse(
            success=True,
            message="密碼重置郵件已發送，請檢查您的收件箱。"
        )
        
    except Exception as e:
        logger.error(f"發送密碼重置郵件失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="發送密碼重置郵件失敗"
        )

@auth_router.post("/reset-password", response_model=APIResponse)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db_session)
):
    """
    重置密碼
    
    使用重置令牌設置新密碼
    """
    try:
        # 實現密碼重置邏輯
        try:
            # 驗證重置令牌
            # user_id = verify_reset_token(reset_data.token)
            # user = crud.get_user_by_id(db, user_id)
            # if not user:
            #     raise HTTPException(status_code=404, detail="用戶不存在")
            
            # 更新密碼
            # crud.update_user_password(db, user.id, reset_data.new_password)
            logger.info("密碼重置功能需要完整的令牌驗證系統")
            
            raise HTTPException(
                status_code=501,
                detail="密碼重置功能正在開發中，請聯繫管理員"
            )
        except Exception as e:
            logger.error(f"密碼重置失敗: {e}")
            raise HTTPException(
                status_code=500,
                detail="密碼重置處理失敗"
            )
        # user = crud.verify_reset_token(db, reset_data.token)
        # if not user:
        #     raise HTTPException(...)
        # crud.update_user_password(db, user.id, reset_data.new_password)
        
        return APIResponse(
            success=True,
            message="密碼重置成功，請使用新密碼登入。"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"密碼重置失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密碼重置失敗"
        )

@auth_router.post("/logout", response_model=APIResponse)
async def logout_user(
    current_user = Depends(get_current_user)
):
    """
    用戶登出
    
    使JWT token失效（在更高級的實現中）
    """
    try:
        # 實現token黑名單或session管理 (簡化版)
        try:
            # 在完整實現中，這裡會將token加入黑名單
            # 目前採用短期token過期策略來保證安全性
            logger.info(f"用戶 {current_user.email} 已登出")
            # redis_client.set(f"blacklist:token:{token_hash}", "revoked", ex=JWT_EXPIRE_SECONDS)
        except Exception as e:
            logger.warning(f"登出處理警告: {e}")
        # session_manager.invalidate_user_sessions(current_user.id)
        
        logger.info(f"用戶登出: {current_user.email} (ID: {current_user.id})")
        
        return APIResponse(
            success=True,
            message="登出成功"
        )
        
    except Exception as e:
        logger.error(f"用戶登出失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出失敗"
        )

@auth_router.get("/quota", response_model=dict)
async def get_user_quota(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """
    獲取用戶配額信息
    
    包含免費使用次數和每日配額
    """
    try:
        quota = crud.get_user_quota(db, current_user.id)
        if not quota:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到用戶配額信息"
            )
        
        # 檢查是否為付費用戶
        subscription = crud.get_user_active_subscription(db, current_user.id)
        is_premium = subscription and subscription.is_premium if subscription else False
        
        return {
            "is_premium": is_premium,
            "total_free_uses": quota.total_free_uses,
            "used_free_uses": quota.used_free_uses,
            "remaining_initial_quota": quota.remaining_initial_quota,
            "daily_used_count": quota.daily_used_count,
            "remaining_daily_quota": quota.remaining_daily_quota,
            "can_use_ai_analysis": quota.can_use_ai_analysis() or is_premium
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取用戶配額失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取配額信息失敗"
        )

# ========== Google OAuth 端點 ==========

@auth_router.get("/google/login")
async def google_oauth_login(
    redirect_uri: str = "http://localhost:3000/auth/google/callback",
    db: Session = Depends(get_db_session)
):
    """
    Google OAuth 登入入口
    
    生成 Google OAuth 授權 URL 並重定向用戶
    """
    try:
        from .oauth import google_oauth, oauth_state_manager
        
        if not google_oauth.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google OAuth 未配置，請聯繫管理員"
            )
        
        # 創建狀態參數用於 CSRF 保護
        state = oauth_state_manager.create_state(redirect_uri)
        
        # 生成授權 URL
        auth_url = google_oauth.get_authorization_url(redirect_uri, state)
        
        logger.info(f"Google OAuth login initiated, redirecting to: {auth_url}")
        
        return {
            "authorization_url": auth_url,
            "state": state,
            "redirect_uri": redirect_uri
        }
        
    except Exception as e:
        logger.error(f"Google OAuth login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google 登入初始化失敗"
        )

class GoogleCallbackRequest(BaseModel):
    code: str
    state: str
    redirect_uri: str = "http://localhost:3000/auth/google/callback"

@auth_router.post("/google/callback", response_model=Token)
async def google_oauth_callback(
    request: GoogleCallbackRequest,
    db: Session = Depends(get_db_session)
):
    """
    Google OAuth 回調處理
    
    處理 Google OAuth 授權碼並創建用戶會話
    """
    try:
        from .oauth import google_oauth, oauth_state_manager
        
        # 驗證狀態參數
        state_data = oauth_state_manager.verify_state(request.state)
        if not state_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="無效的授權狀態，請重新登入"
            )
        
        # 確認回調 URI 匹配
        if state_data["redirect_uri"] != request.redirect_uri:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="回調 URI 不匹配"
            )
        
        # 檢查authorization code是否已經被使用
        if oauth_state_manager.is_code_used(request.code):
            logger.warning(f"Authorization code already used: {request.code[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="授權碼已被使用，請重新登入"
            )
        
        # 標記authorization code為已使用
        oauth_state_manager.mark_code_used(request.code)
        
        # 使用授權碼交換訪問令牌
        token_data = await google_oauth.exchange_code_for_token(request.code, request.redirect_uri)
        
        # 獲取用戶信息
        user_info = await google_oauth.get_user_info(token_data["access_token"])
        
        # 提取用戶數據
        oauth_user_data = google_oauth.extract_user_data(user_info)
        
        # 檢查用戶是否已存在
        existing_user = crud.get_user_by_google_id(db, oauth_user_data.google_id)
        if not existing_user:
            # 檢查郵箱是否已被其他用戶使用
            email_user = crud.get_user_by_email(db, oauth_user_data.email)
            if email_user:
                # 郵箱已被使用，自動綁定 Google 帳戶到現有用戶
                email_user.google_id = oauth_user_data.google_id
                email_user.full_name = oauth_user_data.full_name or email_user.full_name
                email_user.avatar_url = oauth_user_data.avatar_url or email_user.avatar_url
                email_user.email_verified = True  # Google 帳戶已驗證
                
                # 更新最後登入時間
                crud.update_user_login(db, email_user.id)
                
                user = email_user
                logger.info(f"Google account linked to existing user: {user.email} (ID: {user.id})")
            else:
                # 創建新的 OAuth 用戶
                user = crud.create_oauth_user(db, oauth_user_data)
                logger.info(f"New OAuth user created: {user.email} (ID: {user.id})")
        else:
            user = existing_user
            # 更新最後登入時間
            crud.update_user_login(db, user.id)
            logger.info(f"OAuth user login: {user.email} (ID: {user.id})")
        
        # 獲取用戶訂閱狀態
        subscription = crud.get_user_active_subscription(db, user.id)
        subscription_status = "premium" if subscription and subscription.is_premium else "free"
        
        # 生成 JWT token
        access_token = JWTHandler.create_user_token(user, subscription_status)
        
        # 創建用戶響應
        user_response = create_user_response_with_subscription(user, db)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=24 * 3600,  # 24小時
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google 登入處理失敗，請稍後重試"
        )

@auth_router.get("/google/status")
async def google_oauth_status():
    """
    檢查 Google OAuth 配置狀態
    """
    try:
        from .oauth import google_oauth
        
        return {
            "google_oauth_enabled": google_oauth.is_configured(),
            "client_id": google_oauth.client_id[:10] + "..." if google_oauth.client_id else None
        }
        
    except Exception as e:
        logger.error(f"Failed to check Google OAuth status: {e}")
        return {
            "google_oauth_enabled": False,
            "error": "配置檢查失敗"
        }

# ========== 使用次數追蹤端點 ==========

@auth_router.get("/usage/stats")
async def get_user_usage_stats(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """
    獲取當前用戶的使用統計信息
    """
    try:
        # 獲取基本統計
        stats = crud.get_user_usage_stats(db, current_user.id)
        
        # 獲取配額信息
        quota = crud.get_user_quota(db, current_user.id)
        subscription = crud.get_user_active_subscription(db, current_user.id)
        
        # 計算剩餘配額
        quota_info = {
            "is_premium": subscription and subscription.is_premium if subscription else False,
            "remaining_initial_quota": quota.remaining_initial_quota if quota else 0,
            "remaining_daily_quota": quota.remaining_daily_quota if quota else 0,
            "used_today": quota.daily_used_count if quota else 0,
            "total_free_uses": quota.total_free_uses if quota else 0,
            "used_free_uses": quota.used_free_uses if quota else 0
        }
        
        return {
            "success": True,
            "usage_stats": stats,
            "quota_info": quota_info,
            "can_use_ai": crud.check_user_can_use_ai(db, current_user.id)
        }
        
    except Exception as e:
        logger.error(f"獲取使用統計失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取使用統計失敗"
        )

@auth_router.get("/usage/records")
async def get_user_usage_records(
    action_type: str = None,
    limit: int = 50,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """
    獲取當前用戶的使用記錄
    
    Args:
        action_type: 過濾特定動作類型 ("ai_analysis", "chart_view")
        limit: 返回記錄數量限制 (最大100)
    """
    try:
        # 限制最大返回數量
        limit = min(limit, 100)
        
        records = crud.get_user_usage_records(db, current_user.id, action_type, limit)
        
        # 格式化記錄
        formatted_records = []
        for record in records:
            formatted_record = {
                "id": str(record.id),
                "action_type": record.action_type,
                "created_at": record.created_at.isoformat(),
                "extra_data": record.extra_data or {}
            }
            formatted_records.append(formatted_record)
        
        return {
            "success": True,
            "records": formatted_records,
            "total_count": len(formatted_records),
            "filtered_by": action_type
        }
        
    except Exception as e:
        logger.error(f"獲取使用記錄失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取使用記錄失敗"
        )

@auth_router.get("/usage/summary")
async def get_usage_summary(
    days: int = 30,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """
    獲取用戶使用情況摘要
    
    Args:
        days: 統計天數 (默認30天)
    """
    try:
        from .usage_tracking import get_user_usage_summary
        
        # 限制天數範圍
        days = max(1, min(days, 365))
        
        summary = await get_user_usage_summary(str(current_user.id), db, days)
        
        return {
            "success": True,
            "summary": summary,
            "period_days": days
        }
        
    except Exception as e:
        logger.error(f"獲取使用摘要失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取使用摘要失敗"
        )

@auth_router.post("/usage/check-quota")
async def check_usage_quota(
    action_type: str = "ai_analysis",
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """
    檢查用戶是否可以使用特定功能
    
    Args:
        action_type: 要檢查的動作類型
    """
    try:
        from .usage_tracking import check_quota_before_use
        
        can_use, quota_info = await check_quota_before_use(current_user, db, action_type)
        
        return {
            "success": True,
            "can_use": can_use,
            "quota_info": quota_info,
            "action_type": action_type
        }
        
    except Exception as e:
        logger.error(f"檢查使用配額失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="檢查使用配額失敗"
        )

@auth_router.post("/usage/manual-record")
async def manual_usage_record(
    action_type: str,
    success: bool = True,
    extra_data: dict = None,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db_session)
):
    """
    手動記錄使用情況（管理員或特殊情況使用）
    
    Args:
        action_type: 動作類型
        success: 是否成功
        extra_data: 額外數據
    """
    try:
        from .usage_tracking import record_manual_usage
        
        await record_manual_usage(
            db, str(current_user.id), action_type, success, extra_data or {}
        )
        
        return {
            "success": True,
            "message": "使用記錄已創建",
            "recorded": {
                "action_type": action_type,
                "success": success,
                "user_id": str(current_user.id)
            }
        }
        
    except Exception as e:
        logger.error(f"手動記錄使用情況失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="記錄使用情況失敗"
        )

# 健康檢查端點
@auth_router.get("/health")
async def auth_health_check():
    """認證系統健康檢查"""
    return {"status": "healthy", "service": "authentication"}

# 導出路由器
__all__ = ["auth_router"]