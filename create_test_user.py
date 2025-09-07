#!/usr/bin/env python3
"""
創建測試用戶並測試兌換碼系統
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import datetime, timedelta
from src.database.connection import get_db
from src.auth.models import User, FreeQuota
from src.database.redemption_models import RedemptionCode
import uuid
import hashlib

def create_test_user():
    """創建測試用戶並進行兌換碼測試"""
    print("👤 創建測試用戶並測試兌換碼系統")
    print("=" * 50)
    
    try:
        with get_db() as db:
            # 創建測試用戶
            test_user = User(
                id=str(uuid.uuid4()),
                email="testuser@example.com",
                full_name="測試用戶",
                email_verified=True,
                is_active=True,
                password_hash=hashlib.sha256("testpassword123".encode()).hexdigest()
            )
            
            # 檢查用戶是否已存在
            existing_user = db.query(User).filter(User.email == test_user.email).first()
            if existing_user:
                print(f"📧 測試用戶已存在: {existing_user.email}")
                print(f"   用戶ID: {existing_user.id}")
                test_user = existing_user
            else:
                db.add(test_user)
                db.flush()  # 獲取 ID
                print(f"✅ 創建測試用戶: {test_user.email}")
                print(f"   用戶ID: {test_user.id}")
            
            # 創建或獲取免費配額
            user_quota = db.query(FreeQuota).filter(FreeQuota.user_id == test_user.id).first()
            if not user_quota:
                user_quota = FreeQuota(user_id=test_user.id)
                db.add(user_quota)
                db.flush()
                print(f"✅ 創建免費配額")
            else:
                print(f"📊 現有配額狀態:")
            
            print(f"   兌換碼次數: {user_quota.remaining_bonus_credits}")
            print(f"   初始免費次數: {user_quota.remaining_initial_quota}")
            print(f"   每日免費次數: {user_quota.remaining_daily_quota}")
            print(f"   總剩餘次數: {user_quota.total_remaining_quota}")
            
            # 確保兌換碼存在
            print(f"\n🎫 檢查測試兌換碼...")
            test_code = "WEILIANG10"
            redemption_code = db.query(RedemptionCode).filter(
                RedemptionCode.code == test_code
            ).first()
            
            if not redemption_code:
                # 創建兌換碼
                redemption_code = RedemptionCode(
                    code=test_code,
                    credits=10,
                    description="測試兌換碼 - 維良專屬",
                    expires_at=datetime.utcnow() + timedelta(days=365),
                    is_active=True,
                    is_used=False
                )
                db.add(redemption_code)
                print(f"✅ 創建測試兌換碼: {test_code}")
            else:
                print(f"📧 兌換碼已存在: {test_code}")
            
            print(f"   兌換碼狀態: {'可用' if redemption_code.is_active and not redemption_code.is_used else '不可用'}")
            print(f"   可獲得次數: {redemption_code.credits}")
            print(f"   到期時間: {redemption_code.expires_at}")
            
            db.commit()
            
            print(f"\n🔐 測試用戶認證信息:")
            print(f"   Email: {test_user.email}")
            print(f"   Password: testpassword123")
            print(f"   User ID: {test_user.id}")
            
            return test_user.id
            
    except Exception as e:
        print(f"❌ 創建測試用戶失敗: {e}")
        return None

def simulate_redemption_process(user_id):
    """模擬兌換碼兌換流程"""
    print(f"\n🎯 模擬兌換碼兌換流程")
    print("=" * 30)
    
    try:
        with get_db() as db:
            # 獲取用戶和配額
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                print("❌ 找不到測試用戶")
                return False
                
            user_quota = db.query(FreeQuota).filter(FreeQuota.user_id == user_id).first()
            if not user_quota:
                print("❌ 找不到用戶配額")
                return False
            
            print(f"👤 用戶: {user.full_name} ({user.email})")
            print(f"📊 兌換前配額: {user_quota.total_remaining_quota} 次")
            
            # 查找兌換碼
            test_code = "WEILIANG10"
            redemption_code = db.query(RedemptionCode).filter(
                RedemptionCode.code == test_code,
                RedemptionCode.is_active == True
            ).first()
            
            if not redemption_code:
                print(f"❌ 找不到可用的兌換碼: {test_code}")
                return False
            
            if redemption_code.is_used:
                print(f"❌ 兌換碼已被使用")
                return False
            
            # 模擬兌換過程
            print(f"🎫 執行兌換: {test_code}")
            
            # 添加兌換次數
            user_quota.add_bonus_credits(redemption_code.credits)
            
            # 標記兌換碼為已使用
            redemption_code.is_used = True
            redemption_code.used_by_user_id = user_id
            redemption_code.used_at = datetime.utcnow()
            
            db.commit()
            
            print(f"✅ 兌換成功!")
            print(f"📊 兌換後配額: {user_quota.total_remaining_quota} 次")
            print(f"   增加的次數: +{redemption_code.credits}")
            
            return True
            
    except Exception as e:
        print(f"❌ 兌換過程失敗: {e}")
        return False

def generate_auth_token(user_id):
    """生成測試用戶的認證 token（簡化版）"""
    print(f"\n🔑 生成測試認證 Token")
    print("=" * 30)
    
    # 這是一個簡化版本，實際應用中應該使用 JWT
    import base64
    import json
    
    token_data = {
        "user_id": str(user_id),
        "email": "testuser@example.com",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # 簡單的 base64 編碼（不安全，僅用於測試）
    token = base64.b64encode(json.dumps(token_data).encode()).decode()
    
    print(f"✅ 測試 Token 生成成功")
    print(f"📝 Token (前50字符): {token[:50]}...")
    print(f"\n💡 使用方法:")
    print(f"1. 在瀏覽器開發者工具中執行:")
    print(f"   localStorage.setItem('auth_token', '{token}');")
    print(f"2. 重新載入頁面")
    print(f"3. 嘗試兌換碼功能")
    
    return token

def main():
    """主函數"""
    print("🧪 測試用戶創建和兌換碼系統測試")
    print("=" * 50)
    
    # 創建測試用戶
    user_id = create_test_user()
    if not user_id:
        print("❌ 無法創建測試用戶，結束測試")
        return
    
    # 模擬兌換流程
    redemption_success = simulate_redemption_process(user_id)
    
    # 生成測試 token
    test_token = generate_auth_token(user_id)
    
    print(f"\n🎊 測試完成總結:")
    print(f"✅ 測試用戶創建: 成功")
    print(f"{'✅' if redemption_success else '❌'} 兌換碼測試: {'成功' if redemption_success else '失敗'}")
    print(f"✅ Token 生成: 成功")
    
    print(f"\n📋 下一步操作:")
    print(f"1. 打開瀏覽器到 http://localhost:3000")
    print(f"2. 按 F12 打開開發者工具")
    print(f"3. 在 Console 中執行:")
    print(f"   localStorage.setItem('auth_token', '{test_token}');")
    print(f"4. 重新載入頁面")
    print(f"5. 嘗試使用兌換碼: WEILIANG10")

if __name__ == "__main__":
    main()