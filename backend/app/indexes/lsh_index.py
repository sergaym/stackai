"""
LSH (Locality Sensitive Hashing) Vector Index

Custom implementation of Locality Sensitive Hashing for approximate similarity search.
Built from scratch without external vector libraries.

Time Complexity:
- Insert: O(L * k) where L is number of hash tables, k is hash function length
- Search: O(L * k + candidates) where candidates is typically << N
- Space: O(N * L) for hash tables + O(N) for vectors

LSH uses multiple hash functions to map similar vectors to the same buckets.
Works especially well for high-dimensional sparse vectors.
"""

import hashlib
from typing import List, Dict, Set, Optional
from uuid import UUID
from collections import defaultdict
import numpy as np

from .base import VectorIndexBase, SearchResult


class LSHHashFamily:
    """Deterministic random projection hash family for cosine similarity."""
    
    def __init__(self, dimension: int, hash_length: int, seed: int = 42):
        self.dimension = dimension
        self.hash_length = hash_length
        
        # FIXED: Deterministic random vectors using fixed seed
        np.random.seed(seed)
        self.random_vectors = np.random.randn(hash_length, dimension).astype(np.float32)
        
        # Normalize random vectors for better hash quality
        for i in range(hash_length):
            norm = np.linalg.norm(self.random_vectors[i])
            if norm > 0:
                self.random_vectors[i] /= norm
    
    def hash_vector(self, vector: np.ndarray) -> str:
        """Hash a vector using random projections with better distribution."""
        # Compute dot products with random vectors
        projections = np.dot(self.random_vectors, vector)
        
        # IMPROVED: Better hash using sign and magnitude
        binary_hash = (projections >= 0).astype(int)
        
        # Use hashlib for better hash distribution
        hash_bytes = binary_hash.tobytes()
        return hashlib.md5(hash_bytes).hexdigest()[:8]  # 8-char hex hash


class LSHIndex(VectorIndexBase):
    """
    Locality Sensitive Hashing (LSH) Index
    
    Uses deterministic random projection LSH for cosine similarity.
    Maps similar vectors to same hash buckets with high probability.
    """
    
    def __init__(self, dimension: int, num_tables: int = 8, hash_length: int = 12):
        super().__init__(dimension)
        self.num_tables = num_tables
        self.hash_length = hash_length
        
        # Create deterministic hash families with different seeds
        self.hash_families = [
            LSHHashFamily(dimension, hash_length, seed=42 + i) 
            for i in range(num_tables)
        ]
        
        # Hash tables: {table_id: {hash_value: set(chunk_ids)}}
        self.hash_tables: List[Dict[str, Set[UUID]]] = [
            defaultdict(set) for _ in range(num_tables)
        ]
        
        # Store vectors for final similarity computation
        self.vectors: Dict[UUID, np.ndarray] = {}
        self.metadata: Dict[UUID, dict] = {}
    
    async def add_vector(self, chunk_id: UUID, vector: np.ndarray, metadata: Optional[dict] = None) -> None:
        """Add vector to LSH index."""
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension {len(vector)} doesn't match index dimension {self.dimension}")
        
        # Normalize vector for cosine similarity
        normalized_vector = self.normalize_vector(vector)
        
        # Store vector and metadata
        self.vectors[chunk_id] = normalized_vector
        self.metadata[chunk_id] = metadata or {}
        
        # Hash vector into all tables
        for table_idx, hash_family in enumerate(self.hash_families):
            hash_value = hash_family.hash_vector(normalized_vector)
            self.hash_tables[table_idx][hash_value].add(chunk_id)
        
        self.size += 1
    
    async def build_index(self) -> None:
        """Build/optimize the index. LSH builds incrementally, so this is a no-op."""
        self._built = True
    
    async def search(self, query_vector: np.ndarray, k: int = 10) -> List[SearchResult]:
        """Perform k-NN search using LSH with simplified fallback."""
        if not self.vectors:
            return []
        
        normalized_query = self.normalize_vector(query_vector)
        
        # Collect candidate vectors from all hash tables
        candidates = set()
        
        for table_idx, hash_family in enumerate(self.hash_families):
            query_hash = hash_family.hash_vector(normalized_query)
            
            # Get all vectors in the same bucket
            if query_hash in self.hash_tables[table_idx]:
                candidates.update(self.hash_tables[table_idx][query_hash])
        
        # SIMPLIFIED: If no candidates, use linear search (KISS principle)
        if not candidates:
            candidates = set(self.vectors.keys())
        
        # Compute exact similarities for candidates
        similarities = []
        for chunk_id in candidates:
            if chunk_id in self.vectors:  # Safety check
                candidate_vector = self.vectors[chunk_id]
                similarity = self.cosine_similarity(normalized_query, candidate_vector)
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
        """Remove vector from LSH index."""
        if chunk_id not in self.vectors:
            return False
        
        # Remove from hash tables
        vector = self.vectors[chunk_id]
        for table_idx, hash_family in enumerate(self.hash_families):
            hash_value = hash_family.hash_vector(vector)
            if hash_value in self.hash_tables[table_idx]:
                self.hash_tables[table_idx][hash_value].discard(chunk_id)
                # Clean up empty buckets
                if not self.hash_tables[table_idx][hash_value]:
                    del self.hash_tables[table_idx][hash_value]
        
        # Remove from storage
        del self.vectors[chunk_id]
        if chunk_id in self.metadata:
            del self.metadata[chunk_id]
        
        self.size -= 1
        return True
    
    def get_index_stats(self) -> dict:
        """Get comprehensive LSH index statistics."""
        # Calculate bucket statistics
        total_buckets = sum(len(table) for table in self.hash_tables)
        avg_bucket_size = 0
        if total_buckets > 0:
            total_entries = sum(
                len(bucket) for table in self.hash_tables 
                for bucket in table.values()
            )
            avg_bucket_size = total_entries / total_buckets if total_buckets > 0 else 0
        
        return {
            "algorithm": "LSH",
            "size": self.size,
            "built": self._built,
            "num_tables": self.num_tables,
            "hash_length": self.hash_length,
            "total_buckets": total_buckets,
            "avg_bucket_size": round(avg_bucket_size, 2),
            "complexity": f"O({self.num_tables}*{self.hash_length} + candidates)"
        } 