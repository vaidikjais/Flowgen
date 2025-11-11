"""
Configuration Management - Application Settings

Handles environment variables with sensible defaults using
Pydantic Settings v2 for type-safe configuration.
"""
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Configuration is loaded from:
    1. Environment variables
    2. .env file (if present)
    3. Default values (defined here)
    """
    
    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key for LLM access"
    )
    OPENAI_MODEL: str = Field(
        default="gpt-4",
        description="OpenAI model to use for diagram generation"
    )
    OPENAI_BASE_URL: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL for OpenAI API (can be changed for proxies)"
    )
    
    # Server Configuration
    HOST: str = Field(
        default="0.0.0.0",
        description="Host to bind the server to"
    )
    PORT: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Port to bind the server to"
    )
    
    # Security Limits
    MAX_PROMPT_LENGTH: int = Field(
        default=2000,
        ge=1,
        le=10000,
        description="Maximum length of user prompts"
    )
    MAX_DOT_LENGTH: int = Field(
        default=50000,
        ge=1,
        le=100000,
        description="Maximum length of DOT code"
    )
    MAX_TOKENS: int = Field(
        default=1024,
        ge=1,
        le=4096,
        description="Maximum tokens for LLM response"
    )
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = Field(
        default=[
            "http://localhost:8000",
            "http://localhost:3000",
            "http://127.0.0.1:8000"
        ],
        description="Allowed CORS origins"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    
    # Feature Flags
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"Invalid LOG_LEVEL: {v}. Must be one of {valid_levels}"
            )
        return v_upper
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def validate_openai(self) -> None:
        """Validate OpenAI configuration and warn if missing."""
        if not self.OPENAI_API_KEY:
            print(
                "⚠️  WARNING: OPENAI_API_KEY not set. "
                "LLM will use fallback mock implementation."
            )


# Create global settings instance
settings = Settings()

# Validate OpenAI configuration on startup
settings.validate_openai()

