"""
Main API v1 router configuration.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import libraries, documents, chunks

# Create the main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    libraries.router,
    prefix="/libraries",
    tags=["libraries"],
)

api_router.include_router(
    documents.router,
    prefix="/documents", 
    tags=["documents"],
)

api_router.include_router(
    chunks.router,
    prefix="/chunks",
    tags=["chunks"],
)
