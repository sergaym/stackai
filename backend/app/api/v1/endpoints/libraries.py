"""
Library management endpoints.
"""

import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.schemas.library import (
    LibraryCreateRequest,
    LibraryUpdateRequest,
    LibraryResponse,
    LibraryListResponse,
    LibraryDeleteResponse,
)
from app.services.library_service import LibraryService
from app.core.dependencies import get_library_service

router = APIRouter()
logger = logging.getLogger(__name__)


def _library_to_response(library) -> LibraryResponse:
    """Convert Library domain model to API response."""
    return LibraryResponse(
        id=library.id,
        name=library.name,
        description=library.description,
        metadata=library.metadata_ or {},  # Handle metadata_ -> metadata conversion
        created_at=library.created_at,
        updated_at=library.updated_at,
        document_count=library.document_count,
        chunk_count=library.chunk_count
    )


@router.post("/", response_model=LibraryResponse, status_code=status.HTTP_201_CREATED)
async def create_library(
    library_data: LibraryCreateRequest,
    library_service: LibraryService = Depends(get_library_service),
) -> LibraryResponse:
    """
    Create a new library.
    
    Args:
        library_data: Library creation data
        library_service: Injected library service
        
    Returns:
        Created library
    """
    try:
        library = await library_service.create_library(
            name=library_data.name,
            description=library_data.description,
            metadata=library_data.metadata
        )
        
        return _library_to_response(library)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=LibraryListResponse)
async def list_libraries(
    skip: int = 0,
    limit: int = 100,
    library_service: LibraryService = Depends(get_library_service),
) -> LibraryListResponse:
    """
    List all libraries with pagination.
    
    Args:
        skip: Number of libraries to skip
        limit: Maximum number of libraries to return
        library_service: Injected library service
        
    Returns:
        List of libraries with metadata
    """
    libraries = await library_service.list_libraries(skip=skip, limit=limit)
    total_count = await library_service.count_libraries()
    
    library_responses = [
        _library_to_response(library)
        for library in libraries
    ]
    
    return LibraryListResponse(
        libraries=library_responses,
        total=total_count,
        skip=skip,
        limit=limit
    )


@router.get("/{library_id}", response_model=LibraryResponse)
async def get_library(
    library_id: UUID,
    library_service: LibraryService = Depends(get_library_service),
) -> LibraryResponse:
    """
    Get a specific library by ID.
    
    Args:
        library_id: Library identifier
        library_service: Injected library service
        
    Returns:
        Library details
    """
    library = await library_service.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library with ID {library_id} not found"
        )
    
    return _library_to_response(library)


@router.put("/{library_id}", response_model=LibraryResponse)
async def update_library(
    library_id: UUID,
    library_data: LibraryUpdateRequest,
    library_service: LibraryService = Depends(get_library_service),
) -> LibraryResponse:
    """
    Update a specific library.
    
    Args:
        library_id: Library identifier
        library_data: Library update data
        library_service: Injected library service
        
    Returns:
        Updated library
    """
    try:
        # Build update dict from non-None fields
        updates = {}
        if library_data.name is not None:
            updates["name"] = library_data.name
        if library_data.description is not None:
            updates["description"] = library_data.description
        if library_data.metadata is not None:
            updates["metadata_"] = library_data.metadata  # Converting to metadata_ field
        
        library = await library_service.update_library(library_id, **updates)
        if not library:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Library with ID {library_id} not found"
            )
        
        return _library_to_response(library)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{library_id}", response_model=LibraryDeleteResponse)
async def delete_library(
    library_id: UUID,
    library_service: LibraryService = Depends(get_library_service),
) -> LibraryDeleteResponse:
    """Delete a library and all its related data (documents and chunks)."""
    
    deletion_result = await library_service.delete_library(library_id)
    
    if not deletion_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library with ID {library_id} not found"
        )
    
    return LibraryDeleteResponse(**deletion_result)


@router.post("/{library_id}/index", response_model=dict)
async def index_library(
    library_id: UUID,
    library_service: LibraryService = Depends(get_library_service),
) -> dict:
    """
    Index all documents in a library for vector search.
    
    Args:
        library_id: Library identifier
        library_service: Injected library service
        
    Returns:
        Indexing status
    """
    try:
        return await library_service.index_library(library_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        ) 