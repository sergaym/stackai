"""
FastAPI dependency injection configuration.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from app.db.database import get_db_session
from app.repositories.async_chunk_repository import AsyncChunkRepository
from app.repositories.async_document_repository import AsyncDocumentRepository
from app.repositories.async_library_repository import AsyncLibraryRepository
from app.services.chunk_service import ChunkService
from app.services.document_service import DocumentService
from app.services.library_service import LibraryService


# Database dependency
async def get_db() -> AsyncSession:
    """Get database session."""
    async for session in get_db_session():
        yield session


# Service dependencies
async def get_library_service(db: AsyncSession = Depends(get_db)) -> LibraryService:
    """Get library service instance."""
    library_repository = AsyncLibraryRepository(db)
    return LibraryService(library_repository)


async def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    """Get document service instance."""
    document_repository = AsyncDocumentRepository(db)
    library_repository = AsyncLibraryRepository(db)
    return DocumentService(document_repository, library_repository)


async def get_chunk_service(db: AsyncSession = Depends(get_db)) -> ChunkService:
    """Get chunk service instance."""
    chunk_repository = AsyncChunkRepository(db)
    document_repository = AsyncDocumentRepository(db)
    library_repository = AsyncLibraryRepository(db)
    return ChunkService(chunk_repository, document_repository, library_repository)

 