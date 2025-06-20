"""
Simple application configuration.
"""

from functools import lru_cache
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = ConfigDict(env_file=".env")
    
    # Application
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    
    # Database
    database_url: str = Field(...)
    
    # CORS
    allowed_hosts: list[str] = Field(default=["*"])
    
    # Embeddings
    cohere_api_key: str = Field(default="")
    embedding_model: str = Field(default="embed-english-v3.0")
    embedding_dimension: int = Field(default=1024)
    
    # Vector Index
    default_vector_index: str = Field(default="hnsw")


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


settings = get_settings() 