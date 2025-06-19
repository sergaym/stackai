"""
Simple application configuration.
"""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    environment: str = Field("development", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # CORS
    allowed_hosts: list[str] = Field(["*"], env="ALLOWED_HOSTS")
    
    # Optional
    cohere_api_key: str = Field("", env="COHERE_API_KEY")
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


settings = get_settings() 