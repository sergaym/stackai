"""
Async Document Repository.

Simple document database operations.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Document


class AsyncDocumentRepository:
    """Simple async repository for Document operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, document: Document) -> Document:
        """Create a new document."""
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        
        # Re-fetch with relationships loaded
        return await self.get_by_id(document.id)
    
    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID."""
        stmt = (
            select(Document)
            .options(selectinload(Document.chunks))
            .where(Document.id == document_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_library_id(self, library_id: UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get all documents for a library."""
        stmt = (
            select(Document)
            .options(selectinload(Document.chunks))
            .where(Document.library_id == library_id)
            .offset(skip)
            .limit(limit)
            .order_by(Document.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get all documents."""
        stmt = (
            select(Document)
            .options(selectinload(Document.chunks))
            .offset(skip)
            .limit(limit)
            .order_by(Document.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """Get total document count."""
        stmt = select(func.count(Document.id))
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def count_by_library_id(self, library_id: UUID) -> int:
        """Count documents in a library."""
        stmt = select(func.count(Document.id)).where(Document.library_id == library_id)
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def update(self, document_id: UUID, update_data: dict) -> Optional[Document]:
        """Update document by ID."""
        filtered_data = {k: v for k, v in update_data.items() if v is not None}
        if not filtered_data:
            return await self.get_by_id(document_id)
        
        stmt = (
            update(Document)
            .where(Document.id == document_id)
            .values(**filtered_data)
            .returning(Document)
        )
        result = await self.session.execute(stmt)
        updated_document = result.scalar_one_or_none()
        
        if updated_document:
            # Re-fetch with relationships loaded
            return await self.get_by_id(document_id)
        return None
    
    async def delete(self, document_id: UUID) -> bool:
        """Delete document by ID."""
        stmt = delete(Document).where(Document.id == document_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0 