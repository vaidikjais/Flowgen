"""
Diagram Model - SQLModel Database Entity

Defines the diagram database table schema for storing generated diagrams
with prompt caching support.
"""
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, Text, Index
from sqlalchemy import String


class Diagram(SQLModel, table=True):
    """
    Diagram entity for storing generated diagrams.
    
    Stores both the DOT code and metadata about generated diagrams.
    Supports caching via prompt_hash to avoid redundant LLM calls.
    """
    __tablename__ = "diagrams"
    
    # Primary key
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique identifier for the diagram"
    )
    
    # User prompt and hash for caching
    prompt: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Original user prompt in natural language"
    )
    prompt_hash: str = Field(
        max_length=64,
        index=True,
        description="SHA-256 hash of the prompt for cache lookup"
    )
    
    # Generated DOT code
    dot_code: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Generated Graphviz DOT code"
    )
    
    # Rendering configuration
    format: str = Field(
        max_length=10,
        default="svg",
        description="Image format (svg or png)"
    )
    layout: str = Field(
        max_length=20,
        default="dot",
        description="Graphviz layout engine used (dot, neato, fdp, etc.)"
    )
    
    # Image storage (optional - can store base64 or URL)
    image_data: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Base64-encoded image data or URL to stored image"
    )
    
    # Optional user association
    user_id: Optional[str] = Field(
        default=None,
        max_length=255,
        index=True,
        description="User identifier (for multi-tenant support)"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        description="Timestamp when diagram was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when diagram was last updated"
    )
    
    # Metadata
    token_count: Optional[int] = Field(
        default=None,
        description="Number of tokens used for generation (if tracked)"
    )
    generation_time_ms: Optional[int] = Field(
        default=None,
        description="Time taken to generate the diagram in milliseconds"
    )
    
    class Config:
        """SQLModel configuration."""
        arbitrary_types_allowed = True


# Create indexes for common queries
__table_args__ = (
    Index("idx_diagrams_prompt_hash", "prompt_hash"),
    Index("idx_diagrams_created_at", "created_at"),
    Index("idx_diagrams_user_id", "user_id"),
)

