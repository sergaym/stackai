"""
Library request/response schemas.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class LibraryCreateRequest(BaseModel):
    """Request schema for creating a new library."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Library name")
    description: Optional[str] = Field(None, max_length=1000, description="Library description")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Custom metadata")


class LibraryUpdateRequest(BaseModel):
    """Request schema for updating an existing library."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Library name")
    description: Optional[str] = Field(None, max_length=1000, description="Library description")
    metadata: Optional[Dict[str, str]] = Field(None, description="Custom metadata")


class LibraryResponse(BaseModel):
    """Response schema for library data."""
    
    id: UUID = Field(..., description="Unique library identifier")
    name: str = Field(..., description="Library name")
    description: Optional[str] = Field(None, description="Library description")
    metadata: Dict[str, str] = Field(..., description="Custom metadata")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Statistics
    document_count: int = Field(..., description="Number of documents in library")
    chunk_count: int = Field(..., description="Number of chunks in library")


class LibraryListResponse(BaseModel):
    """Response schema for library listing."""
    
    libraries: List[LibraryResponse] = Field(..., description="List of libraries")
    total: int = Field(..., description="Total number of libraries")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum number of items returned")


class LibraryDeleteResponse(BaseModel):
    """Response schema for library deletion operations."""
    
    message: str = Field(..., description="Deletion confirmation message") 