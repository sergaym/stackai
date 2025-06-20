"""
Async Library Repository.

Simple, direct library database operations.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Library


class AsyncLibraryRepository:
    """Simple async repository for Library operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, library: Library) -> Library:
        """Create a new library."""
        self.session.add(library)
        await self.session.flush()
        await self.session.refresh(library)
        
        # Re-fetch with relationships loaded
        return await self.get_by_id(library.id)
    
    async def get_by_id(self, library_id: UUID) -> Optional[Library]:
        """Get library by ID."""
        stmt = (
            select(Library)
            .options(
                selectinload(Library.documents),
                selectinload(Library.chunks)
            )
            .where(Library.id == library_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Library]:
        """Get library by name."""
        stmt = select(Library).where(Library.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Library]:
        """Get all libraries with pagination."""
        stmt = (
            select(Library)
            .options(
                selectinload(Library.documents),
                selectinload(Library.chunks)
            )
            .offset(skip)
            .limit(limit)
            .order_by(Library.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """Get total count of libraries."""
        from sqlalchemy import func
        stmt = select(func.count(Library.id))
        result = await self.session.execute(stmt)
        return result.scalar()
    
    async def update(self, library_id: UUID, update_data: dict) -> Optional[Library]:
        """Update library by ID."""
        filtered_data = {k: v for k, v in update_data.items() if v is not None}
        if not filtered_data:
            return await self.get_by_id(library_id)
        
        stmt = (
            update(Library)
            .where(Library.id == library_id)
            .values(**filtered_data)
            .returning(Library)
        )
        result = await self.session.execute(stmt)
        updated_library = result.scalar_one_or_none()
        
        if updated_library:
            # Re-fetch with relationships loaded
            return await self.get_by_id(library_id)
        return None
    
    async def delete(self, library_id: UUID) -> bool:
        """Delete library by ID."""
        stmt = delete(Library).where(Library.id == library_id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0 