"""
Chunk business logic service.
"""

from typing import List, Optional, Tuple
from uuid import UUID

from app.db.models import Chunk
from app.repositories.async_chunk_repository import AsyncChunkRepository
from app.repositories.async_document_repository import AsyncDocumentRepository
from app.repositories.async_library_repository import AsyncLibraryRepository
from app.services.embedding_service import generate_embeddings
from app.core.config import settings


class ChunkService:
    """Simple chunk service with validation and auto-embedding."""
    
    def __init__(self, chunk_repository: AsyncChunkRepository, 
                 document_repository: AsyncDocumentRepository,
                 library_repository: AsyncLibraryRepository):
        self.chunk_repository = chunk_repository
        self.document_repository = document_repository
        self.library_repository = library_repository
    
    async def _generate_embedding_for_chunk(self, text: str) -> Tuple[Optional[List[float]], Optional[int], str, bool]:
        """Generate embedding for chunk text - separated concern."""
        embeddings = await generate_embeddings([text])
        embedding = embeddings[0] if embeddings else None
        
        return (
            embedding,
            len(embedding) if embedding else None,
            settings.embedding_model,
            True if embedding else False
        )
    
    async def create_chunk(self, document_id: UUID, library_id: UUID, text: str, 
                         position: int = 0, metadata: Optional[dict] = None) -> Chunk:
        """Create a new chunk with validation and automatic embedding generation."""
        # Validation
        document = await self.document_repository.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        library = await self.library_repository.get_by_id(library_id)
        if not library:
            raise ValueError(f"Library with ID {library_id} not found")
        
        if document.library_id != library_id:
            raise ValueError(f"Document {document_id} does not belong to library {library_id}")
        
        # Generate embedding
        embedding, dimension, model, is_indexed = await self._generate_embedding_for_chunk(text)
        
        # Create chunk
        chunk = Chunk(
            document_id=document_id,
            library_id=library_id,
            text=text,
            text_length=len(text),
            position=position,
            metadata_=metadata or {},
            embedding=embedding,
            embedding_dimension=dimension,
            embedding_model=model,
            is_indexed=is_indexed
        )
        return await self.chunk_repository.create(chunk)
    
    async def update_chunk_text(self, chunk_id: UUID, text: str) -> Optional[Chunk]:
        """Update chunk text and automatically regenerate embedding."""
        # Check if chunk exists
        chunk = await self.chunk_repository.get_by_id(chunk_id)
        if not chunk:
            return None
        
        # Generate new embedding for updated text
        embedding, dimension, model, is_indexed = await self._generate_embedding_for_chunk(text)
        
        # Update with new text and embedding
        updates = {
            "text": text,
            "text_length": len(text),
            "embedding": embedding,
            "embedding_dimension": dimension,
            "embedding_model": model,
            "is_indexed": is_indexed
        }
        
        return await self.chunk_repository.update(chunk_id, updates)
    
    async def regenerate_embedding(self, chunk_id: UUID) -> Optional[Chunk]:
        """Regenerate embedding for existing chunk text."""
        chunk = await self.chunk_repository.get_by_id(chunk_id)
        if not chunk:
            return None
        
        # Generate new embedding using current text
        embedding, dimension, model, is_indexed = await self._generate_embedding_for_chunk(chunk.text)
        
        updates = {
            "embedding": embedding,
            "embedding_dimension": dimension,
            "embedding_model": model,
            "is_indexed": is_indexed
        }
        
        return await self.chunk_repository.update(chunk_id, updates)
    
    async def get_chunk(self, chunk_id: UUID) -> Optional[Chunk]:
        """Get a chunk by ID."""
        return await self.chunk_repository.get_by_id(chunk_id)
    
    async def list_chunks(self, document_id: Optional[UUID] = None, library_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[Chunk]:
        """List chunks with optional filtering."""
        if document_id:
            return await self.chunk_repository.get_by_document_id(document_id, skip=skip, limit=limit)
        elif library_id:
            return await self.chunk_repository.get_by_library_id(library_id, skip=skip, limit=limit)
        return await self.chunk_repository.get_all(skip=skip, limit=limit)
    
    async def count_chunks(self, document_id: Optional[UUID] = None, library_id: Optional[UUID] = None) -> int:
        """Get total count of chunks."""
        if document_id:
            return await self.chunk_repository.count_by_document_id(document_id)
        elif library_id:
            return await self.chunk_repository.count_by_library_id(library_id)
        return await self.chunk_repository.count()
    
    async def update_chunk(self, chunk_id: UUID, **updates) -> Optional[Chunk]:
        """Update a chunk (for non-text updates)."""
        return await self.chunk_repository.update(chunk_id, updates)
    
    async def delete_chunk(self, chunk_id: UUID) -> Optional[dict]:
        """Delete a chunk and return success message."""
        chunk = await self.chunk_repository.get_by_id(chunk_id)
        if not chunk:
            return None
        
        deleted = await self.chunk_repository.delete(chunk_id)
        if not deleted:
            return None
        
        return {
            "message": f"Chunk with ID '{chunk_id}' deleted successfully"
        } 