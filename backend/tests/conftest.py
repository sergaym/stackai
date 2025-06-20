"""
Pytest configuration and shared fixtures for unit tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID
from datetime import datetime


# Unit Test Fixtures
@pytest.fixture
def fixed_uuid():
    """Fixed UUID for testing."""
    return UUID("12345678-1234-5678-9abc-123456789abc")


@pytest.fixture
def fixed_datetime():
    """Fixed datetime for testing."""
    return datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing."""
    return {"key1": "value1", "key2": "value2"}


# Mock Domain Models
@pytest.fixture
def mock_library_domain(fixed_uuid, fixed_datetime, sample_metadata):
    """Mock library domain model."""
    library = MagicMock()
    library.id = fixed_uuid
    library.name = "Test Library"
    library.description = "Test Description"
    library.metadata_ = sample_metadata
    library.created_at = fixed_datetime
    library.updated_at = fixed_datetime
    return library


@pytest.fixture
def mock_document_domain(fixed_uuid, fixed_datetime, sample_metadata):
    """Mock document domain model."""
    document = MagicMock()
    document.id = fixed_uuid
    document.library_id = fixed_uuid
    document.name = "Test Document"
    document.description = "Test Description"
    document.source_url = None
    document.content_type = "text/plain"
    document.metadata_ = sample_metadata
    document.created_at = fixed_datetime
    document.updated_at = fixed_datetime
    document.is_processed = True
    document.processing_status = "completed"
    return document


@pytest.fixture
def mock_chunk_domain(fixed_uuid, fixed_datetime, sample_metadata):
    """Mock chunk domain model."""
    chunk = MagicMock()
    chunk.id = fixed_uuid
    chunk.document_id = fixed_uuid
    chunk.library_id = fixed_uuid
    chunk.text = "Test chunk text content"
    chunk.text_length = len("Test chunk text content")
    chunk.position = 0
    chunk.metadata_ = sample_metadata
    chunk.embedding_dimension = 384
    chunk.embedding_model = "test-model"
    chunk.created_at = fixed_datetime
    chunk.updated_at = fixed_datetime
    chunk.is_indexed = True
    return chunk


# Mock Services
@pytest.fixture
def mock_library_service():
    """Mock library service."""
    return AsyncMock()


@pytest.fixture
def mock_document_service():
    """Mock document service."""
    return AsyncMock()


@pytest.fixture
def mock_chunk_service():
    """Mock chunk service."""
    return AsyncMock() 