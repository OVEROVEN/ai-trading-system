#!/usr/bin/env python3
"""
Setup script to ensure redemption codes exist in database
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import datetime, timedelta
from src.database.connection import get_db
from src.database.redemption_models import RedemptionCode

def setup_redemption_codes():
    """Ensure redemption codes exist in database"""
    print("🎫 Setting up redemption codes...")
    print("=" * 50)
    
    # Redemption codes to create
    codes_to_create = [
        {"code": "WEILIANG10", "credits": 10, "desc": "維良專屬兌換碼"},
        {"code": "KBDASOCCER100", "credits": 100, "desc": "足球粉絲專屬兌換碼"},
        {"code": "NEWUSER20", "credits": 20, "desc": "新用戶礼包"},
        {"code": "TRADER50", "credits": 50, "desc": "交易員專屬"},
        {"code": "PREMIUM30", "credits": 30, "desc": "高級用戶礼包"}
    ]
    
    try:
        with get_db() as db:
            for code_info in codes_to_create:
                # Check if code already exists
                existing_code = db.query(RedemptionCode).filter(
                    RedemptionCode.code == code_info["code"]
                ).first()
                
                if existing_code:
                    print(f"✅ Code {code_info['code']} already exists")
                    print(f"   Credits: {existing_code.credits}")
                    print(f"   Is Active: {existing_code.is_active}")
                    print(f"   Is Used: {existing_code.is_used}")
                    if existing_code.expires_at:
                        print(f"   Expires: {existing_code.expires_at}")
                else:
                    # Create new code
                    new_code = RedemptionCode(
                        code=code_info["code"],
                        credits=code_info["credits"],
                        description=code_info["desc"],
                        expires_at=datetime.utcnow() + timedelta(days=365),  # 1 year expiration
                        is_active=True,
                        is_used=False
                    )
                    db.add(new_code)
                    db.commit()
                    print(f"✅ Created new code {code_info['code']}")
                    print(f"   Credits: {code_info['credits']}")
                    print(f"   Description: {code_info['desc']}")
                
                print()
            
            # Count total codes
            total_codes = db.query(RedemptionCode).count()
            active_codes = db.query(RedemptionCode).filter(
                RedemptionCode.is_active == True,
                RedemptionCode.is_used == False
            ).count()
            
            print("=" * 50)
            print(f"📊 Database Summary:")
            print(f"   Total codes: {total_codes}")
            print(f"   Active unused codes: {active_codes}")
            print("✅ Redemption codes setup complete!")
            
    except Exception as e:
        print(f"❌ Error setting up redemption codes: {e}")
        return False
    
    return True

if __name__ == "__main__":
    setup_redemption_codes()