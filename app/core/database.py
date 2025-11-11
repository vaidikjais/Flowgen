"""
Database Utilities - Async Database Configuration

Creates async SQLModel engine and session management with
proper connection pooling and transaction handling.
"""
import logging
from typing import AsyncGenerator
from sqlmodel import SQLModel, create_engine
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)

from app.core.config import settings

logger = logging.getLogger(__name__)

# Async engine with connection pooling
async_engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def create_db_and_tables() -> None:
    """
    Create all database tables.
    
    This should be called on application startup.
    Imports all models to ensure they're registered with SQLModel.
    """
    # Import all models here to register them with SQLModel
    # This must be done before create_all is called
    from app.models.diagram_model import Diagram
    from app.models.user_preference_model import UserPreference
    from app.models.generation_log_model import GenerationLog
    
    logger.info("Creating database tables...")
    
    async with async_engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)
    
    logger.info("✓ Database tables created successfully")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.
    
    This provides a database session that automatically handles:
    - Transaction commit on success
    - Transaction rollback on error
    - Session cleanup
    
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to check connection
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def close_db_connection() -> None:
    """
    Close database connection pool.
    
    This should be called on application shutdown.
    """
    logger.info("Closing database connections...")
    await async_engine.dispose()
    logger.info("✓ Database connections closed")

