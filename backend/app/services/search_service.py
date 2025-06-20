"""
Search Service - Orchestrates Vector Search Workflow

Handles the complete search workflow:
1. Embed query text
2. Query index service
3. Fetch chunk data from database
4. Return formatted results
"""

from typing import List, Dict, Optional
from uuid import UUID

from app.services.index_service import IndexService
from app.services.embedding_service import generate_query_embedding
from app.repositories.async_chunk_repository import AsyncChunkRepository
from app.repositories.async_document_repository import AsyncDocumentRepository
from app.indexes.index_manager import IndexType


class SearchResult:
    """Search result data structure."""
    
    def __init__(self, chunk_id: UUID, text: str, similarity_score: float, 
                 document_name: str, metadata: Optional[dict] = None):
        self.chunk_id = chunk_id
        self.text = text
        self.similarity_score = similarity_score
        self.document_name = document_name
        self.metadata = metadata or {}


class SearchService:
    """
    Search service orchestrating the complete search workflow.    
    """
    
    def __init__(self, index_service: IndexService, 
                 chunk_repository: AsyncChunkRepository,
                 document_repository: AsyncDocumentRepository):
        self.index_service = index_service
        self.chunk_repository = chunk_repository
        self.document_repository = document_repository
    
    async def search_by_text(self, library_id: UUID, query_text: str, 
                            k: int = 10, index_type: Optional[IndexType] = None) -> List[SearchResult]:
        """
        Search by text query.
        
        Args:
            library_id: Library to search in
            query_text: Text query to search for
            k: Number of results to return
            index_type: Optional specific index algorithm to use
            
        Returns:
            List of search results
        """
        # Early return for empty query
        if not query_text.strip():
            return []
        
        # Step 1: Embed the query
        query_embedding = await generate_query_embedding(query_text)
        if not query_embedding:
            return []
        
        # Step 2: Search using embedding
        return await self.search_by_embedding(library_id, query_embedding, k, index_type)
    
    async def search_by_embedding(self, library_id: UUID, query_embedding: List[float],
                                 k: int = 10, index_type: Optional[IndexType] = None) -> List[SearchResult]:
        """
        Search by embedding vector.
        
        Args:
            library_id: Library to search in
            query_embedding: Embedding vector to search for
            k: Number of results to return
            index_type: Optional specific index algorithm to use
            
        Returns:
            List of search results
        """
        # Early return for empty embedding
        if not query_embedding:
            return []
        
        # Step 1: Query index service (simplified - no pre-filtering)
        index_results = await self.index_service.query(
            library_id=library_id,
            query_embedding=query_embedding,
            k=k,
            index_type=index_type
        )
        
        if not index_results:
            return []
        
        # Step 2: Fetch chunk data from database (batch operation)
        search_results = await self._fetch_chunk_details_batch(index_results)
        
        return search_results
    
    async def _fetch_chunk_details_batch(self, index_results: List[tuple]) -> List[SearchResult]:
        """
        Fetch chunk details from database efficiently using batch operations.
        
        Args:
            index_results: List of (chunk_id, similarity_score) tuples
            
        Returns:
            List of complete search results
        """
        if not index_results:
            return []
        
        # Extract chunk IDs and create score mapping
        chunk_ids = [chunk_id for chunk_id, _ in index_results]
        score_map = {chunk_id: score for chunk_id, score in index_results}
        
        search_results = []
        
        # Fetch chunks (could be optimized with batch fetch if repository supports it)
        for chunk_id in chunk_ids:
            try:
                # Fetch chunk
                chunk = await self.chunk_repository.get_by_id(chunk_id)
                if not chunk:
                    continue
                
                # Fetch document for name (cached or batch fetched in production)
                document = await self.document_repository.get_by_id(chunk.document_id)
                document_name = document.name if document else "Unknown Document"
                
                # Create search result
                result = SearchResult(
                    chunk_id=chunk.id,
                    text=chunk.text,
                    similarity_score=score_map[chunk_id],
                    document_name=document_name,
                    metadata=chunk.metadata_ or {}
                )
                
                search_results.append(result)
                
            except Exception:
                # Skip failed chunks (production would log this)
                continue
        
        return search_results
    
    async def get_search_stats(self, library_id: UUID) -> Dict[str, any]:
        """Get search statistics for a library."""
        return self.index_service.get_library_stats(library_id) 