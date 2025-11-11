"""
Common Schemas - Shared Pydantic Models

Contains common schemas used across the application including
pagination, health checks, and error responses.
"""
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field

# Type variable for generic pagination
T = TypeVar('T')


class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    
    limit: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum number of items to return"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of items to skip"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    
    total: int = Field(
        ...,
        description="Total number of items available"
    )
    limit: int = Field(
        ...,
        description="Maximum number of items per page"
    )
    offset: int = Field(
        ...,
        description="Number of items skipped"
    )
    items: List[T] = Field(
        ...,
        description="List of items in this page"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(
        default="ok",
        description="Overall health status"
    )
    version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    database: Optional[str] = Field(
        default=None,
        description="Database connection status"
    )
    llm: Optional[str] = Field(
        default=None,
        description="LLM availability status"
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str = Field(
        ...,
        description="Error type or message"
    )
    detail: Optional[str] = Field(
        None,
        description="Additional error details"
    )
    request_id: Optional[str] = Field(
        None,
        description="Request ID for tracking"
    )

