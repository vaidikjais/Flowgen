"""
Test Configuration and Fixtures

Provides pytest fixtures for testing the application including:
- Test client
- Sample test data
"""
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient

from app.main import app


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client for API testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client


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

