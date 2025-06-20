"""
Brute-Force Vector Index

Simple linear search implementation for vector similarity.
Built from scratch without external vector libraries.

Time Complexity:
- Insert: O(1) - Just store the vector
- Search: O(N * d) where N is number of vectors, d is dimension
- Remove: O(1) - Direct dictionary deletion
- Space: O(N * d) for vector storage

Brute-force computes cosine similarity with every vector and returns top k.
Guarantees exact results, simple implementation, excellent baseline for validation.
"""

from typing import List, Dict, Optional
from uuid import UUID
import numpy as np

from .base import VectorIndexBase, SearchResult


class BruteForceIndex(VectorIndexBase):
    """
    Brute-Force Vector Index
    
    Simple linear search that computes similarity with all vectors.
    - Exact results (no approximation)
    - O(N*d) search complexity
    - Perfect baseline for algorithm validation
    - Suitable for small datasets or ground truth comparison
    """
    
    def __init__(self, dimension: int):
        super().__init__(dimension)
        # Simple storage: chunk_id -> normalized vector
        self.vectors: Dict[UUID, np.ndarray] = {}
        self.metadata: Dict[UUID, dict] = {}
    
    async def add_vector(self, chunk_id: UUID, vector: np.ndarray, metadata: Optional[dict] = None) -> None:
        """Add vector to brute-force index with validation."""
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension {len(vector)} doesn't match index dimension {self.dimension}")
        
        # Handle edge case: zero vector
        if np.allclose(vector, 0):
            # Store zero vector as-is (will have zero similarity with everything)
            normalized_vector = vector.copy()
        else:
            # Normalize vector for cosine similarity
            normalized_vector = self.normalize_vector(vector)
        
        # Store vector and metadata
        is_new_vector = chunk_id not in self.vectors
        self.vectors[chunk_id] = normalized_vector
        self.metadata[chunk_id] = metadata or {}
        
        # Update size only if it's a new vector
        if is_new_vector:
            self.size += 1
    
    async def build_index(self) -> None:
        """Build index. Brute-force needs no building - just mark as built."""
        self._built = True
    
    async def search(self, query_vector: np.ndarray, k: int = 10) -> List[SearchResult]:
        """Perform k-NN search using brute-force linear scan with exact results."""
        if not self.vectors:
            return []
        
        # Handle edge case: k larger than available vectors
        k = min(k, len(self.vectors))
        
        # Normalize query vector
        if np.allclose(query_vector, 0):
            normalized_query = query_vector.copy()
        else:
            normalized_query = self.normalize_vector(query_vector)
        
        # Compute similarity with every vector (brute-force)
        similarities = []
        for chunk_id, vector in self.vectors.items():
            similarity = self.cosine_similarity(normalized_query, vector)
            distance = 1.0 - similarity
            similarities.append((chunk_id, similarity, distance))
        
        # Sort by similarity (descending) and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for chunk_id, similarity, distance in similarities[:k]:
            results.append(SearchResult(
                chunk_id=chunk_id,
                similarity_score=similarity,
                distance=distance
            ))
        
        return results
    
    async def remove_vector(self, chunk_id: UUID) -> bool:
        """Remove vector from brute-force index."""
        if chunk_id not in self.vectors:
            return False
        
        # Remove from storage
        del self.vectors[chunk_id]
        if chunk_id in self.metadata:
            del self.metadata[chunk_id]
        
        self.size -= 1
        return True
    
    def get_index_stats(self) -> dict:
        """Get comprehensive brute-force index statistics."""
        # Calculate vector statistics if we have data
        stats = {
            "algorithm": "Brute-Force",
            "size": self.size,
            "built": self._built,
            "dimension": self.dimension,
            "complexity": f"O({self.size} * {self.dimension}) per search",
            "guarantees": "Exact results (no approximation)"
        }
        
        if self.vectors:
            # Calculate some basic vector statistics
            vector_norms = [np.linalg.norm(vec) for vec in self.vectors.values()]
            stats.update({
                "avg_vector_norm": round(float(np.mean(vector_norms)), 4),
                "min_vector_norm": round(float(np.min(vector_norms)), 4), 
                "max_vector_norm": round(float(np.max(vector_norms)), 4),
                "memory_usage_mb": round(self.size * self.dimension * 4 / 1024 / 1024, 2)  # float32 = 4 bytes
            })
        
        return stats 