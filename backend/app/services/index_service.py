"""
Index Service - In-Memory Vector Indexing

Manages in-memory vector indexes per library.
Handles adding/removing chunks and provides efficient k-NN search.
"""

from typing import Dict, Optional, Tuple, List
from uuid import UUID
import numpy as np

from app.indexes.index_manager import VectorIndexManager, IndexType
from app.core.config import settings


class IndexService:
    """
    In-memory vector indexing service.
    """
    
    def __init__(self):
        # Per-library index managers (single source of truth)
        self._library_indexes: Dict[UUID, VectorIndexManager] = {}
        # Configuration
        self._default_index_type = self._get_default_index_type()
        
    def _get_default_index_type(self) -> IndexType:
        """Get default index type from configuration."""
        index_name = getattr(settings, 'default_vector_index', 'hnsw').lower()
        return {
            'hnsw': IndexType.HNSW,
            'lsh': IndexType.LSH,
            'brute_force': IndexType.BRUTE_FORCE
        }.get(index_name, IndexType.HNSW)
    
    def _get_or_create_index(self, library_id: UUID, index_type: Optional[IndexType] = None) -> VectorIndexManager:
        """Get or create index manager for a library with specific algorithm."""
        # Create a composite key for library + algorithm
        index_key = f"{library_id}_{(index_type or self._default_index_type).value}"
        
        if index_key not in self._library_indexes:
            self._library_indexes[index_key] = VectorIndexManager(
                dimension=settings.embedding_dimension,
                index_type=index_type or self._default_index_type
            )
        return self._library_indexes[index_key]
    
    def _get_default_index_for_library(self, library_id: UUID) -> Optional[VectorIndexManager]:
        """Get the default index for a library."""
        default_key = f"{library_id}_{self._default_index_type.value}"
        return self._library_indexes.get(default_key)
    
    async def add_chunk(self, library_id: UUID, chunk_id: UUID, 
                       embedding: List[float], metadata: Optional[dict] = None, 
                       build_all_algorithms: bool = False) -> bool:
        """
        Add chunk to library indexes.
        
        Args:
            library_id: Library identifier
            chunk_id: Chunk identifier  
            embedding: Vector embedding
            metadata: Optional chunk metadata
            build_all_algorithms: If True, adds to all algorithms (for comparison)
                                 If False, only adds to default algorithm (production efficient)
            
        Returns:
            True if added successfully
        """
        if not embedding:
            return False
            
        try:
            vector = np.array(embedding, dtype=np.float32)
            
            if build_all_algorithms:
                # Add to all index types for algorithm comparison
                for index_type in IndexType:
                    index_manager = self._get_or_create_index(library_id, index_type)
                    await index_manager.add_vector(chunk_id, vector, metadata)
            else:
                # Only add to default index (efficient for startup)
                index_manager = self._get_or_create_index(library_id, self._default_index_type)
                await index_manager.add_vector(chunk_id, vector, metadata)
            
            return True
            
        except Exception:
            return False
    
    async def remove_chunk(self, library_id: UUID, chunk_id: UUID) -> bool:
        """
        Remove chunk from all library indexes.
        
        Args:
            library_id: Library identifier
            chunk_id: Chunk identifier
            
        Returns:
            True if removed successfully from any index
        """
        try:
            success = False
            
            # Remove from all index types for this library
            for index_type in IndexType:
                index_key = f"{library_id}_{index_type.value}"
                if index_key in self._library_indexes:
                    index_manager = self._library_indexes[index_key]
                    if await index_manager.remove_vector(chunk_id):
                        success = True
            
            return success
            
        except Exception:
            return False
    
    async def query(self, library_id: UUID, query_embedding: List[float], 
                   k: int = 10, index_type: Optional[IndexType] = None) -> List[Tuple[UUID, float]]:
        """
        Query specific library index for similar chunks.
        
        Args:
            library_id: Library identifier
            query_embedding: Query vector
            k: Number of results to return
            index_type: Specific index type to use (defaults to configured default)
            
        Returns:
            List of (chunk_id, similarity_score) tuples
        """
        if not query_embedding:
            return []
            
        try:
            # Use specified index type or default
            target_index_type = index_type or self._default_index_type
            index_manager = self._get_or_create_index(library_id, target_index_type)
            
            query_vector = np.array(query_embedding, dtype=np.float32)
            
            # Search with the specific index
            results = await index_manager.search(query_vector, k)
            
            # Return results as tuples
            return [(result.chunk_id, result.similarity_score) for result in results]
            
        except Exception:
            return []
    
    async def build_library_index(self, library_id: UUID, 
                                 index_type: Optional[IndexType] = None,
                                 build_all_algorithms: bool = False) -> bool:
        """
        Build/optimize specific index for a library.
        
        Args:
            library_id: Library identifier
            index_type: Specific index type to build
            build_all_algorithms: If True, builds all algorithms (for comparison)
            
        Returns:
            True if built successfully
        """
        try:
            if index_type:
                # Build specific index type
                index_manager = self._get_or_create_index(library_id, index_type)
                await index_manager.build_index()
            elif build_all_algorithms:
                # Build all index types for this library
                for idx_type in IndexType:
                    index_key = f"{library_id}_{idx_type.value}"
                    if index_key in self._library_indexes:
                        await self._library_indexes[index_key].build_index()
            else:
                # Build only default index (efficient for startup)
                default_index = self._get_default_index_for_library(library_id)
                if default_index:
                    await default_index.build_index()
            
            return True
            
        except Exception:
            return False
    
    def get_library_stats(self, library_id: UUID) -> Dict[str, any]:
        """Get statistics for a library's indexes."""
        default_index = self._get_default_index_for_library(library_id)
        if not default_index:
            return {"error": "Library not found"}
        
        return {
            "library_id": str(library_id),
            "total_chunks": default_index.size,
            "index_type": default_index.index_type.value,
            "index_stats": default_index.get_index_stats()
        }
    
    async def remove_library_index(self, library_id: UUID) -> bool:
        """Remove all indexes for a library."""
        try:
            removed = False
            # Remove all index types for this library
            for index_type in IndexType:
                index_key = f"{library_id}_{index_type.value}"
                if index_key in self._library_indexes:
                    del self._library_indexes[index_key]
                    removed = True
            return removed
        except Exception:
            return False 