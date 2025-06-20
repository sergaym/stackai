"""
Unit tests for library endpoint functions.

Tests individual endpoint functions in isolation with properly mocked dependencies.
"""

import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from uuid import uuid4

from app.api.v1.endpoints.libraries import (
    create_library, get_library, list_libraries, 
    update_library, delete_library, index_library
)
from app.schemas.library import LibraryCreateRequest, LibraryUpdateRequest



class TestCreateLibraryUnit:
    """Unit tests for create_library function."""
    
    @pytest.mark.asyncio
    async def test_create_library_success(self, mock_library_service, mock_library_domain):
        """Test create_library function with successful creation."""
        # Arrange
        request_data = LibraryCreateRequest(name="Test Library", description="Test Description")
        mock_library_service.create_library.return_value = mock_library_domain
        
        # Act
        result = await create_library(request_data, mock_library_service)
        
        # Assert
        assert result.name == "Test Library"
        assert result.description == "Test Description" 
        mock_library_service.create_library.assert_called_once_with(
            name="Test Library",
            description="Test Description",
            metadata={}  # LibraryCreateRequest defaults metadata to empty dict
        )
    
    @pytest.mark.asyncio
    async def test_create_library_with_metadata(self, mock_library_service, mock_library_domain):
        """Test create_library function with metadata."""
        # Arrange
        metadata = {"key": "value"}
        request_data = LibraryCreateRequest(
            name="Test Library", 
            description="Test Description",
            metadata=metadata
        )
        mock_library_service.create_library.return_value = mock_library_domain
        
        # Act
        result = await create_library(request_data, mock_library_service)
        
        # Assert
        assert result.name == "Test Library"
        mock_library_service.create_library.assert_called_once_with(
            name="Test Library",
            description="Test Description", 
            metadata=metadata
        )
    
    @pytest.mark.asyncio
    async def test_create_library_service_error(self, mock_library_service):
        """Test create_library function when service raises ValueError."""
        # Arrange
        request_data = LibraryCreateRequest(name="Duplicate Library")
        mock_library_service.create_library.side_effect = ValueError("Library name already exists")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await create_library(request_data, mock_library_service)
        
        assert exc_info.value.status_code == 400
        assert "Library name already exists" in str(exc_info.value.detail)



class TestGetLibraryUnit:
    """Unit tests for get_library function."""
    
    @pytest.mark.asyncio
    async def test_get_library_success(self, mock_library_service, mock_library_domain, fixed_uuid):
        """Test get_library function with existing library."""
        # Arrange
        mock_library_service.get_library.return_value = mock_library_domain
        
        # Act
        result = await get_library(fixed_uuid, mock_library_service)
        
        # Assert
        assert result.id == fixed_uuid
        assert result.name == "Test Library"
        mock_library_service.get_library.assert_called_once_with(fixed_uuid)
    
    @pytest.mark.asyncio
    async def test_get_library_not_found(self, mock_library_service, fixed_uuid):
        """Test get_library function when library doesn't exist."""
        # Arrange
        mock_library_service.get_library.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_library(fixed_uuid, mock_library_service)
        
        assert exc_info.value.status_code == 404
        assert f"Library with ID {fixed_uuid} not found" in str(exc_info.value.detail)



class TestListLibrariesUnit:
    """Unit tests for list_libraries function."""
    
    @pytest.mark.asyncio
    async def test_list_libraries_success(self, mock_library_service, mock_library_domain):
        """Test list_libraries function with results."""
        # Arrange
        mock_library_service.list_libraries.return_value = [mock_library_domain]
        mock_library_service.count_libraries.return_value = 1
        
        # Act
        result = await list_libraries(skip=0, limit=100, library_service=mock_library_service)
        
        # Assert
        assert result.total == 1
        assert result.skip == 0
        assert result.limit == 100
        assert len(result.libraries) == 1
        assert result.libraries[0].name == "Test Library"
        mock_library_service.list_libraries.assert_called_once_with(skip=0, limit=100)
        mock_library_service.count_libraries.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_libraries_empty(self, mock_library_service):
        """Test list_libraries function with no results."""
        # Arrange
        mock_library_service.list_libraries.return_value = []
        mock_library_service.count_libraries.return_value = 0
        
        # Act
        result = await list_libraries(skip=0, limit=100, library_service=mock_library_service)
        
        # Assert
        assert result.total == 0
        assert len(result.libraries) == 0



class TestUpdateLibraryUnit:
    """Unit tests for update_library function."""
    
    @pytest.mark.asyncio
    async def test_update_library_success(self, mock_library_service, mock_library_domain, fixed_uuid):
        """Test update_library function with successful update.""" 
        # Arrange
        request_data = LibraryUpdateRequest(name="Updated Library")
        mock_library_service.update_library.return_value = mock_library_domain
        
        # Act
        result = await update_library(fixed_uuid, request_data, mock_library_service)
        
        # Assert
        assert result.name == "Test Library"  # Mock returns the original mock
        mock_library_service.update_library.assert_called_once_with(
            fixed_uuid, name="Updated Library"
        )
    
    @pytest.mark.asyncio
    async def test_update_library_not_found(self, mock_library_service, fixed_uuid):
        """Test update_library function when library doesn't exist."""
        # Arrange
        request_data = LibraryUpdateRequest(name="Updated Library")
        mock_library_service.update_library.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await update_library(fixed_uuid, request_data, mock_library_service)
        
        assert exc_info.value.status_code == 404
        assert f"Library with ID {fixed_uuid} not found" in str(exc_info.value.detail)



class TestDeleteLibraryUnit:
    """Unit tests for delete_library function."""
    
    @pytest.mark.asyncio
    async def test_delete_library_success(self, mock_library_service, fixed_uuid):
        """Test delete_library function with successful deletion."""
        # Arrange
        deletion_result = {"message": "Library deleted successfully"}
        mock_library_service.delete_library.return_value = deletion_result
        
        # Act
        result = await delete_library(fixed_uuid, mock_library_service)
        
        # Assert
        assert result.message == "Library deleted successfully"
        mock_library_service.delete_library.assert_called_once_with(fixed_uuid)
    
    @pytest.mark.asyncio
    async def test_delete_library_not_found(self, mock_library_service, fixed_uuid):
        """Test delete_library function when library doesn't exist."""
        # Arrange
        mock_library_service.delete_library.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await delete_library(fixed_uuid, mock_library_service)
        
        assert exc_info.value.status_code == 404
        assert f"Library with ID {fixed_uuid} not found" in str(exc_info.value.detail)



class TestIndexLibraryUnit:
    """Unit tests for index_library function."""
    
    @pytest.mark.asyncio
    async def test_index_library_success(self, mock_library_service, fixed_uuid):
        """Test index_library function with successful indexing."""
        # Arrange
        index_result = {"message": "Library indexed successfully", "chunks_indexed": 10}
        mock_library_service.index_library.return_value = index_result
        
        # Act
        result = await index_library(fixed_uuid, mock_library_service)
        
        # Assert
        assert result["message"] == "Library indexed successfully"
        assert result["chunks_indexed"] == 10
        mock_library_service.index_library.assert_called_once_with(fixed_uuid)
    
    @pytest.mark.asyncio
    async def test_index_library_not_found(self, mock_library_service, fixed_uuid):
        """Test index_library function when library doesn't exist."""
        # Arrange
        mock_library_service.index_library.side_effect = ValueError("Library not found")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await index_library(fixed_uuid, mock_library_service)
        
        assert exc_info.value.status_code == 404
        assert "Library not found" in str(exc_info.value.detail) 