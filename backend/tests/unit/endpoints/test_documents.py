"""
Unit tests for document endpoint functions.

Tests individual endpoint functions in isolation with properly mocked dependencies.
"""

import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from uuid import uuid4

from app.api.v1.endpoints.documents import (
    create_document, get_document, list_documents, 
    update_document, delete_document
)
from app.schemas.document import DocumentCreateRequest, DocumentUpdateRequest



class TestCreateDocumentUnit:
    """Unit tests for create_document function."""
    
    @pytest.mark.asyncio
    async def test_create_document_success(self, mock_document_service, mock_document_domain, fixed_uuid):
        """Test create_document function with successful creation."""
        # Arrange
        request_data = DocumentCreateRequest(
            library_id=fixed_uuid,
            name="Test Document", 
            description="Test Description"
        )
        mock_document_service.create_document.return_value = mock_document_domain
        
        # Act
        result = await create_document(request_data, mock_document_service)
        
        # Assert
        assert result.name == "Test Document"
        assert result.description == "Test Description"
        assert result.library_id == fixed_uuid
        mock_document_service.create_document.assert_called_once_with(
            library_id=fixed_uuid,
            name="Test Document",
            description="Test Description",
            content_type="text/plain",
            metadata={}
        )
    
    @pytest.mark.asyncio
    async def test_create_document_with_metadata(self, mock_document_service, mock_document_domain, fixed_uuid):
        """Test create_document function with metadata."""
        # Arrange
        metadata = {"type": "report", "version": "1.0"}
        request_data = DocumentCreateRequest(
            library_id=fixed_uuid,
            name="Test Document",
            content_type="application/pdf",
            metadata=metadata
        )
        mock_document_service.create_document.return_value = mock_document_domain
        
        # Act
        result = await create_document(request_data, mock_document_service)
        
        # Assert
        assert result.name == "Test Document"
        mock_document_service.create_document.assert_called_once_with(
            library_id=fixed_uuid,
            name="Test Document",
            description=None,
            content_type="application/pdf",
            metadata=metadata
        )
    
    @pytest.mark.asyncio
    async def test_create_document_service_error(self, mock_document_service, fixed_uuid):
        """Test create_document function when service raises ValueError."""
        # Arrange
        request_data = DocumentCreateRequest(library_id=fixed_uuid, name="Test Document")
        mock_document_service.create_document.side_effect = ValueError("Library not found")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_document(request_data, mock_document_service)
        
        assert exc_info.value.status_code == 400
        assert "Library not found" in str(exc_info.value.detail)



class TestGetDocumentUnit:
    """Unit tests for get_document function."""
    
    @pytest.mark.asyncio
    async def test_get_document_success(self, mock_document_service, mock_document_domain, fixed_uuid):
        """Test get_document function with existing document."""
        # Arrange
        mock_document_service.get_document.return_value = mock_document_domain
        
        # Act
        result = await get_document(fixed_uuid, mock_document_service)
        
        # Assert
        assert result.id == fixed_uuid
        assert result.name == "Test Document"
        mock_document_service.get_document.assert_called_once_with(fixed_uuid)
    
    @pytest.mark.asyncio
    async def test_get_document_not_found(self, mock_document_service, fixed_uuid):
        """Test get_document function when document doesn't exist."""
        # Arrange
        mock_document_service.get_document.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_document(fixed_uuid, mock_document_service)
        
        assert exc_info.value.status_code == 404
        assert f"Document with ID {fixed_uuid} not found" in str(exc_info.value.detail)



