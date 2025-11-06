"""
Configuration Module

Loads and manages application configuration from environment variables.
Uses pydantic for validation and type safety.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via .env file or environment variables.
    """
    
    # LiveKit Configuration
    livekit_url: str = "ws://localhost:7880"
    livekit_api_key: Optional[str] = None
    livekit_api_secret: Optional[str] = None
    
    # FastAPI Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_title: str = "Voice Agent API"
    api_version: str = "1.0.0"
    api_debug: bool = False
    
    # Agent Configuration
    agent_timeout: int = 30  # seconds
    
    # AI Service API Keys (optional)
    google_api_key: Optional[str] = None
    eleven_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env instead of raising errors


# Global settings instance
settings = Settings()

