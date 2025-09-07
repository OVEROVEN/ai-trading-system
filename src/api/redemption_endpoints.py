"""
兌換碼系統API端點
"""
from fastapi import APIRouter, Depends, HTTPException, status
import logging

logger = logging.getLogger(__name__)
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from ..database.connection import get_db_session
from ..database.redemption_models import RedemptionCode, RedemptionHistory
from ..auth.models import User, FreeQuota
from ..auth.auth import get_current_user

router = APIRouter(prefix="/api/redemption", tags=["兌換碼系統"])

# Pydantic 模型
class RedeemCodeRequest(BaseModel):
    code: str = Field(..., description="兌換碼")

class RedeemCodeResponse(BaseModel):
    success: bool = Field(..., description="兌換是否成功")
    message: str = Field(..., description="兌換結果訊息")
    credits_added: Optional[int] = Field(None, description="增加的AI分析次數")
    total_credits: Optional[int] = Field(None, description="總剩餘次數")

class CreateCodeRequest(BaseModel):
    credits: int = Field(10, description="兌換次數", ge=1, le=1000)
    expires_days: Optional[int] = Field(30, description="有效天數", ge=1, le=365)
    description: Optional[str] = Field(None, description="兌換碼說明")
    batch_count: int = Field(1, description="生成數量", ge=1, le=100)

class CodeInfo(BaseModel):
    id: int
    code: str
    credits: int
    description: Optional[str]
    is_active: bool
    is_used: bool
    created_at: datetime
    expires_at: Optional[datetime]
    used_at: Optional[datetime]
    used_by_email: Optional[str] = None

class RedemptionHistoryItem(BaseModel):
    code: str
    credits_added: int
    redeemed_at: datetime
    description: Optional[str]

# API 端點
@router.post("/redeem", response_model=RedeemCodeResponse)
async def redeem_code(
    request: RedeemCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """兌換兌換碼"""
    try:
        # 清理兌換碼格式
        code = request.code.upper().strip()
        
        # 查找兌換碼
        redemption_code = db.query(RedemptionCode).filter(
            RedemptionCode.code == code,
            RedemptionCode.is_active == True
        ).first()
        
        if not redemption_code:
            return RedeemCodeResponse(
                success=False,
                message="兌換碼不存在或已失效"
            )
        
        # 檢查是否已使用
        if redemption_code.is_used:
            return RedeemCodeResponse(
                success=False,
                message="兌換碼已被使用"
            )
        
        # 檢查是否過期
        if redemption_code.expires_at and redemption_code.expires_at < datetime.utcnow():
            return RedeemCodeResponse(
                success=False,
                message="兌換碼已過期"
            )
        
        # 檢查用戶是否已經使用過這個兌換碼
        existing_history = db.query(RedemptionHistory).filter(
            RedemptionHistory.user_id == current_user.id,
            RedemptionHistory.code_id == redemption_code.id
        ).first()
        
        if existing_history:
            return RedeemCodeResponse(
                success=False,
                message="您已經使用過這個兌換碼"
            )
        
        # 獲取用戶配額
        user_quota = db.query(FreeQuota).filter(
            FreeQuota.user_id == current_user.id
        ).first()
        
        if not user_quota:
            # 創建用戶配額記錄
            user_quota = FreeQuota(user_id=current_user.id)
            db.add(user_quota)
            db.flush()
        
        # 添加兌換次數
        user_quota.add_bonus_credits(redemption_code.credits)
        
        # 標記兌換碼為已使用
        redemption_code.is_used = True
        redemption_code.used_by_user_id = str(current_user.id)
        redemption_code.used_at = datetime.utcnow()
        
        # 記錄兌換歷史
        history = RedemptionHistory(
            user_id=str(current_user.id),
            code_id=redemption_code.id,
            credits_added=redemption_code.credits
        )
        db.add(history)
        
        db.commit()
        
        return RedeemCodeResponse(
            success=True,
            message=f"兌換成功！獲得 {redemption_code.credits} 次AI分析",
            credits_added=redemption_code.credits,
            total_credits=user_quota.total_remaining_quota
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Redemption failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"兌換過程中發生錯誤：{str(e)}"
        )

@router.get("/history", response_model=List[RedemptionHistoryItem])
async def get_redemption_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """獲取用戶兌換歷史"""
    history = db.query(RedemptionHistory).filter(
        RedemptionHistory.user_id == current_user.id
    ).order_by(RedemptionHistory.redeemed_at.desc()).all()
    
    result = []
    for item in history:
        result.append(RedemptionHistoryItem(
            code=item.redemption_code.code,
            credits_added=item.credits_added,
            redeemed_at=item.redeemed_at,
            description=item.redemption_code.description
        ))
    
    return result

@router.get("/credits")
async def get_user_credits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """獲取用戶當前AI分析次數"""
    user_quota = db.query(FreeQuota).filter(
        FreeQuota.user_id == current_user.id
    ).first()
    
    if not user_quota:
        # 創建用戶配額記錄
        user_quota = FreeQuota(user_id=current_user.id)
        db.add(user_quota)
        db.commit()
    
    return {
        "bonus_credits": user_quota.remaining_bonus_credits,
        "free_credits": user_quota.remaining_initial_quota,
        "daily_credits": user_quota.remaining_daily_quota,
        "total_credits": user_quota.total_remaining_quota,
        "can_use_ai": user_quota.can_use_ai_analysis()
    }

# 管理員功能（需要額外的權限檢查）
@router.post("/admin/create", response_model=List[CodeInfo])
async def create_redemption_codes(
    request: CreateCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """創建兌換碼（管理員功能）"""
    # TODO: 添加管理員權限檢查
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="需要管理員權限")
    
    try:
        created_codes = []
        
        for _ in range(request.batch_count):
            code = RedemptionCode.generate_code(
                credits=request.credits,
                expires_days=request.expires_days,
                description=request.description
            )
            db.add(code)
            created_codes.append(code)
        
        db.commit()
        
        result = []
        for code in created_codes:
            result.append(CodeInfo(
                id=code.id,
                code=code.code,
                credits=code.credits,
                description=code.description,
                is_active=code.is_active,
                is_used=code.is_used,
                created_at=code.created_at,
                expires_at=code.expires_at,
                used_at=code.used_at
            ))
        
        return result
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"創建兌換碼時發生錯誤：{str(e)}"
        )

@router.get("/admin/codes", response_model=List[CodeInfo])
async def list_redemption_codes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """列出所有兌換碼（管理員功能）"""
    # TODO: 添加管理員權限檢查
    
    codes = db.query(RedemptionCode).offset(skip).limit(limit).all()
    
    result = []
    for code in codes:
        user_email = None
        if code.used_by_user:
            user_email = code.used_by_user.email
            
        result.append(CodeInfo(
            id=code.id,
            code=code.code,
            credits=code.credits,
            description=code.description,
            is_active=code.is_active,
            is_used=code.is_used,
            created_at=code.created_at,
            expires_at=code.expires_at,
            used_at=code.used_at,
            used_by_email=user_email
        ))
    
    return result