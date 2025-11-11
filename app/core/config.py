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
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = Field(
        description="LLM provider: 'openai', 'nvidia', or 'gemini'"
    )
    
    # OpenAI API Configuration
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenAI API key for LLM access"
    )
    OPENAI_MODEL: Optional[str] = Field(
        default=None,
        description="OpenAI model to use for diagram generation"
    )
    OPENAI_BASE_URL: Optional[str] = Field(
        default=None,
        description="Base URL for OpenAI API (can be changed for proxies)"
    )
    
    # NVIDIA NIM Configuration
    NVIDIA_API_KEY: Optional[str] = Field(
        default=None,
        description="NVIDIA NIM API key"
    )
    NVIDIA_MODEL: Optional[str] = Field(
        default=None,
        description="NVIDIA NIM model name"
    )
    NVIDIA_BASE_URL: Optional[str] = Field(
        default=None,
        description="NVIDIA NIM API base URL"
    )
    
    # Google Gemini Configuration
    GOOGLE_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API key"
    )
    GEMINI_MODEL: Optional[str] = Field(
        default=None,
        description="Google Gemini model name"
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
    
    @field_validator("LLM_PROVIDER")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        """Validate LLM provider is valid."""
        valid_providers = ["openai", "nvidia", "gemini"]
        v_lower = v.lower().strip()
        if v_lower not in valid_providers:
            raise ValueError(
                f"Invalid LLM_PROVIDER: {v}. Must be one of {valid_providers}"
            )
        return v_lower
    
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
    
    def validate_llm(self) -> None:
        """Validate LLM configuration and warn if missing."""
        if self.LLM_PROVIDER == "openai":
            if not self.OPENAI_API_KEY:
                print("⚠️  WARNING: OPENAI_API_KEY not set. LLM will use fallback mock implementation.")
            if not self.OPENAI_MODEL:
                print("⚠️  WARNING: OPENAI_MODEL not set. Please set in .env")
        elif self.LLM_PROVIDER == "nvidia":
            if not self.NVIDIA_API_KEY:
                print("⚠️  WARNING: NVIDIA_API_KEY not set. LLM will use fallback mock implementation.")
            if not self.NVIDIA_MODEL:
                print("⚠️  WARNING: NVIDIA_MODEL not set. Please set in .env")
        elif self.LLM_PROVIDER == "gemini":
            if not self.GOOGLE_API_KEY:
                print("⚠️  WARNING: GOOGLE_API_KEY not set. LLM will use fallback mock implementation.")
            if not self.GEMINI_MODEL:
                print("⚠️  WARNING: GEMINI_MODEL not set. Please set in .env")


# Create global settings instance
settings = Settings()

# Validate LLM configuration on startup
settings.validate_llm()

