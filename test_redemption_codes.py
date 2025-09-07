#!/usr/bin/env python3
"""
测试兑换码系统功能
"""

import requests
import json

def test_redemption_system():
    """测试兑换码系统的各个功能"""
    base_url = "http://localhost:8000"
    
    print("🧪 兑换码系统功能测试")
    print("=" * 50)
    
    # 1. 测试健康检查
    print("\n1. 🏥 测试API健康状态...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ API服务器正常运行")
        else:
            print(f"❌ API服务器异常: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 无法连接到API服务器: {e}")
        return
    
    # 2. 测试兑换码列表端点（无需认证的管理端点）
    print("\n2. 📋 测试兑换码列表API...")
    try:
        # 注意：在实际应用中这需要管理员认证
        print("   (需要用户登录才能访问，这里只测试端点是否存在)")
        response = requests.get(f"{base_url}/api/redemption/admin/codes")
        if response.status_code == 401 or response.status_code == 403:
            print("✅ 兑换码管理API端点存在且有正确的权限控制")
        else:
            print(f"⚠️ 意外的响应状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 兑换码列表API测试失败: {e}")
    
    # 3. 测试API文档
    print("\n3. 📚 测试API文档...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ Swagger API文档可访问")
            print("   👉 请在浏览器中访问: http://localhost:8000/docs")
        else:
            print(f"❌ API文档访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API文档测试失败: {e}")
    
    # 4. 显示已创建的兑换码
    print("\n4. 🎫 已创建的兑换码:")
    print("-" * 50)
    redemption_codes = [
        {"code": "WEILIANG10", "credits": 10, "desc": "维良专属兑换码"},
        {"code": "KBDASOCCER100", "credits": 100, "desc": "足球粉丝专属兑换码"}, 
        {"code": "NEWUSER20", "credits": 20, "desc": "新用户礼包"},
        {"code": "TRADER50", "credits": 50, "desc": "交易员专属"},
        {"code": "PREMIUM30", "credits": 30, "desc": "高级用户礼包"}
    ]
    
    for code_info in redemption_codes:
        print(f"🎫 {code_info['code']}")
        print(f"   💎 AI分析次数: {code_info['credits']}")
        print(f"   📝 描述: {code_info['desc']}")
        print()
    
    # 5. 测试前端应用
    print("5. 🌐 测试前端应用...")
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("✅ 前端应用正常运行")
            print("   👉 请在浏览器中访问: http://localhost:3000")
        else:
            print(f"⚠️ 前端应用状态异常: {response.status_code}")
    except Exception as e:
        print(f"⚠️ 前端应用可能尚未启动: {e}")
    
    print("\n" + "=" * 50)
    print("🎊 测试完成！")
    print("\n📝 使用步骤:")
    print("1. 在浏览器中打开 http://localhost:3000")
    print("2. 使用Google账号登录")
    print("3. 在兑换码输入框中输入任一兑换码:")
    print("   • WEILIANG10 (10次)")
    print("   • KBDASOCCER100 (100次)")
    print("   • NEWUSER20 (20次)")
    print("   • TRADER50 (50次)")
    print("   • PREMIUM30 (30次)")
    print("4. 点击兑换按钮")
    print("5. 查看您的AI分析次数增加")
    print("\n⚠️ 注意: 每个账号每个兑换码只能使用一次")

if __name__ == "__main__":
    test_redemption_system()