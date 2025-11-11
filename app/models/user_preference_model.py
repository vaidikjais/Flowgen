"""
User Preference Model - SQLModel Database Entity

Defines the user preferences table schema for storing user-specific
settings and preferences.
"""
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class UserPreference(SQLModel, table=True):
    """
    User Preference entity for storing user-specific settings.
    
    Allows users to customize default diagram generation parameters.
    """
    __tablename__ = "user_preferences"
    
    # Primary key
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique identifier for the preference record"
    )
    
    # User identifier (unique per user)
    user_id: str = Field(
        max_length=255,
        unique=True,
        index=True,
        description="Unique user identifier"
    )
    
    # Diagram generation preferences
    default_format: str = Field(
        max_length=10,
        default="svg",
        description="Default diagram format (svg or png)"
    )
    default_layout: str = Field(
        max_length=20,
        default="dot",
        description="Default Graphviz layout engine (dot, neato, fdp, etc.)"
    )
    
    # UI preferences
    theme: Optional[str] = Field(
        default="light",
        max_length=20,
        description="UI theme preference (light, dark, auto)"
    )
    
    # Notification preferences
    enable_notifications: bool = Field(
        default=True,
        description="Whether to enable notifications"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        description="Timestamp when preferences were created"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when preferences were last updated"
    )
    
    class Config:
        """SQLModel configuration."""
        arbitrary_types_allowed = True

