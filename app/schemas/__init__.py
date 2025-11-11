"""Pydantic schemas for request/response validation."""

from app.schemas.common_schema import (
    PaginationParams,
    PaginatedResponse,
    HealthResponse,
    ErrorResponse
)
from app.schemas.diagram_schema import (
    GenerateDiagramRequest,
    PreviewDiagramRequest,
    DiagramCreate,
    DiagramUpdate,
    DiagramResponse,
    DiagramOut,
    DiagramDetailOut,
    DiagramListResponse
)
from app.schemas.user_preference_schema import (
    UserPreferenceCreate,
    UserPreferenceUpdate,
    UserPreferenceOut
)

__all__ = [
    # Common schemas
    "PaginationParams",
    "PaginatedResponse",
    "HealthResponse",
    "ErrorResponse",
    # Diagram schemas
    "GenerateDiagramRequest",
    "PreviewDiagramRequest",
    "DiagramCreate",
    "DiagramUpdate",
    "DiagramResponse",
    "DiagramOut",
    "DiagramDetailOut",
    "DiagramListResponse",
    # User preference schemas
    "UserPreferenceCreate",
    "UserPreferenceUpdate",
    "UserPreferenceOut",
]

