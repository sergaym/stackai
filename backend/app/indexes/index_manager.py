"""
Vector Index Manager

Manages a single vector indexing algorithm per library.
Provides a unified interface for different indexing strategies.
"""

from enum import Enum
from typing import List, Optional, Any
from uuid import UUID
import numpy as np

from .base import VectorIndexBase, SearchResult
from .hnsw_index import HNSWIndex
from .lsh_index import LSHIndex
from .brute_force_index import BruteForceIndex


class IndexType(Enum):
    """Available vector index types."""
    HNSW = "hnsw"
    LSH = "lsh"
    BRUTE_FORCE = "brute_force"


class VectorIndexManager:
    """
    Manager for a single vector indexing algorithm.
    
    Simplified to use one index type per instance following KISS principles.
    """
    
    def __init__(self, dimension: int, index_type: IndexType = IndexType.HNSW):
        self.dimension = dimension
        self.index_type = index_type
        self.index: VectorIndexBase = self._create_index(index_type)
        
    def _create_index(self, index_type: IndexType) -> VectorIndexBase:
        """Create a new index of the specified type."""
        if index_type == IndexType.HNSW:
            return HNSWIndex(
                dimension=self.dimension,
                max_connections=16,
                max_connections_0=32
            )
        elif index_type == IndexType.LSH:
            return LSHIndex(
                dimension=self.dimension,
                num_tables=10,
                hash_length=10
            )
        elif index_type == IndexType.BRUTE_FORCE:
            return BruteForceIndex(
                dimension=self.dimension
            )
        
        # This should never be reached with valid IndexType enum values
        raise ValueError(f"Unknown index type: {index_type}")
    
    @property
    def size(self) -> int:
        """Get the number of vectors in the index."""
        return self.index.size
    
    async def add_vector(self, chunk_id: UUID, vector: np.ndarray, 
                        metadata: Optional[dict] = None) -> None:
        """Add vector to the index."""
        await self.index.add_vector(chunk_id, vector, metadata)
    
    async def build_index(self) -> None:
        """Build/optimize the index."""
        await self.index.build_index()
    
    async def search(self, query_vector: np.ndarray, k: int = 10) -> List[SearchResult]:
        """Search using the index."""
        return await self.index.search(query_vector, k)
    
    async def remove_vector(self, chunk_id: UUID) -> bool:
        """Remove vector from the index."""
        return await self.index.remove_vector(chunk_id)
    
    def get_index_stats(self) -> dict:
        """Get statistics for the index."""
        stats = self.index.get_index_stats()
        stats.update({
            "index_type": self.index_type.value,
            "dimension": self.dimension
        })
        return stats 