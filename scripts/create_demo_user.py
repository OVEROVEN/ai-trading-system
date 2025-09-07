#!/usr/bin/env python3
"""
創建演示用戶腳本
"""

import asyncio
from src.database.connection import get_db_session
from src.auth import crud
from src.auth.schemas import UserCreate

def create_demo_user():
    """創建演示用戶"""
    db = next(get_db_session())
    
    try:
        # 檢查用戶是否已存在
        existing_user = crud.get_user_by_email(db, "demo@example.com")
        if existing_user:
            print("✅ 演示用戶已存在:")
            print(f"   Email: {existing_user.email}")
            print(f"   Name: {existing_user.full_name}")
            print(f"   ID: {existing_user.id}")
            return
        
        # 創建新用戶
        user_create = UserCreate(
            email="demo@example.com",
            password="demo123",
            full_name="Demo User"
        )
        
        user = crud.create_user(db, user_create)
        
        print("✅ 演示用戶創建成功:")
        print(f"   Email: {user.email}")
        print(f"   Password: demo123")
        print(f"   Name: {user.full_name}")
        print(f"   ID: {user.id}")
        print(f"   免費配額: 3次初始 + 每天1次")
        
    except Exception as e:
        print(f"❌ 創建用戶失敗: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_user()