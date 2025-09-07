#!/usr/bin/env python3
"""
創建符合長度要求的兌換碼並測試
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import datetime, timedelta
from src.database.connection import get_db
from src.database.redemption_models import RedemptionCode

def create_valid_redemption_codes():
    """創建符合12-14字符長度要求的兌換碼"""
    print("🎫 創建符合長度要求的兌換碼")
    print("=" * 40)
    
    # 新的兌換碼（12-14字符）
    new_codes = [
        {"code": "WEILIANG100X", "credits": 10, "desc": "維良專屬兌換碼（修正版）"},  # 12字符
        {"code": "SOCCER100FANS", "credits": 100, "desc": "足球粉絲專屬兌換碼"},      # 13字符
        {"code": "NEWUSER20TEST", "credits": 20, "desc": "新用戶礼包"},            # 13字符
        {"code": "TRADER50BONUS", "credits": 50, "desc": "交易員專屬"},            # 13字符
        {"code": "PREMIUM30GOLD", "credits": 30, "desc": "高級用戶礼包"}             # 13字符
    ]
    
    try:
        with get_db() as db:
            print(f"📋 準備創建 {len(new_codes)} 個新兌換碼...")
            
            for code_info in new_codes:
                code_length = len(code_info["code"])
                print(f"\n🎫 處理兌換碼: {code_info['code']} ({code_length} 字符)")
                
                if code_length < 12 or code_length > 14:
                    print(f"❌ 跳過 - 長度不符合要求 (需要12-14字符)")
                    continue
                
                # 檢查兌換碼是否已存在
                existing = db.query(RedemptionCode).filter(
                    RedemptionCode.code == code_info["code"]
                ).first()
                
                if existing:
                    print(f"📧 兌換碼已存在")
                    print(f"   狀態: {'可用' if existing.is_active and not existing.is_used else '已使用'}")
                else:
                    # 創建新兌換碼
                    new_code = RedemptionCode(
                        code=code_info["code"],
                        credits=code_info["credits"],
                        description=code_info["desc"],
                        expires_at=datetime.utcnow() + timedelta(days=365),
                        is_active=True,
                        is_used=False
                    )
                    db.add(new_code)
                    print(f"✅ 創建新兌換碼")
                    print(f"   可獲得次數: {code_info['credits']}")
                    print(f"   描述: {code_info['desc']}")
            
            db.commit()
            
            print(f"\n📊 兌換碼創建完成！")
            
            # 顯示所有可用的兌換碼
            print(f"\n🎫 所有可用的兌換碼:")
            print("=" * 50)
            
            available_codes = db.query(RedemptionCode).filter(
                RedemptionCode.is_active == True,
                RedemptionCode.is_used == False
            ).all()
            
            for code in available_codes:
                code_length = len(code.code)
                status = "✅ 符合長度" if 12 <= code_length <= 14 else "❌ 長度不符"
                print(f"🎫 {code.code} ({code_length} 字符) - {code.credits} 次 - {status}")
                print(f"   {code.description}")
                print()
            
            return True
            
    except Exception as e:
        print(f"❌ 創建兌換碼失敗: {e}")
        return False

def test_valid_code():
    """測試符合長度要求的兌換碼"""
    print(f"\n🧪 測試符合要求的兌換碼")
    print("=" * 30)
    
    # 使用第一個符合要求的兌換碼
    test_code = "WEILIANG100X"  # 12字符
    
    print(f"🎯 測試兌換碼: {test_code}")
    print(f"📏 長度: {len(test_code)} 字符")
    print(f"✅ 符合要求: {'是' if 12 <= len(test_code) <= 14 else '否'}")
    
    print(f"\n📋 使用此兌換碼進行測試:")
    print(f"1. 打開瀏覽器到 http://localhost:3000")
    print(f"2. 按 F12 打開開發者工具")
    print(f"3. 在 Console 中執行:")
    print(f"   localStorage.setItem('auth_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDIzYWZlMDEtYWU1ZS00N2NjLTllZGQtYjBhY2ZmZDIyNTg2IiwiZW1haWwiOiJ0ZXN0dXNlckBleGFtcGxlLmNvbSIsInN1YnNjcmlwdGlvbl9zdGF0dXMiOiJmcmVlIiwiZXhwIjoxNzU2ODAwNjk2LCJpYXQiOjE3NTY3MTQyOTZ9.92Dv8HJo3j_DgD-vgXpduGQa65fNn3FJ0XGYWKWJWKA');")
    print(f"4. 重新載入頁面 (F5)")
    print(f"5. 輸入兌換碼: {test_code}")
    print(f"6. 點擊「立即兌換」")
    
    return test_code

def main():
    print("🎫 兌換碼長度修正工具")
    print("=" * 40)
    
    # 創建符合要求的兌換碼
    success = create_valid_redemption_codes()
    
    if success:
        # 提供測試兌換碼
        test_code = test_valid_code()
        
        print(f"\n🎊 修正完成！")
        print(f"現在您可以使用 {test_code} 來測試兌換功能了！")
    else:
        print(f"❌ 修正失敗")

if __name__ == "__main__":
    main()