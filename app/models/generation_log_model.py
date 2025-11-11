"""
Generation Log Model - SQLModel Database Entity

Defines the generation log table schema for tracking LLM API usage,
performance metrics, and error logging.
"""
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column, Text


class GenerationLog(SQLModel, table=True):
    """
    Generation Log entity for tracking LLM API usage and performance.
    
    Logs each diagram generation attempt for analytics, debugging,
    and cost tracking.
    """
    __tablename__ = "generation_logs"
    
    # Primary key
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique identifier for the log entry"
    )
    
    # Request information
    prompt: str = Field(
        sa_column=Column(Text, nullable=False),
        description="User prompt that was sent to LLM"
    )
    prompt_hash: str = Field(
        max_length=64,
        index=True,
        description="SHA-256 hash of the prompt"
    )
    
    # API usage tracking
    tokens_used: Optional[int] = Field(
        default=None,
        description="Number of tokens consumed by the LLM call"
    )
    model_used: Optional[str] = Field(
        default=None,
        max_length=100,
        description="LLM model that was used (e.g., gpt-4, gpt-3.5-turbo)"
    )
    
    # Performance metrics
    latency_ms: Optional[int] = Field(
        default=None,
        description="Time taken for the LLM call in milliseconds"
    )
    total_time_ms: Optional[int] = Field(
        default=None,
        description="Total time including rendering in milliseconds"
    )
    
    # Status tracking
    success: bool = Field(
        default=True,
        index=True,
        description="Whether the generation was successful"
    )
    error_message: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Error message if generation failed"
    )
    error_type: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Type of error (e.g., LLMError, RenderError)"
    )
    
    # Cache information
    was_cached: bool = Field(
        default=False,
        description="Whether the result was served from cache"
    )
    
    # Optional user association
    user_id: Optional[str] = Field(
        default=None,
        max_length=255,
        index=True,
        description="User identifier (for analytics)"
    )
    
    # Related diagram
    diagram_id: Optional[UUID] = Field(
        default=None,
        foreign_key="diagrams.id",
        description="ID of the generated diagram (if successful)"
    )
    
    # Timestamp
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True,
        description="Timestamp when the generation was attempted"
    )
    
    class Config:
        """SQLModel configuration."""
        arbitrary_types_allowed = True

