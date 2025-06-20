"""
Base Vector Index Interface

Abstract base class for all vector indexing algorithms.
Defines the contract that all custom indexes must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any
from uuid import UUID
import numpy as np
from dataclasses import dataclass


@dataclass
class IndexedVector:
    """Vector with associated metadata for indexing."""
    chunk_id: UUID
    vector: np.ndarray
    metadata: Optional[dict] = None


@dataclass
class SearchResult:
    """Result from vector similarity search."""
    chunk_id: UUID
    similarity_score: float
    distance: float


class VectorIndexBase(ABC):
    """Abstract base class for vector indexes."""
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.size = 0
        self._built = False
    
    @abstractmethod
    async def add_vector(self, chunk_id: UUID, vector: np.ndarray, metadata: Optional[dict] = None) -> None:
        """Add a vector to the index."""
        pass
    
    @abstractmethod
    async def build_index(self) -> None:
        """Build/optimize the index structure."""
        pass
    
    @abstractmethod
    async def search(self, query_vector: np.ndarray, k: int = 10) -> List[SearchResult]:
        """Perform k-NN search."""
        pass
    
    @abstractmethod
    async def remove_vector(self, chunk_id: UUID) -> bool:
        """Remove a vector from the index."""
        pass
    
    @abstractmethod
    def get_index_stats(self) -> dict:
        """Get index statistics and complexity info."""
        pass
    
    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(dot_product / (norm_a * norm_b))
    
    @staticmethod
    def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
        """Compute Euclidean distance between two vectors."""
        return float(np.linalg.norm(a - b))
    
    @staticmethod
    def normalize_vector(vector: np.ndarray) -> np.ndarray:
        """L2 normalize a vector."""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm 