"""
Chunk request/response schemas.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChunkCreateRequest(BaseModel):
    """Request schema for creating a new chunk."""
    
    document_id: UUID = Field(..., description="ID of the document")
    library_id: UUID = Field(..., description="ID of the library")
    text: str = Field(..., min_length=1, description="Chunk text content")
    position: int = Field(default=0, description="Position within document")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Custom metadata")


class ChunkUpdateRequest(BaseModel):
    """Request schema for updating an existing chunk."""
    
    text: Optional[str] = Field(None, min_length=1, description="Chunk text content")
    position: Optional[int] = Field(None, description="Position within document")
    metadata: Optional[Dict[str, str]] = Field(None, description="Custom metadata")


class ChunkResponse(BaseModel):
    """Response schema for chunk data."""
    
    id: UUID = Field(..., description="Unique chunk identifier")
    document_id: UUID = Field(..., description="Document ID")
    library_id: UUID = Field(..., description="Library ID")
    text: str = Field(..., description="Chunk text content")
    text_length: int = Field(..., description="Text length in characters")
    position: int = Field(..., description="Position within document")
    metadata: Dict[str, str] = Field(..., description="Custom metadata")
    
    # Vector embedding info
    embedding_dimension: Optional[int] = Field(None, description="Embedding dimension")
    embedding_model: Optional[str] = Field(None, description="Model used for embedding")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Status
    is_indexed: bool = Field(..., description="Whether chunk is indexed")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class ChunkListResponse(BaseModel):
    """Response schema for chunk listing."""
    
    chunks: List[ChunkResponse] = Field(..., description="List of chunks")
    total: int = Field(..., description="Total number of chunks")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum number of items returned") 