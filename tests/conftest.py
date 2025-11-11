"""
Test Configuration and Fixtures

Provides pytest fixtures for testing the application including:
- Test database setup
- Test client
- Mock dependencies
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from httpx import AsyncClient

from app.main import app
from app.core.database import get_session
from app.core.config import settings

# Test database URL (use separate test database)
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/diagramgpt_test"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.
    
    Creates all tables before test and drops them after.
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client with test database session.
    
    Overrides the get_session dependency to use test database.
    """
    # Override get_session dependency
    async def override_get_session():
        yield db_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    # Create test client
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    # Clear dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_dot_code() -> str:
    """Sample DOT code for testing."""
    return """digraph test {
    rankdir=TB;
    A -> B;
    B -> C;
}"""


@pytest.fixture
def sample_prompt() -> str:
    """Sample prompt for testing."""
    return "Create a simple flowchart with 3 nodes"

