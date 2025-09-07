#!/usr/bin/env python3
"""
創建有效的 JWT token 用於測試
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import jwt
from datetime import datetime, timedelta
import uuid

# JWT 設定（應該與後端一致）
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

def create_jwt_token():
    """創建有效的 JWT token"""
    print("🔑 創建測試 JWT Token")
    print("=" * 30)
    
    # 從設定中獲取密鑰（需要匹配後端）
    try:
        from config.settings import settings
        jwt_secret = settings.jwt_secret_key
        print(f"✅ 使用系統 JWT 密鑰")
    except Exception as e:
        # 如果無法獲取系統密鑰，使用默認值
        jwt_secret = "your-secret-key-here-change-this-in-production"
        print(f"⚠️ 使用預設 JWT 密鑰: {e}")
    
    # 測試用戶資料（從之前創建的測試用戶）
    user_id = "023afe01-ae5e-47cc-9edd-b0acffd22586"
    email = "testuser@example.com"
    
    # 創建 JWT payload
    payload = {
        "user_id": user_id,
        "email": email,
        "subscription_status": "free",
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
        "iat": datetime.utcnow()
    }
    
    # 生成 JWT token
    try:
        token = jwt.encode(payload, jwt_secret, algorithm=ALGORITHM)
        
        print(f"✅ JWT Token 生成成功")
        print(f"📝 用戶 ID: {user_id}")
        print(f"📧 電子郵件: {email}")
        print(f"⏰ 過期時間: {payload['exp']}")
        print(f"🔑 Token (前50字符): {token[:50]}...")
        print(f"\n完整 Token:")
        print(token)
        
        # 驗證 token 是否有效
        try:
            decoded = jwt.decode(token, jwt_secret, algorithms=[ALGORITHM])
            print(f"\n✅ Token 驗證成功")
            print(f"📋 解碼內容: {decoded}")
        except Exception as e:
            print(f"❌ Token 驗證失敗: {e}")
        
        return token
        
    except Exception as e:
        print(f"❌ 創建 JWT Token 失敗: {e}")
        return None

def create_test_script(token):
    """創建測試腳本"""
    if not token:
        return
    
    print(f"\n📝 創建瀏覽器測試腳本")
    print("=" * 30)
    
    script_content = f"""
// 在瀏覽器開發者工具 Console 中執行以下代碼

// 1. 設置 JWT Token
localStorage.setItem('auth_token', '{token}');
console.log('✅ JWT Token 已設置');

// 2. 重新載入頁面
location.reload();

// 3. 檢查認證狀態
setTimeout(() => {{
    console.log('🔍 檢查認證狀態...');
    console.log('Token:', localStorage.getItem('auth_token'));
    
    // 測試 API 調用
    fetch('http://localhost:8000/api/redemption/credits', {{
        headers: {{
            'Authorization': 'Bearer ' + localStorage.getItem('auth_token'),
            'Content-Type': 'application/json'
        }}
    }})
    .then(response => {{
        console.log('📡 API 響應狀態:', response.status);
        return response.json();
    }})
    .then(data => {{
        console.log('📊 用戶配額:', data);
    }})
    .catch(error => {{
        console.error('❌ API 錯誤:', error);
    }});
}}, 2000);
"""
    
    # 儲存腳本到文件
    with open('browser_test_script.js', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ 測試腳本已儲存到: browser_test_script.js")
    
    print(f"\n📋 使用步驟:")
    print(f"1. 打開瀏覽器到 http://localhost:3000")
    print(f"2. 按 F12 打開開發者工具")
    print(f"3. 切換到 Console 標籤")
    print(f"4. 複製貼上以下代碼並執行:")
    print(f"   localStorage.setItem('auth_token', '{token}');")
    print(f"5. 重新載入頁面 (F5)")
    print(f"6. 嘗試兌換碼: WEILIANG10")

def main():
    print("🧪 JWT Token 測試工具")
    print("=" * 30)
    
    # 創建 JWT token
    token = create_jwt_token()
    
    if token:
        # 創建測試腳本
        create_test_script(token)
        
        print(f"\n🎊 JWT Token 創建完成！")
        print(f"現在可以在瀏覽器中測試兌換碼功能了。")
    else:
        print(f"❌ JWT Token 創建失敗")

if __name__ == "__main__":
    main()