"""
Document request/response schemas.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentCreateRequest(BaseModel):
    """Request schema for creating a new document."""
    
    library_id: UUID = Field(..., description="ID of the library")
    name: str = Field(..., min_length=1, max_length=255, description="Document name")
    description: Optional[str] = Field(None, max_length=1000, description="Document description")
    content_type: str = Field(default="text/plain", description="MIME type")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Custom metadata")


class DocumentUpdateRequest(BaseModel):
    """Request schema for updating an existing document."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Document name")
    description: Optional[str] = Field(None, max_length=1000, description="Document description")
    metadata: Optional[Dict[str, str]] = Field(None, description="Custom metadata")


class DocumentResponse(BaseModel):
    """Response schema for document data."""
    
    id: UUID = Field(..., description="Unique document identifier")
    library_id: UUID = Field(..., description="Library ID")
    name: str = Field(..., description="Document name")
    description: Optional[str] = Field(None, description="Document description")
    content_type: str = Field(..., description="MIME type")
    metadata: Dict[str, str] = Field(..., description="Custom metadata")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Statistics
    chunk_count: int = Field(..., description="Number of chunks")
    
    # Processing status
    is_processed: bool = Field(..., description="Whether document is processed")
    processing_status: str = Field(..., description="Processing status")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class DocumentListResponse(BaseModel):
    """Response schema for document listing."""
    
    documents: List[DocumentResponse] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum number of items returned") 