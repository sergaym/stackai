"""
Document management endpoints.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.document import (
    DocumentCreateRequest,
    DocumentUpdateRequest,
    DocumentResponse,
    DocumentListResponse,
    DocumentDeleteResponse,
)
from app.services.document_service import DocumentService
from app.core.dependencies import get_document_service
from app.db.models import Document

router = APIRouter()


def _document_to_response(document: Document) -> DocumentResponse:
    """Convert Document model to API response."""
    return DocumentResponse(
        id=document.id,
        library_id=document.library_id,
        name=document.name,
        description=document.description,
        source_url=document.source_url,
        content_type=document.content_type,
        metadata=document.metadata_ or {},  # Handle metadata_ -> metadata conversion
        created_at=document.created_at,
        updated_at=document.updated_at,
        chunk_count=document.chunk_count,
        is_processed=document.is_processed,
        processing_status=document.processing_status
    )


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreateRequest,
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """
    Create a new document in a library.
    
    Args:
        document_data: Document creation data
        document_service: Injected document service
        
    Returns:
        Created document
    """
    try:
        document = await document_service.create_document(
            library_id=document_data.library_id,
            name=document_data.name,
            description=document_data.description,
            content_type=document_data.content_type,
            metadata=document_data.metadata
        )
        
        return _document_to_response(document)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    library_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentListResponse:
    """
    List documents with optional library filtering.
    
    Args:
        library_id: Optional library filter
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        document_service: Injected document service
        
    Returns:
        List of documents with metadata
    """
    documents = await document_service.list_documents(
        library_id=library_id, 
        skip=skip, 
        limit=limit
    )
    total_count = await document_service.count_documents(library_id=library_id)
    
    document_responses = [_document_to_response(document) for document in documents]
    
    return DocumentListResponse(
        documents=document_responses,
        total=total_count,
        skip=skip,
        limit=limit
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """
    Get a specific document by ID.
    
    Args:
        document_id: Document identifier
        document_service: Injected document service
        
    Returns:
        Document details
    """
    document = await document_service.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    return _document_to_response(document)


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_data: DocumentUpdateRequest,
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """
    Update a specific document.
    
    Args:
        document_id: Document identifier
        document_data: Document update data
        document_service: Injected document service
        
    Returns:
        Updated document
    """
    # Build update dict from non-None fields
    updates = {}
    if document_data.name is not None:
        updates["name"] = document_data.name
    if document_data.description is not None:
        updates["description"] = document_data.description
    if document_data.metadata is not None:
        updates["metadata_"] = document_data.metadata  # Converting to metadata_ field
    
    document = await document_service.update_document(document_id, **updates)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    return _document_to_response(document)


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: UUID,
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentDeleteResponse:
    """Delete a document and all its related chunks."""
    
    deletion_result = await document_service.delete_document(document_id)
    
    if not deletion_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    return DocumentDeleteResponse(**deletion_result)