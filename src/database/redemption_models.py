"""
兌換碼系統數據庫模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, timedelta
import secrets
import string

# Import the same base class as auth models
from src.auth.models import Base

class RedemptionCode(Base):
    """兌換碼模型"""
    __tablename__ = "redemption_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)  # 兌換碼
    credits = Column(Integer, nullable=False, default=10)  # 增加的AI分析次數
    description = Column(Text)  # 兌換碼描述
    
    # 狀態
    is_active = Column(Boolean, default=True)  # 是否啟用
    is_used = Column(Boolean, default=False)   # 是否已使用
    used_by_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # 使用者
    
    # 時間
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # 過期時間
    used_at = Column(DateTime, nullable=True)     # 使用時間
    
    # 關聯
    used_by_user = relationship("User", back_populates="redeemed_codes")

    @classmethod
    def generate_code(cls, credits: int = 10, expires_days: int = 30, description: str = None):
        """生成兌換碼"""
        # 生成12位兌換碼：4個字符 + 4個數字 + 4個字符
        code_chars = string.ascii_uppercase + string.digits
        code = ''.join(secrets.choice(code_chars) for _ in range(12))
        
        # 確保格式：XXXX-XXXX-XXXX
        formatted_code = f"{code[:4]}-{code[4:8]}-{code[8:12]}"
        
        expires_at = datetime.utcnow() + timedelta(days=expires_days) if expires_days else None
        
        return cls(
            code=formatted_code,
            credits=credits,
            description=description,
            expires_at=expires_at
        )

class RedemptionHistory(Base):
    """兌換歷史記錄"""
    __tablename__ = "redemption_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(), ForeignKey("users.id"), nullable=False)
    code_id = Column(Integer, ForeignKey("redemption_codes.id"), nullable=False)
    credits_added = Column(Integer, nullable=False)
    redeemed_at = Column(DateTime, default=datetime.utcnow)
    
    # 關聯
    user = relationship("User")
    redemption_code = relationship("RedemptionCode")