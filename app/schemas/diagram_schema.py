"""
Diagram Schemas - Pydantic Models for Diagram API Validation

Defines Pydantic schemas for diagram-related API requests
and responses with proper validation and serialization.
"""
from typing import Literal, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


# Input Schemas (API requests)

class GenerateDiagramRequest(BaseModel):
    """Request model for generating a diagram from natural language."""
    
    prompt: str = Field(
        ..., 
        min_length=1, 
        max_length=2000,
        description="Natural language description of the diagram to generate"
    )
    format: Literal["svg", "png"] = Field(
        default="svg",
        description="Output format for the diagram"
    )
    layout: Optional[Literal["dot", "neato", "fdp", "sfdp", "twopi", "circo"]] = Field(
        default="dot",
        description="Graphviz layout engine to use"
    )
    user_id: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional user identifier for tracking"
    )
    
    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Validate prompt is not empty after stripping."""
        if not v.strip():
            raise ValueError("Prompt cannot be empty or whitespace only")
        return v.strip()


class PreviewDiagramRequest(BaseModel):
    """Request model for previewing/rendering DOT code directly."""
    
    dot: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Graphviz DOT code to render"
    )
    format: Literal["svg", "png"] = Field(
        default="svg",
        description="Output format for the diagram"
    )
    layout: Optional[Literal["dot", "neato", "fdp", "sfdp", "twopi", "circo"]] = Field(
        default="dot",
        description="Graphviz layout engine to use"
    )
    
    @field_validator("dot")
    @classmethod
    def validate_dot(cls, v: str) -> str:
        """Basic validation of DOT code."""
        if not v.strip():
            raise ValueError("DOT code cannot be empty")
        return v.strip()


# Internal Schemas (for service layer)

class DiagramCreate(BaseModel):
    """Schema for creating a diagram in the database."""
    
    prompt: str
    prompt_hash: str
    dot_code: str
    format: str = "svg"
    layout: str = "dot"
    image_data: Optional[str] = None
    user_id: Optional[str] = None
    token_count: Optional[int] = None
    generation_time_ms: Optional[int] = None


class DiagramUpdate(BaseModel):
    """Schema for updating a diagram."""
    
    dot_code: Optional[str] = None
    image_data: Optional[str] = None
    updated_at: Optional[datetime] = None


# Output Schemas (API responses)

class DiagramResponse(BaseModel):
    """Response model for JSON fallback with base64-encoded image."""
    
    diagram_dot: str = Field(
        ...,
        description="Generated Graphviz DOT code"
    )
    image_base64: str = Field(
        ...,
        description="Base64-encoded diagram image"
    )
    format: str = Field(
        ...,
        description="Image format (svg or png)"
    )
    diagram_id: Optional[UUID] = Field(
        None,
        description="ID of the saved diagram in database"
    )


class DiagramOut(BaseModel):
    """Output schema for diagram metadata (without image data)."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    prompt: str
    dot_code: str
    format: str
    layout: str
    user_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    token_count: Optional[int]
    generation_time_ms: Optional[int]


class DiagramDetailOut(BaseModel):
    """Detailed output schema including image data."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    prompt: str
    dot_code: str
    format: str
    layout: str
    image_data: Optional[str]
    user_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    token_count: Optional[int]
    generation_time_ms: Optional[int]


class DiagramListResponse(BaseModel):
    """Paginated list response for diagrams."""
    
    total: int = Field(..., description="Total number of diagrams")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Number of items skipped")
    items: list[DiagramOut] = Field(..., description="List of diagrams")

