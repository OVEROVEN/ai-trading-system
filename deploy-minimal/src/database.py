"""
數據庫連接和會話管理

設置SQLAlchemy engine和會話工廠
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from config.settings import settings

# 數據庫配置
if settings.database_url.startswith("sqlite"):
    # SQLite配置
    engine = create_engine(
        settings.database_url,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
            "timeout": 20
        },
        echo=False  # 設為True可以看到SQL語句
    )
    
    # SQLite外鍵支持
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    event.listen(engine, "connect", set_sqlite_pragma)
    
else:
    # PostgreSQL配置
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,  # 驗證連接有效性
        pool_size=10,        # 連接池大小
        max_overflow=20,     # 最大溢出連接數
        pool_recycle=3600,   # 連接回收時間（秒）
        echo=False
    )

# 創建會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """
    依賴注入函數，為每個請求提供數據庫會話
    
    使用方法:
    def some_endpoint(db: Session = Depends(get_db)):
        # 使用db進行數據庫操作
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """創建所有數據表"""
    from src.auth.models import Base
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """刪除所有數據表（謹慎使用）"""
    from src.auth.models import Base
    Base.metadata.drop_all(bind=engine)

def init_database():
    """初始化數據庫"""
    try:
        create_tables()
        print("✅ 數據庫表創建成功")
    except Exception as e:
        print(f"❌ 數據庫初始化失敗: {e}")
        raise

def check_database_connection():
    """檢查數據庫連接"""
    try:
        db = SessionLocal()
        # 嘗試執行簡單查詢
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"❌ 數據庫連接失敗: {e}")
        return False

# 數據庫健康檢查
async def database_health_check() -> dict:
    """數據庫健康檢查，返回狀態信息"""
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).fetchone()
        db.close()
        
        return {
            "status": "healthy",
            "database_type": "sqlite" if settings.database_url.startswith("sqlite") else "postgresql",
            "connection": "ok"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "connection": "failed"
        }

if __name__ == "__main__":
    # 直接執行此腳本時初始化數據庫
    print("🚀 初始化數據庫...")
    
    if check_database_connection():
        print("✅ 數據庫連接正常")
        init_database()
    else:
        print("❌ 無法連接到數據庫，請檢查配置")