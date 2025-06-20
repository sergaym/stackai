"""
Chunk business logic service.
"""

from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from app.db.models import Chunk
from app.repositories.async_chunk_repository import AsyncChunkRepository
from app.repositories.async_document_repository import AsyncDocumentRepository
from app.repositories.async_library_repository import AsyncLibraryRepository
from app.services.embedding_service import generate_embeddings
from app.services.index_service import IndexService
from app.core.config import settings


class ChunkService:
    """Simple chunk service with validation and auto-embedding."""
    
    def __init__(self, chunk_repository: AsyncChunkRepository, 
                 document_repository: AsyncDocumentRepository,
                 library_repository: AsyncLibraryRepository,
                 index_service: Optional[IndexService] = None):
        self.chunk_repository = chunk_repository
        self.document_repository = document_repository
        self.library_repository = library_repository
        self.index_service = index_service
    
    async def _generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts efficiently."""
        if not texts:
            return []
        
        try:
            embeddings = await generate_embeddings(texts)
            return embeddings if embeddings else [None] * len(texts)
        except Exception:
            return [None] * len(texts)
    
    async def _generate_embedding_for_chunk(self, text: str) -> Tuple[Optional[List[float]], Optional[int], str, bool]:
        """Generate embedding for chunk text - use batch method for efficiency."""
        embeddings = await self._generate_embeddings_batch([text])
        embedding = embeddings[0] if embeddings else None
        
        return (
            embedding,
            len(embedding) if embedding else None,
            settings.embedding_model,
            True if embedding else False
        )
    
    async def create_chunks_batch(self, chunks_data: List[Dict[str, Any]]) -> List[Chunk]:
        """
        Create multiple chunks efficiently with batch embedding generation.
        
        Args:
            chunks_data: List of chunk data dicts with keys:
                - document_id: UUID
                - library_id: UUID  
                - text: str
                - position: int (optional)
                - metadata: dict (optional)
                
        Returns:
            List of created chunks
        """
        if not chunks_data:
            return []
        
        # Validate all documents and libraries exist (early validation)
        document_ids = set(data['document_id'] for data in chunks_data)
        library_ids = set(data['library_id'] for data in chunks_data)
        
        # Batch validation
        for doc_id in document_ids:
            document = await self.document_repository.get_by_id(doc_id)
            if not document:
                raise ValueError(f"Document with ID {doc_id} not found")
        
        for lib_id in library_ids:
            library = await self.library_repository.get_by_id(lib_id)
            if not library:
                raise ValueError(f"Library with ID {lib_id} not found")
        
        # Extract texts for batch embedding generation
        texts = [data['text'] for data in chunks_data]
        
        # Generate embeddings efficiently in one API call
        embeddings = await self._generate_embeddings_batch(texts)
        
        # Create chunks with embeddings
        created_chunks = []
        for i, data in enumerate(chunks_data):
            embedding = embeddings[i] if i < len(embeddings) else None
            
            chunk = Chunk(
                document_id=data['document_id'],
                library_id=data['library_id'],
                text=data['text'],
                text_length=len(data['text']),
                position=data.get('position', i),
                metadata_=data.get('metadata', {}),
                embedding=embedding,
                embedding_dimension=len(embedding) if embedding else None,
                embedding_model=settings.embedding_model,
                is_indexed=True if embedding else False
            )
            
            created_chunk = await self.chunk_repository.create(chunk)
            created_chunks.append(created_chunk)
            
            # Add to index if embedding exists and index service is available
            if embedding and self.index_service:
                await self.index_service.add_chunk(
                    library_id=data['library_id'],
                    chunk_id=created_chunk.id,
                    embedding=embedding,
                    metadata=data.get('metadata', {})
                )
        
        return created_chunks
    
    async def create_chunk(self, document_id: UUID, library_id: UUID, text: str, 
                         position: int = 0, metadata: Optional[dict] = None) -> Chunk:
        """
        Create a single chunk with validation and automatic embedding generation.
        For batch operations, use create_chunks_batch() for better efficiency.
        """
        # Use batch method for consistency
        chunks_data = [{
            'document_id': document_id,
            'library_id': library_id,
            'text': text,
            'position': position,
            'metadata': metadata or {}
        }]
        
        created_chunks = await self.create_chunks_batch(chunks_data)
        return created_chunks[0] if created_chunks else None
    
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
        
        updated_chunk = await self.chunk_repository.update(chunk_id, updates)
        
        # Update index if embedding changed and index service is available
        if updated_chunk and embedding and self.index_service:
            # Remove old vector and add new one
            await self.index_service.remove_chunk(updated_chunk.library_id, chunk_id)
            await self.index_service.add_chunk(
                library_id=updated_chunk.library_id,
                chunk_id=chunk_id,
                embedding=embedding,
                metadata={"text_length": len(text)}
            )
        
        return updated_chunk
    
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
    
    async def delete_chunk(self, chunk_id: UUID) -> Optional[dict]:
        """Delete a chunk and return success message."""
        chunk = await self.chunk_repository.get_by_id(chunk_id)
        if not chunk:
            return None
        
        # Remove from index if index service is available
        if self.index_service:
            await self.index_service.remove_chunk(chunk.library_id, chunk_id)
        
        deleted = await self.chunk_repository.delete(chunk_id)
        if not deleted:
            return None
        
        return {
            "message": f"Chunk with ID '{chunk_id}' deleted successfully"
        } 