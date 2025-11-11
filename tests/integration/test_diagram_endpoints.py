"""
Integration tests for diagram endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_preview_diagram(client: AsyncClient, sample_dot_code: str):
    """Test diagram preview endpoint."""
    response = await client.post(
        "/api/diagram/preview",
        json={
            "dot": sample_dot_code,
            "format": "svg",
            "layout": "dot"
        }
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_preview_diagram_json_response(client: AsyncClient, sample_dot_code: str):
    """Test diagram preview with JSON response."""
    response = await client.post(
        "/api/diagram/preview",
        json={
            "dot": sample_dot_code,
            "format": "svg",
            "layout": "dot"
        },
        headers={"Accept": "application/json"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "diagram_dot" in data
    assert "image_base64" in data
    assert "format" in data
    assert data["format"] == "svg"


@pytest.mark.asyncio
async def test_preview_diagram_invalid_dot(client: AsyncClient):
    """Test diagram preview with invalid DOT code."""
    response = await client.post(
        "/api/diagram/preview",
        json={
            "dot": "invalid dot code",
            "format": "svg",
            "layout": "dot"
        }
    )
    
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_get_diagram_history_empty(client: AsyncClient):
    """Test getting diagram history when empty."""
    response = await client.get("/api/diagram/history")
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert data["total"] == 0
    assert len(data["items"]) == 0


@pytest.mark.asyncio
async def test_get_diagram_not_found(client: AsyncClient):
    """Test getting non-existent diagram."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/diagram/{fake_uuid}")
    
    assert response.status_code == 404

