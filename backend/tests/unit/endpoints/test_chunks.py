"""
Unit tests for chunk endpoint functions.

Tests individual endpoint functions in isolation with properly mocked dependencies.
"""

import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from uuid import uuid4

from app.api.v1.endpoints.chunks import (
    create_chunk, get_chunk, list_chunks, 
    update_chunk, delete_chunk, regenerate_chunk_embedding
)
from app.schemas.chunk import ChunkCreateRequest, ChunkUpdateRequest


class TestCreateChunkUnit:
    """Unit tests for create_chunk function."""
    
    @pytest.mark.asyncio
    async def test_create_chunk_success(self, mock_chunk_service, mock_chunk_domain):
        """Test create_chunk function with successful creation."""
        # Arrange
        document_id = uuid4()
        library_id = uuid4()
        request_data = ChunkCreateRequest(
            document_id=document_id,
            library_id=library_id,
            text="Test chunk content",
            position=0,
            metadata={"key": "value"}
        )
        mock_chunk_service.create_chunk.return_value = mock_chunk_domain
        
        # Act
        result = await create_chunk(request_data, mock_chunk_service)
        
        # Assert
        assert result.text == "Test chunk text content"
        mock_chunk_service.create_chunk.assert_called_once_with(
            document_id=document_id,
            library_id=library_id,
            text="Test chunk content",
            position=0,
            metadata={"key": "value"}
        )
    
    @pytest.mark.asyncio
    async def test_create_chunk_service_error(self, mock_chunk_service):
        """Test create_chunk function handles service errors."""
        # Arrange
        request_data = ChunkCreateRequest(
            document_id=uuid4(),
            library_id=uuid4(),
            text="Test chunk content"
        )
        mock_chunk_service.create_chunk.side_effect = ValueError("Document not found")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_chunk(request_data, mock_chunk_service)
        
        assert exc_info.value.status_code == 400
        assert "Document not found" in str(exc_info.value.detail)


class TestGetChunkUnit:
    """Unit tests for get_chunk function."""
    
    @pytest.mark.asyncio
    async def test_get_chunk_success(self, mock_chunk_service, mock_chunk_domain):
        """Test get_chunk function with existing chunk."""
        # Arrange
        chunk_id = uuid4()
        mock_chunk_service.get_chunk.return_value = mock_chunk_domain
        
        # Act
        result = await get_chunk(chunk_id, mock_chunk_service)
        
        # Assert
        assert result.text == "Test chunk text content"
        mock_chunk_service.get_chunk.assert_called_once_with(chunk_id)
    
    @pytest.mark.asyncio
    async def test_get_chunk_not_found(self, mock_chunk_service):
        """Test get_chunk function with non-existent chunk."""
        # Arrange
        chunk_id = uuid4()
        mock_chunk_service.get_chunk.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_chunk(chunk_id, mock_chunk_service)
        
        assert exc_info.value.status_code == 404
        assert str(chunk_id) in str(exc_info.value.detail)


class TestListChunksUnit:
    """Unit tests for list_chunks function."""
    
    @pytest.mark.asyncio
    async def test_list_chunks_success(self, mock_chunk_service, mock_chunk_domain):
        """Test list_chunks function with successful listing."""
        # Arrange
        document_id = uuid4()
        library_id = uuid4()
        mock_chunk_service.list_chunks.return_value = [mock_chunk_domain]
        mock_chunk_service.count_chunks.return_value = 1
        
        # Act
        result = await list_chunks(
            document_id=document_id,
            library_id=library_id,
            skip=0,
            limit=10,
            chunk_service=mock_chunk_service
        )
        
        # Assert
        assert len(result.chunks) == 1
        assert result.total == 1
        assert result.skip == 0
        assert result.limit == 10
        mock_chunk_service.list_chunks.assert_called_once_with(
            document_id=document_id,
            library_id=library_id,
            skip=0,
            limit=10
        )
        mock_chunk_service.count_chunks.assert_called_once_with(
            document_id=document_id,
            library_id=library_id
        )
    
    @pytest.mark.asyncio
    async def test_list_chunks_no_filters(self, mock_chunk_service, mock_chunk_domain):
        """Test list_chunks function without filters."""
        # Arrange
        mock_chunk_service.list_chunks.return_value = [mock_chunk_domain]
        mock_chunk_service.count_chunks.return_value = 1
        
        # Act
        result = await list_chunks(chunk_service=mock_chunk_service)
        
        # Assert
        assert len(result.chunks) == 1
        assert result.total == 1
        mock_chunk_service.list_chunks.assert_called_once_with(
            document_id=None,
            library_id=None,
            skip=0,
            limit=100
        )


