"""Simple document service."""

from typing import List, Optional
from uuid import UUID

from app.db.models import Document
from app.repositories.async_document_repository import AsyncDocumentRepository
from app.repositories.async_library_repository import AsyncLibraryRepository


class DocumentService:
    """Simple document service with library validation."""
    
    def __init__(self, document_repository: AsyncDocumentRepository, library_repository: AsyncLibraryRepository):
        self.document_repository = document_repository
        self.library_repository = library_repository
    
    async def create_document(self, library_id: UUID, name: str, description: Optional[str] = None, 
                           content_type: str = "text/plain", metadata: Optional[dict] = None) -> Document:
        """Create a new document with library validation."""
        library = await self.library_repository.get_by_id(library_id)
        if not library:
            raise ValueError(f"Library with ID {library_id} not found")
        
        document = Document(
            library_id=library_id,
            name=name,
            description=description,
            content_type=content_type,
            metadata_=metadata or {}
        )
        return await self.document_repository.create(document)
    
    async def get_document(self, document_id: UUID) -> Optional[Document]:
        """Get a document by ID."""
        return await self.document_repository.get_by_id(document_id)
    
    async def list_documents(self, library_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[Document]:
        """List documents with optional filtering."""
        if library_id:
            return await self.document_repository.get_by_library_id(library_id, skip=skip, limit=limit)
        return await self.document_repository.get_all(skip=skip, limit=limit)
    
    async def count_documents(self, library_id: Optional[UUID] = None) -> int:
        """Count documents with optional library filtering."""
        if library_id:
            return await self.document_repository.count_by_library_id(library_id)
        return await self.document_repository.count()
    
    async def update_document(self, document_id: UUID, **updates) -> Optional[Document]:
        """Update a document."""
        return await self.document_repository.update(document_id, updates)
    
    async def delete_document(self, document_id: UUID) -> Optional[dict]:
        """Delete a document and return success message."""
        # Check if document exists
        document = await self.document_repository.get_by_id(document_id)
        if not document:
            return None
        
        # Delete document (cascades to chunks)
        deleted = await self.document_repository.delete(document_id)
        
        if not deleted:
            return None
        
        return {
            "message": f"Document '{document.name}' deleted successfully"
        } 