class TestListDocumentsUnit:
    """Unit tests for list_documents function."""
    
    @pytest.mark.asyncio
    async def test_list_documents_success(self, mock_document_service, mock_document_domain):
        """Test list_documents function with results."""
        # Arrange
        mock_document_service.list_documents.return_value = [mock_document_domain]
        mock_document_service.count_documents.return_value = 1
        
        # Act
        result = await list_documents(skip=0, limit=100, document_service=mock_document_service)
        
        # Assert
        assert result.total == 1
        assert result.skip == 0
        assert result.limit == 100
        assert len(result.documents) == 1
        assert result.documents[0].name == "Test Document"
        mock_document_service.list_documents.assert_called_once_with(
            library_id=None, skip=0, limit=100
        )
        mock_document_service.count_documents.assert_called_once_with(library_id=None)
    
    @pytest.mark.asyncio
    async def test_list_documents_with_library_filter(self, mock_document_service, mock_document_domain, fixed_uuid):
        """Test list_documents function with library filter."""
        # Arrange
        mock_document_service.list_documents.return_value = [mock_document_domain]
        mock_document_service.count_documents.return_value = 1
        
        # Act
        result = await list_documents(
            library_id=fixed_uuid, skip=10, limit=50, 
            document_service=mock_document_service
        )
        
        # Assert
        assert result.total == 1
        assert result.skip == 10
        assert result.limit == 50
        mock_document_service.list_documents.assert_called_once_with(
            library_id=fixed_uuid, skip=10, limit=50
        )
        mock_document_service.count_documents.assert_called_once_with(library_id=fixed_uuid)
    
    @pytest.mark.asyncio
    async def test_list_documents_empty(self, mock_document_service):
        """Test list_documents function with no results."""
        # Arrange
        mock_document_service.list_documents.return_value = []
        mock_document_service.count_documents.return_value = 0
        
        # Act
        result = await list_documents(skip=0, limit=100, document_service=mock_document_service)
        
        # Assert
        assert result.total == 0
        assert len(result.documents) == 0



class TestUpdateDocumentUnit:
    """Unit tests for update_document function."""
    
    @pytest.mark.asyncio
    async def test_update_document_success(self, mock_document_service, mock_document_domain, fixed_uuid):
        """Test update_document function with successful update."""
        # Arrange
        request_data = DocumentUpdateRequest(name="Updated Document")
        mock_document_service.update_document.return_value = mock_document_domain
        
        # Act
        result = await update_document(fixed_uuid, request_data, mock_document_service)
        
        # Assert
        assert result.name == "Test Document"  # Mock returns the original mock
        mock_document_service.update_document.assert_called_once_with(
            fixed_uuid, name="Updated Document"
        )
    
    @pytest.mark.asyncio
    async def test_update_document_with_metadata(self, mock_document_service, mock_document_domain, fixed_uuid):
        """Test update_document function with metadata update."""
        # Arrange
        metadata = {"updated": "true", "version": "2.0"}
        request_data = DocumentUpdateRequest(
            name="Updated Document",
            description="Updated Description",
            metadata=metadata
        )
        mock_document_service.update_document.return_value = mock_document_domain
        
        # Act
        result = await update_document(fixed_uuid, request_data, mock_document_service)
        
        # Assert
        assert result.name == "Test Document"
        mock_document_service.update_document.assert_called_once_with(
            fixed_uuid,
            name="Updated Document",
            description="Updated Description",
            metadata_=metadata
        )
    
    @pytest.mark.asyncio
    async def test_update_document_not_found(self, mock_document_service, fixed_uuid):
        """Test update_document function when document doesn't exist."""
        # Arrange
        request_data = DocumentUpdateRequest(name="Updated Document")
        mock_document_service.update_document.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_document(fixed_uuid, request_data, mock_document_service)
        
        assert exc_info.value.status_code == 404
        assert f"Document with ID {fixed_uuid} not found" in str(exc_info.value.detail)



class TestDeleteDocumentUnit:
    """Unit tests for delete_document function."""
    
    @pytest.mark.asyncio
    async def test_delete_document_success(self, mock_document_service, fixed_uuid):
        """Test delete_document function with successful deletion."""
        # Arrange
        deletion_result = {"message": "Document 'Test Document' deleted successfully"}
        mock_document_service.delete_document.return_value = deletion_result
        
        # Act
        result = await delete_document(fixed_uuid, mock_document_service)
        
        # Assert
        assert result.message == "Document 'Test Document' deleted successfully"
        mock_document_service.delete_document.assert_called_once_with(fixed_uuid)
    
    @pytest.mark.asyncio
    async def test_delete_document_not_found(self, mock_document_service, fixed_uuid):
        """Test delete_document function when document doesn't exist."""
        # Arrange
        mock_document_service.delete_document.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await delete_document(fixed_uuid, mock_document_service)
        
        assert exc_info.value.status_code == 404
        assert f"Document with ID {fixed_uuid} not found" in str(exc_info.value.detail) 