class TestUpdateChunkUnit:
    """Unit tests for update_chunk function."""
    
    @pytest.mark.asyncio
    async def test_update_chunk_text_success(self, mock_chunk_service, mock_chunk_domain):
        """Test update_chunk function with text update (triggers re-embedding)."""
        # Arrange
        chunk_id = uuid4()
        request_data = ChunkUpdateRequest(text="Updated chunk content")
        mock_chunk_service.update_chunk_text.return_value = mock_chunk_domain
        
        # Act
        result = await update_chunk(chunk_id, request_data, mock_chunk_service)
        
        # Assert
        assert result.text == "Test chunk text content"
        mock_chunk_service.update_chunk_text.assert_called_once_with(
            chunk_id, "Updated chunk content"
        )
    
    @pytest.mark.asyncio
    async def test_update_chunk_metadata_success(self, mock_chunk_service, mock_chunk_domain):
        """Test update_chunk function with metadata update."""
        # Arrange
        chunk_id = uuid4()
        request_data = ChunkUpdateRequest(
            position=5,
            metadata={"updated": "metadata"}
        )
        mock_chunk_service.update_chunk.return_value = mock_chunk_domain
        
        # Act
        result = await update_chunk(chunk_id, request_data, mock_chunk_service)
        
        # Assert
        assert result.text == "Test chunk text content"
        mock_chunk_service.update_chunk.assert_called_once_with(
            chunk_id,
            position=5,
            metadata_={"updated": "metadata"}
        )
    
    @pytest.mark.asyncio
    async def test_update_chunk_no_changes(self, mock_chunk_service, mock_chunk_domain):
        """Test update_chunk function with no changes."""
        # Arrange
        chunk_id = uuid4()
        request_data = ChunkUpdateRequest()  # No fields set
        mock_chunk_service.get_chunk.return_value = mock_chunk_domain
        
        # Act
        result = await update_chunk(chunk_id, request_data, mock_chunk_service)
        
        # Assert
        assert result.text == "Test chunk text content"
        mock_chunk_service.get_chunk.assert_called_once_with(chunk_id)
    
    @pytest.mark.asyncio
    async def test_update_chunk_text_not_found(self, mock_chunk_service):
        """Test update_chunk function with text update for non-existent chunk."""
        # Arrange
        chunk_id = uuid4()
        request_data = ChunkUpdateRequest(text="Updated content")
        mock_chunk_service.update_chunk_text.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_chunk(chunk_id, request_data, mock_chunk_service)
        
        assert exc_info.value.status_code == 404
        assert str(chunk_id) in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_chunk_metadata_not_found(self, mock_chunk_service):
        """Test update_chunk function with metadata update for non-existent chunk."""
        # Arrange
        chunk_id = uuid4()
        request_data = ChunkUpdateRequest(position=5)
        mock_chunk_service.update_chunk.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_chunk(chunk_id, request_data, mock_chunk_service)
        
        assert exc_info.value.status_code == 404
        assert str(chunk_id) in str(exc_info.value.detail)


class TestRegenerateChunkEmbeddingUnit:
    """Unit tests for regenerate_chunk_embedding function."""
    
    @pytest.mark.asyncio
    async def test_regenerate_embedding_success(self, mock_chunk_service, mock_chunk_domain):
        """Test regenerate_chunk_embedding function with successful regeneration."""
        # Arrange
        chunk_id = uuid4()
        mock_chunk_service.regenerate_embedding.return_value = mock_chunk_domain
        
        # Act
        result = await regenerate_chunk_embedding(chunk_id, mock_chunk_service)
        
        # Assert
        assert result.text == "Test chunk text content"
        mock_chunk_service.regenerate_embedding.assert_called_once_with(chunk_id)
    
    @pytest.mark.asyncio
    async def test_regenerate_embedding_not_found(self, mock_chunk_service):
        """Test regenerate_chunk_embedding function with non-existent chunk."""
        # Arrange
        chunk_id = uuid4()
        mock_chunk_service.regenerate_embedding.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await regenerate_chunk_embedding(chunk_id, mock_chunk_service)
        
        assert exc_info.value.status_code == 404
        assert str(chunk_id) in str(exc_info.value.detail)


class TestDeleteChunkUnit:
    """Unit tests for delete_chunk function."""
    
    @pytest.mark.asyncio
    async def test_delete_chunk_success(self, mock_chunk_service):
        """Test delete_chunk function with successful deletion."""
        # Arrange
        chunk_id = uuid4()
        deletion_result = {"message": "Chunk deleted successfully"}
        mock_chunk_service.delete_chunk.return_value = deletion_result
        
        # Act
        result = await delete_chunk(chunk_id, mock_chunk_service)
        
        # Assert
        assert result.message == "Chunk deleted successfully"
        mock_chunk_service.delete_chunk.assert_called_once_with(chunk_id)
    
    @pytest.mark.asyncio
    async def test_delete_chunk_not_found(self, mock_chunk_service):
        """Test delete_chunk function with non-existent chunk."""
        # Arrange
        chunk_id = uuid4()
        mock_chunk_service.delete_chunk.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await delete_chunk(chunk_id, mock_chunk_service)
        
        assert exc_info.value.status_code == 404
        assert str(chunk_id) in str(exc_info.value.detail) 