"""
Database connection and session management.
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from config.settings import settings
from database.models import Base


class Database:
    """Database connection manager."""
    
    def __init__(self, database_url: str = None):
        """Initialize database connection.
        
        Args:
            database_url: Database URL. If None, uses settings.
        """
        self.database_url = database_url or settings.DATABASE_URL
        
        # Create engine
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before using
            echo=False,  # Set to True for SQL logging
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
    
    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        Base.metadata.drop_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session.
        
        Yields:
            Database session.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database instance
_db_instance = None


def get_database() -> Database:
    """Get the global database instance.
    
    Returns:
        Database instance.
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


def get_db_session() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session.
    
    Yields:
        Database session.
    """
    db = get_database()
    with db.get_session() as session:
        yield session


def init_database():
    """Initialize database (create tables)."""
    db = get_database()
    db.create_tables()
    print("Database tables created successfully.")


if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
