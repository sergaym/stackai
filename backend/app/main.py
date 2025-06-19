"""
Main FastAPI application factory and configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings

def create_application() -> FastAPI:
    """
    Application factory pattern for creating FastAPI instance.
    """
    settings = get_settings()
    
    app = FastAPI(
        title="StackAI Vector Database API",
        description="A Vector Database for semantic search and document indexing",
        version="1.0.0",
        docs_url="/docs" if settings.environment == "development" else None,
        redoc_url="/redoc" if settings.environment == "development" else None,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for container orchestration."""
        return {
            "status": "healthy",
            "service": "stack-ai-vector-db-api",
            "version": "1.0.0",
        }

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    return app


# Create the FastAPI application instance
app = create_application() 