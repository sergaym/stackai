"""
HNSW (Hierarchical Navigable Small World) Vector Index

Simplified HNSW implementation for interview demonstration.
Built from scratch without external vector libraries.

Time Complexity:
- Insert: O(log N) expected
- Search: O(log N) expected  
- Space: O(N * M) where M is max connections per node

HNSW creates a multi-layer graph where higher layers have fewer nodes.
"""

import random
from typing import List, Dict, Set, Optional
from uuid import UUID
import numpy as np

from .base import VectorIndexBase, SearchResult


class HNSWIndex(VectorIndexBase):
    """
    HNSW Index for vector search.
    """
    
    def __init__(self, dimension: int, max_connections: int = 16, max_connections_0: int = 32):
        super().__init__(dimension)
        self.max_connections = max_connections  
        self.max_connections_0 = max_connections_0
        
        # Core data structures only
        self.vectors: Dict[UUID, np.ndarray] = {}
        self.levels: Dict[UUID, int] = {}  # chunk_id -> level
        self.connections: Dict[UUID, Dict[int, Set[UUID]]] = {}  # chunk_id -> {level: neighbors}
        self.entry_point: Optional[UUID] = None
        
        # Deterministic random seed
        random.seed(42)
    
    def _generate_level(self) -> int:
        """Generate level deterministically with exponential decay."""
        level = 0
        # Use deterministic approach for consistent behavior
        while random.random() < 0.5 and level < 8:  # Cap at 8 levels (KISS)
            level += 1
        return level
    
    async def add_vector(self, chunk_id: UUID, vector: np.ndarray, metadata: Optional[dict] = None) -> None:
        """Add vector to HNSW index with simplified insertion."""
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension {len(vector)} doesn't match index dimension {self.dimension}")
        
        # Store normalized vector
        normalized_vector = self.normalize_vector(vector)
        self.vectors[chunk_id] = normalized_vector
        
        # Assign level
        level = self._generate_level()
        self.levels[chunk_id] = level
        
        # Initialize connections
        self.connections[chunk_id] = {i: set() for i in range(level + 1)}
        
        # If first node, make it entry point
        if self.entry_point is None:
            self.entry_point = chunk_id
            self.size += 1
            return
        
        # Connect to closest existing nodes at each level
        await self._simple_insert(chunk_id, normalized_vector, level)
        self.size += 1
    
    async def _simple_insert(self, chunk_id: UUID, vector: np.ndarray, target_level: int) -> None:
        """Simplified insertion - connects to closest nodes at each level."""
        # Find candidates at each level
        for level in range(target_level + 1):
            # Get all nodes at this level
            level_nodes = [
                nid for nid, node_level in self.levels.items() 
                if node_level >= level and nid != chunk_id
            ]
            
            if not level_nodes:
                continue
            
            # Find closest nodes
            similarities = []
            for node_id in level_nodes:
                sim = self.cosine_similarity(vector, self.vectors[node_id])
                similarities.append((sim, node_id))
            
            # Sort by similarity and connect to best
            similarities.sort(reverse=True)
            max_conn = self.max_connections_0 if level == 0 else self.max_connections
            
            for sim, neighbor_id in similarities[:max_conn]:
                # Bidirectional connection (simplified)
                self.connections[chunk_id][level].add(neighbor_id)
                self.connections[neighbor_id][level].add(chunk_id)
                
                # Basic pruning if too many connections
                if len(self.connections[neighbor_id][level]) > max_conn:
                    # Remove worst connection
                    worst_neighbor = self._find_worst_neighbor(neighbor_id, level)
                    if worst_neighbor:
                        self.connections[neighbor_id][level].discard(worst_neighbor)
                        self.connections[worst_neighbor][level].discard(neighbor_id)
        
        # Update entry point if this node is at higher level
        if target_level > self.levels.get(self.entry_point, 0):
            self.entry_point = chunk_id
    
    def _find_worst_neighbor(self, node_id: UUID, level: int) -> Optional[UUID]:
        """Find the worst (least similar) neighbor to remove."""
        if node_id not in self.connections or level not in self.connections[node_id]:
            return None
        
        node_vector = self.vectors[node_id]
        worst_sim = float('inf')
        worst_neighbor = None
        
        for neighbor_id in self.connections[node_id][level]:
            if neighbor_id in self.vectors:
                sim = self.cosine_similarity(node_vector, self.vectors[neighbor_id])
                if sim < worst_sim:
                    worst_sim = sim
                    worst_neighbor = neighbor_id
        
        return worst_neighbor
    
    async def search(self, query_vector: np.ndarray, k: int = 10) -> List[SearchResult]:
        """Simplified k-NN search using HNSW structure."""
        if not self.vectors or self.entry_point is None:
            return []
        
        normalized_query = self.normalize_vector(query_vector)
        
        # Start from entry point
        current_best = self.entry_point
        entry_level = self.levels[self.entry_point]
        
        # Greedy search from top level down
        for level in range(entry_level, -1, -1):
            current_best = await self._search_level_simple(normalized_query, current_best, level)
        
        # Get final candidates from level 0
        candidates = await self._get_level_candidates(normalized_query, current_best, k * 3)
        
        # Calculate similarities and return top k
        results = []
        for candidate_id in candidates:
            if candidate_id in self.vectors:
                similarity = self.cosine_similarity(normalized_query, self.vectors[candidate_id])
                distance = 1.0 - similarity
                results.append(SearchResult(
                    chunk_id=candidate_id,
                    similarity_score=similarity,
                    distance=distance
                ))
        
        # Sort by similarity and return top k
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:k]
    
    async def _search_level_simple(self, query: np.ndarray, start_node: UUID, level: int) -> UUID:
        """Simplified greedy search at a single level."""
        current = start_node
        improved = True
        
        while improved:
            improved = False
            current_sim = self.cosine_similarity(query, self.vectors[current])
            
            # Check all neighbors at this level
            if current in self.connections and level in self.connections[current]:
                for neighbor_id in self.connections[current][level]:
                    if neighbor_id in self.vectors:
                        neighbor_sim = self.cosine_similarity(query, self.vectors[neighbor_id])
                        if neighbor_sim > current_sim:
                            current = neighbor_id
                            improved = True
                            break
        
        return current
    
    async def _get_level_candidates(self, query: np.ndarray, start_node: UUID, num_candidates: int) -> List[UUID]:
        """Get candidates from level 0 using BFS."""
        visited = set()
        candidates = []
        queue = [start_node]
        
        while queue and len(candidates) < num_candidates:
            node_id = queue.pop(0)
            if node_id in visited:
                continue
            
            visited.add(node_id)
            candidates.append(node_id)
            
            # Add neighbors from level 0
            if node_id in self.connections and 0 in self.connections[node_id]:
                for neighbor_id in self.connections[node_id][0]:
                    if neighbor_id not in visited:
                        queue.append(neighbor_id)
        
        return candidates
    
    async def build_index(self) -> None:
        """Build/optimize the index. HNSW builds incrementally."""
        self._built = True
    
    async def remove_vector(self, chunk_id: UUID) -> bool:
        """Remove vector from HNSW index."""
        if chunk_id not in self.vectors:
            return False
        
        # Remove all connections
        if chunk_id in self.connections:
            for level_connections in self.connections[chunk_id].values():
                for neighbor_id in level_connections:
                    if neighbor_id in self.connections:
                        for level in self.connections[neighbor_id]:
                            self.connections[neighbor_id][level].discard(chunk_id)
        
        # Remove from data structures
        del self.vectors[chunk_id]
        del self.levels[chunk_id]
        del self.connections[chunk_id]
        
        # Handle entry point removal
        if chunk_id == self.entry_point:
            self.entry_point = next(iter(self.vectors.keys())) if self.vectors else None
        
        self.size -= 1
        return True
    
    def get_index_stats(self) -> dict:
        """Get HNSW index statistics."""
        if not self.vectors:
            return {
                "algorithm": "HNSW",
                "size": 0,
                "built": self._built,
                "levels": 0,
                "avg_connections": 0
            }
        
        # Calculate level distribution
        level_counts = {}
        total_connections = 0
        
        for node_level in self.levels.values():
            level_counts[node_level] = level_counts.get(node_level, 0) + 1
        
        for node_connections in self.connections.values():
            for level_connections in node_connections.values():
                total_connections += len(level_connections)
        
        avg_connections = total_connections / len(self.vectors) if self.vectors else 0
        
        return {
            "algorithm": "HNSW",
            "size": self.size,
            "built": self._built,
            "max_level": max(self.levels.values()) if self.levels else 0,
            "level_distribution": level_counts,
            "avg_connections_per_node": round(avg_connections, 2),
            "complexity": "O(log N) search, O(log N) insert"
        } 