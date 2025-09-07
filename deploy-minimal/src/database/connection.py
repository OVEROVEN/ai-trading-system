"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging
from typing import Generator

from config.settings import settings
from .models import Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                settings.database_url,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=300,    # Recycle connections every 5 minutes
                echo=settings.debug  # Log SQL queries in debug mode
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create all tables
            self.create_tables()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}")
            raise
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {str(e)}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_session_sync(self) -> Session:
        """Get a synchronous database session (manual cleanup required)"""
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.get_session() as session:
                # Simple query to test connection
                session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
def get_db_session():
    """Dependency function for FastAPI"""
    session = db_manager.get_session_sync()
    try:
        yield session
    finally:
        session.close()

@contextmanager
def get_db():
    """Context manager for database sessions"""
    with db_manager.get_session() as session:
        yield session

def init_database():
    """Initialize database (called at startup)"""
    return db_manager

def health_check_db() -> bool:
    """Check database health"""
    return db_manager.health_check()

# Database utilities
class DatabaseUtils:
    """Utility functions for database operations"""
    
    @staticmethod
    def bulk_insert_stock_prices(session: Session, price_data: list):
        """Efficiently insert multiple stock price records"""
        try:
            from .models import StockPrice
            session.bulk_insert_mappings(StockPrice, price_data)
            session.commit()
            logger.info(f"Bulk inserted {len(price_data)} stock price records")
        except Exception as e:
            session.rollback()
            logger.error(f"Bulk insert failed: {str(e)}")
            raise
    
    @staticmethod
    def bulk_insert_indicators(session: Session, indicator_data: list):
        """Efficiently insert multiple technical indicator records"""
        try:
            from .models import TechnicalIndicator
            session.bulk_insert_mappings(TechnicalIndicator, indicator_data)
            session.commit()
            logger.info(f"Bulk inserted {len(indicator_data)} indicator records")
        except Exception as e:
            session.rollback()
            logger.error(f"Bulk insert indicators failed: {str(e)}")
            raise
    
    @staticmethod
    def get_latest_price(session: Session, symbol: str):
        """Get the latest price for a symbol"""
        try:
            from .models import StockPrice
            latest = session.query(StockPrice)\
                          .filter(StockPrice.symbol == symbol)\
                          .order_by(StockPrice.timestamp.desc())\
                          .first()
            return latest
        except Exception as e:
            logger.error(f"Failed to get latest price for {symbol}: {str(e)}")
            return None
    
    @staticmethod
    def get_price_history(session: Session, symbol: str, days: int = 30):
        """Get price history for a symbol"""
        try:
            from datetime import datetime, timedelta
            from .models import StockPrice
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            prices = session.query(StockPrice)\
                           .filter(StockPrice.symbol == symbol)\
                           .filter(StockPrice.timestamp >= cutoff_date)\
                           .order_by(StockPrice.timestamp.asc())\
                           .all()
            return prices
        except Exception as e:
            logger.error(f"Failed to get price history for {symbol}: {str(e)}")
            return []
    
    @staticmethod
    def cleanup_old_data(session: Session, days_to_keep: int = 365):
        """Clean up old data to manage database size"""
        try:
            from datetime import datetime, timedelta
            from .models import StockPrice, TechnicalIndicator, TradingSignal
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Delete old records
            deleted_prices = session.query(StockPrice)\
                                  .filter(StockPrice.timestamp < cutoff_date)\
                                  .delete()
            
            deleted_indicators = session.query(TechnicalIndicator)\
                                      .filter(TechnicalIndicator.timestamp < cutoff_date)\
                                      .delete()
            
            deleted_signals = session.query(TradingSignal)\
                                   .filter(TradingSignal.timestamp < cutoff_date)\
                                   .delete()
            
            session.commit()
            
            logger.info(f"Cleaned up old data: {deleted_prices} prices, "
                       f"{deleted_indicators} indicators, {deleted_signals} signals")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to cleanup old data: {str(e)}")
            raise

# Initialize on import
try:
    db_manager = DatabaseManager()
except Exception as e:
    logger.error(f"Failed to initialize database manager: {str(e)}")
    db_manager = None