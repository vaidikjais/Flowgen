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


