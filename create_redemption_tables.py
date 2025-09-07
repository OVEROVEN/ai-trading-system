#!/usr/bin/env python3
"""
创建兑换码数据表和初始化兑换码
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from src.database.connection import db_manager, get_db
from src.database.redemption_models import Base, RedemptionCode
from src.auth.models import FreeQuota, User
from datetime import datetime, timedelta
import secrets
import string

def create_redemption_tables():
    """创建兑换码相关数据表"""
    if not db_manager:
        print("❌ 数据库管理器未初始化")
        return False
    
    engine = db_manager.engine
    
    print("📊 创建兑换码数据表...")
    
    # 创建兑换码表
    try:
        # 删除已存在的表（如果存在）
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS redemption_history"))
            conn.execute(text("DROP TABLE IF EXISTS redemption_codes"))
            conn.commit()
        
        # 创建新表
        Base.metadata.create_all(engine)
        print("✅ 兑换码数据表创建成功！")
        
        # 同时确保 FreeQuota 表有兑换码相关字段
        with engine.connect() as conn:
            # 检查是否已有兑换码字段
            try:
                conn.execute(text("SELECT bonus_credits FROM free_quotas LIMIT 1"))
                print("✅ FreeQuota 表已有兑换码字段")
            except Exception:
                print("📝 添加兑换码字段到 FreeQuota 表...")
                try:
                    conn.execute(text("ALTER TABLE free_quotas ADD COLUMN bonus_credits INTEGER DEFAULT 0"))
                    conn.execute(text("ALTER TABLE free_quotas ADD COLUMN used_bonus_credits INTEGER DEFAULT 0"))
                    conn.commit()
                    print("✅ FreeQuota 表字段添加成功！")
                except Exception as e:
                    print(f"⚠️ 字段可能已存在: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建表时出错: {e}")
        return False

def generate_specific_codes():
    """生成具体的兑换码"""
    if not db_manager:
        print("❌ 数据库管理器未初始化")
        return False
    
    session = db_manager.get_session_sync()
    
    print("\n🎫 生成具体兑换码...")
    
    # 定义兑换码
    codes_to_create = [
        {
            "code": "WEILIANG10",
            "credits": 10,
            "description": "维良专属兑换码 - 10次AI分析",
            "expires_days": 90
        },
        {
            "code": "KBDASOCCER100", 
            "credits": 100,
            "description": "足球粉丝专属兑换码 - 100次AI分析",
            "expires_days": 180
        },
        {
            "code": "NEWUSER20",
            "credits": 20, 
            "description": "新用户礼包 - 20次AI分析",
            "expires_days": 60
        },
        {
            "code": "TRADER50",
            "credits": 50,
            "description": "交易员专属 - 50次AI分析", 
            "expires_days": 120
        },
        {
            "code": "PREMIUM30",
            "credits": 30,
            "description": "高级用户礼包 - 30次AI分析",
            "expires_days": 90
        }
    ]
    
    created_codes = []
    
    try:
        for code_info in codes_to_create:
            # 检查兑换码是否已存在
            existing_code = session.query(RedemptionCode).filter(
                RedemptionCode.code == code_info["code"]
            ).first()
            
            if existing_code:
                print(f"⚠️ 兑换码 {code_info['code']} 已存在，跳过...")
                continue
            
            # 创建过期时间
            expires_at = datetime.utcnow() + timedelta(days=code_info["expires_days"])
            
            # 创建兑换码
            redemption_code = RedemptionCode(
                code=code_info["code"],
                credits=code_info["credits"], 
                description=code_info["description"],
                expires_at=expires_at,
                is_active=True,
                is_used=False
            )
            
            session.add(redemption_code)
            created_codes.append(code_info)
            print(f"✅ 创建兑换码: {code_info['code']} ({code_info['credits']}次)")
        
        session.commit()
        print(f"\n🎉 成功创建 {len(created_codes)} 个兑换码！")
        
        # 显示创建的兑换码信息
        print("\n📋 兑换码列表:")
        print("=" * 60)
        for code in created_codes:
            print(f"🎫 {code['code']}")
            print(f"   💎 点数: {code['credits']} 次AI分析")
            print(f"   📝 描述: {code['description']}")
            print(f"   ⏰ 有效期: {code['expires_days']} 天")
            print("-" * 60)
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"❌ 创建兑换码时出错: {e}")
        return False
    finally:
        session.close()

def list_all_codes():
    """列出所有兑换码"""
    if not db_manager:
        print("❌ 数据库管理器未初始化")
        return
    
    session = db_manager.get_session_sync()
    
    try:
        codes = session.query(RedemptionCode).all()
        
        if not codes:
            print("📭 暂无兑换码")
            return
        
        print(f"\n📊 现有兑换码总数: {len(codes)}")
        print("=" * 80)
        
        for code in codes:
            status = "✅ 启用" if code.is_active else "❌ 禁用"
            used_status = "🔴 已使用" if code.is_used else "🟢 未使用"
            
            print(f"🎫 {code.code}")
            print(f"   💎 点数: {code.credits}")
            print(f"   📝 描述: {code.description or '无描述'}")
            print(f"   📊 状态: {status} | {used_status}")
            print(f"   📅 创建: {code.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if code.expires_at:
                print(f"   ⏰ 过期: {code.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
            if code.used_at:
                print(f"   🕒 使用时间: {code.used_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 80)
            
    except Exception as e:
        print(f"❌ 列出兑换码时出错: {e}")
    finally:
        session.close()

def main():
    print("🚀 兑换码系统初始化")
    print("=" * 50)
    
    # 1. 创建数据表
    if not create_redemption_tables():
        print("❌ 数据表创建失败，退出")
        return
    
    # 2. 生成兑换码
    if not generate_specific_codes():
        print("❌ 兑换码生成失败，退出")
        return
    
    # 3. 列出所有兑换码
    list_all_codes()
    
    print("\n🎊 兑换码系统初始化完成！")
    print("\n📝 使用方法:")
    print("1. 用户登录后可在前端界面看到兑换码输入框")
    print("2. 输入兑换码如 WEILIANG10 即可获得相应的AI分析次数")
    print("3. 每个账号对每个兑换码只能使用一次")
    print("4. 兑换码有有效期限制")

if __name__ == "__main__":
    main()