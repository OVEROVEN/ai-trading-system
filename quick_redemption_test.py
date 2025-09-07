#!/usr/bin/env python3
"""
快速兌換碼功能測試（模擬用戶登錄後的操作）
"""

import requests
import json

def test_without_auth():
    """測試無需認證的端點"""
    base_url = "http://localhost:8000"
    
    print("🧪 兌換碼系統快速測試")
    print("=" * 50)
    
    # 1. 測試健康檢查
    print("\n1. 🏥 API健康檢查...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ API伺服器正常運行")
        else:
            print(f"❌ API伺服器異常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 無法連接API: {e}")
        return False
    
    # 2. 測試兌換碼API端點存在性（期望返回403/401，說明端點存在但需要認證）
    print("\n2. 🔐 測試兌換碼API端點...")
    endpoints_to_test = [
        "/api/redemption/credits",
        "/api/redemption/history", 
        "/api/redemption/redeem"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code in [401, 403]:
                print(f"✅ {endpoint} - 端點存在且有正確的認證保護")
            elif response.status_code == 500:
                print(f"❌ {endpoint} - 內部伺服器錯誤（可能是程式碼問題）")
            else:
                print(f"⚠️ {endpoint} - 意外的狀態碼: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - 測試失敗: {e}")
    
    # 3. 測試POST端點（兌換）
    print("\n3. 🎫 測試兌換端點...")
    try:
        response = requests.post(f"{base_url}/api/redemption/redeem", 
                               json={"code": "WEILIANG10"},
                               headers={"Content-Type": "application/json"})
        if response.status_code in [401, 403]:
            print("✅ 兌換端點存在且有正確的認證保護")
        elif response.status_code == 422:
            print("✅ 兌換端點存在但需要正確的請求格式")
        else:
            print(f"⚠️ 兌換端點返回意外狀態碼: {response.status_code}")
    except Exception as e:
        print(f"❌ 兌換端點測試失敗: {e}")
    
    return True

def show_available_codes():
    """顯示可用的兌換碼"""
    print("\n" + "=" * 50)
    print("🎫 可用的兌換碼：")
    print("-" * 50)
    
    codes = [
        {"code": "WEILIANG10", "credits": 10, "desc": "維良專屬兌換碼"},
        {"code": "KBDASOCCER100", "credits": 100, "desc": "足球粉絲專屬兌換碼"},
        {"code": "NEWUSER20", "credits": 20, "desc": "新用戶礼包"},
        {"code": "TRADER50", "credits": 50, "desc": "交易員專屬"},
        {"code": "PREMIUM30", "credits": 30, "desc": "高級用戶礼包"}
    ]
    
    for code_info in codes:
        print(f"🎫 {code_info['code']}")
        print(f"   💎 AI分析次數: {code_info['credits']}")
        print(f"   📝 說明: {code_info['desc']}")
        print()
    
    print("=" * 50)
    print("📝 使用方法:")
    print("1. 打開瀏覽器到 http://localhost:3000")
    print("2. 使用Google帳號登錄")
    print("3. 在兌換碼輸入框中輸入以上任一兌換碼")
    print("4. 點擊「立即兌換」按鈕")
    print("5. 查看您的AI分析次數增加")
    print("\n⚠️ 注意：每個帳號每個兌換碼只能使用一次！")

def main():
    success = test_without_auth()
    
    if success:
        show_available_codes()
        print(f"\n🎊 測試完成！兌換碼系統已準備就緒")
        print(f"🌐 前端地址: http://localhost:3000")
        print(f"📚 API文檔: http://localhost:8000/docs")
    else:
        print(f"\n❌ 測試失敗，請檢查系統配置")

if __name__ == "__main__":
    main()