"""
User Preference Schemas - Pydantic Models for User Preferences

Defines Pydantic schemas for user preference-related API requests
and responses.
"""
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# Input Schemas (API requests)

class UserPreferenceCreate(BaseModel):
    """Input schema for creating user preferences."""
    
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique user identifier"
    )
    default_format: Literal["svg", "png"] = Field(
        default="svg",
        description="Default diagram format"
    )
    default_layout: Literal["dot", "neato", "fdp", "sfdp", "twopi", "circo"] = Field(
        default="dot",
        description="Default Graphviz layout engine"
    )
    theme: Optional[Literal["light", "dark", "auto"]] = Field(
        default="light",
        description="UI theme preference"
    )
    enable_notifications: bool = Field(
        default=True,
        description="Whether to enable notifications"
    )


class UserPreferenceUpdate(BaseModel):
    """Input schema for updating user preferences."""
    
    default_format: Optional[Literal["svg", "png"]] = None
    default_layout: Optional[Literal["dot", "neato", "fdp", "sfdp", "twopi", "circo"]] = None
    theme: Optional[Literal["light", "dark", "auto"]] = None
    enable_notifications: Optional[bool] = None


# Output Schemas (API responses)

class UserPreferenceOut(BaseModel):
    """Output schema for user preferences."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: str
    default_format: str
    default_layout: str
    theme: Optional[str]
    enable_notifications: bool
    created_at: datetime
    updated_at: Optional[datetime]

