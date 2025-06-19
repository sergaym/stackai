"""
Chunk management endpoints.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.chunk import (
    ChunkCreateRequest,
    ChunkUpdateRequest,
    ChunkResponse,
    ChunkListResponse,
    ChunkDeleteResponse,
)
from app.services.chunk_service import ChunkService
from app.core.dependencies import get_chunk_service
from app.db.models import Chunk

router = APIRouter()


def _chunk_to_response(chunk: Chunk) -> ChunkResponse:
    """Convert Chunk domain model to ChunkResponse."""
    return ChunkResponse(
        id=chunk.id,
        document_id=chunk.document_id,
        library_id=chunk.library_id,
        text=chunk.text,
        text_length=chunk.text_length,
        position=chunk.position,
        metadata=chunk.metadata_ or {},
        embedding_dimension=chunk.embedding_dimension,
        embedding_model=chunk.embedding_model,
        created_at=chunk.created_at,
        updated_at=chunk.updated_at,
        is_indexed=chunk.is_indexed
    )


@router.post("/", response_model=ChunkResponse, status_code=status.HTTP_201_CREATED)
async def create_chunk(
    chunk_data: ChunkCreateRequest,
    chunk_service: ChunkService = Depends(get_chunk_service),
) -> ChunkResponse:
    """
    Create a new chunk in a document.
    
    Args:
        chunk_data: Chunk creation data
        chunk_service: Injected chunk service
        
    Returns:
        Created chunk
    """
    try:
        chunk = await chunk_service.create_chunk(
            document_id=chunk_data.document_id,
            library_id=chunk_data.library_id,
            text=chunk_data.text,
            position=chunk_data.position,
            metadata=chunk_data.metadata
        )
        
        return _chunk_to_response(chunk)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=ChunkListResponse)
async def list_chunks(
    document_id: UUID = None,
    library_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    chunk_service: ChunkService = Depends(get_chunk_service),
) -> ChunkListResponse:
    """
    List chunks with optional filtering.
    
    Args:
        document_id: Optional document filter
        library_id: Optional library filter
        skip: Number of chunks to skip
        limit: Maximum number of chunks to return
        chunk_service: Injected chunk service
        
    Returns:
        List of chunks with metadata
    """
    chunks = await chunk_service.list_chunks(
        document_id=document_id,
        library_id=library_id,
        skip=skip,
        limit=limit
    )
    total_count = await chunk_service.count_chunks(
        document_id=document_id,
        library_id=library_id
    )
    
    chunk_responses = [_chunk_to_response(chunk) for chunk in chunks]
    
    return ChunkListResponse(
        chunks=chunk_responses,
        total=total_count,
        skip=skip,
        limit=limit
    )


@router.get("/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(
    chunk_id: UUID,
    chunk_service: ChunkService = Depends(get_chunk_service),
) -> ChunkResponse:
    """
    Get a specific chunk by ID.
    
    Args:
        chunk_id: Chunk identifier
        chunk_service: Injected chunk service
        
    Returns:
        Chunk details
    """
    chunk = await chunk_service.get_chunk(chunk_id)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chunk with ID {chunk_id} not found"
        )
    
    return _chunk_to_response(chunk)


@router.put("/{chunk_id}", response_model=ChunkResponse)
async def update_chunk(
    chunk_id: UUID,
    chunk_data: ChunkUpdateRequest,
    chunk_service: ChunkService = Depends(get_chunk_service),
) -> ChunkResponse:
    """
    Update a specific chunk.
    
    Args:
        chunk_id: Chunk identifier
        chunk_data: Chunk update data
        chunk_service: Injected chunk service
        
    Returns:
        Updated chunk
    """
    # Build update dict from non-None fields
    updates = {}
    if chunk_data.text is not None:
        updates["text"] = chunk_data.text
        updates["text_length"] = len(chunk_data.text)
    if chunk_data.position is not None:
        updates["position"] = chunk_data.position
    if chunk_data.metadata is not None:
        updates["metadata_"] = chunk_data.metadata
    
    chunk = await chunk_service.update_chunk(chunk_id, **updates)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chunk with ID {chunk_id} not found"
        )
    
    return _chunk_to_response(chunk)


@router.put("/{chunk_id}/embedding", response_model=ChunkResponse)
async def update_chunk_embedding(
    chunk_id: UUID,
    embedding_data: dict,
    chunk_service: ChunkService = Depends(get_chunk_service),
) -> ChunkResponse:
    """
    Update a chunk's embedding vector.
    
    Args:
        chunk_id: Chunk identifier
        embedding_data: Dictionary with 'embedding', 'model', and optional 'is_indexed'
        chunk_service: Injected chunk service
        
    Returns:
        Updated chunk with embedding
    """
    if "embedding" not in embedding_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing 'embedding' field in request body"
        )
    
    embedding = embedding_data["embedding"]
    model = embedding_data.get("model", "unknown")
    is_indexed = embedding_data.get("is_indexed", True)
    
    if not isinstance(embedding, list) or not all(isinstance(x, (int, float)) for x in embedding):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'embedding' must be a list of numbers"
        )
    
    # Update the chunk with embedding
    updates = {
        "embedding": embedding,
        "embedding_dimension": len(embedding),
        "embedding_model": model,
        "is_indexed": is_indexed
    }
    
    chunk = await chunk_service.update_chunk(chunk_id, **updates)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chunk with ID {chunk_id} not found"
        )
    
    return _chunk_to_response(chunk)


@router.delete("/{chunk_id}", response_model=ChunkDeleteResponse)
async def delete_chunk(
    chunk_id: UUID,
    chunk_service: ChunkService = Depends(get_chunk_service),
) -> ChunkDeleteResponse:
    """Delete a specific chunk."""
    
    deletion_result = await chunk_service.delete_chunk(chunk_id)
    
    if not deletion_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chunk with ID {chunk_id} not found"
        )
    
    return ChunkDeleteResponse(**deletion_result)