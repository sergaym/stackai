"""
Simple Chunk Repository.

Only the methods we actually use.
"""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from app.db.models import Chunk


class AsyncChunkRepository:
    """Simple async repository for Chunk operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, chunk: Chunk) -> Chunk:
        """Create a new chunk."""
        self.session.add(chunk)
        await self.session.flush()
        await self.session.refresh(chunk)
        return chunk
    
    async def get_by_id(self, chunk_id: UUID) -> Optional[Chunk]:
        """Get chunk by ID."""
        stmt = select(Chunk).where(Chunk.id == chunk_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_document_id(self, document_id: UUID, skip: int = 0, limit: int = 100) -> List[Chunk]:
        """Get chunks for a document."""
        stmt = (
            select(Chunk)
            .where(Chunk.document_id == document_id)
            .offset(skip)
            .limit(limit)
            .order_by(Chunk.position)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_library_id(self, library_id: UUID, skip: int = 0, limit: int = 100) -> List[Chunk]:
        """Get chunks for a library."""
        stmt = (
            select(Chunk)
            .where(Chunk.library_id == library_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Chunk]:
        """Get all chunks."""
        stmt = (
            select(Chunk)
            .offset(skip)
            .limit(limit)
            .order_by(Chunk.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """Get total chunk count."""
        stmt = select(func.count(Chunk.id))
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def count_by_library_id(self, library_id: UUID) -> int:
        """Count chunks in a library."""
        stmt = select(func.count(Chunk.id)).where(Chunk.library_id == library_id)
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def count_by_document_id(self, document_id: UUID) -> int:
        """Count chunks in a document."""
        stmt = select(func.count(Chunk.id)).where(Chunk.document_id == document_id)
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def update(self, chunk_id: UUID, update_data: dict) -> Optional[Chunk]:
        """Update chunk by ID."""
        filtered_data = {k: v for k, v in update_data.items() if v is not None}
        if not filtered_data:
            return await self.get_by_id(chunk_id)
        
        stmt = (
            update(Chunk)
            .where(Chunk.id == chunk_id)
            .values(**filtered_data)
            .returning(Chunk)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete(self, chunk_id: UUID) -> bool:
        """Delete chunk by ID."""
        stmt = delete(Chunk).where(Chunk.id == chunk_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def vector_search(self, query_embedding: List[float], library_id: Optional[UUID] = None, k: int = 10) -> List[Tuple[Chunk, float]]:
        """Vector similarity search"""
        # Get indexed chunks
        stmt = select(Chunk).where(Chunk.is_indexed == True)
        
        if library_id:
            stmt = stmt.where(Chunk.library_id == library_id)
        
        result = await self.session.execute(stmt)
        chunks = list(result.scalars().all())
        
        # Simple cosine similarity - KISS style
        results = []
        query_vec = np.array(query_embedding, dtype=np.float32)
        
        for chunk in chunks:
            if chunk.embedding:
                chunk_vec = np.array(chunk.embedding, dtype=np.float32)
                # Simple dot product similarity (vectors are already normalized by Cohere)
                similarity = float(np.dot(query_vec, chunk_vec))
                results.append((chunk, similarity))
        
        # Return top k results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k] 