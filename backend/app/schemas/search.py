"""Advanced search schemas with custom vector indexing support."""

from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request schema for vector similarity search."""
    
    query: str = Field(..., min_length=1, description="Search query text")
    library_id: Optional[UUID] = Field(None, description="Optional library to search within")
    k: int = Field(default=3, ge=1, le=100, description="Number of results to return")


class SearchResult(BaseModel):
    """Individual search result."""
    
    chunk_id: UUID
    text: str
    similarity_score: float
    document_name: str


class SearchResponse(BaseModel):
    """Response schema for search results."""
    
    query: str
    results: List[SearchResult]
    total_results: int
    algorithm_used: Optional[str] = Field(None, description="Vector index algorithm used")
    index_stats: Optional[Dict[str, Any]] = Field(None, description="Index statistics") 