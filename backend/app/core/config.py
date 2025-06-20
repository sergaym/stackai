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
    
    # Embeddings
    cohere_api_key: str = Field("", env="COHERE_API_KEY")
    embedding_model: str = Field("embed-english-v3.0", env="EMBEDDING_MODEL")
    embedding_dimension: int = Field(1024, env="EMBEDDING_DIMENSION")
    
    # Vector Index
    default_vector_index: str = Field("hnsw", env="DEFAULT_VECTOR_INDEX")
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


settings = get_settings() 