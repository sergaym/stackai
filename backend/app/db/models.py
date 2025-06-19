"""
Database models - KISS approach.
"""

from datetime import datetime
from typing import Dict, List
from uuid import UUID, uuid4

from sqlalchemy import ARRAY, Boolean, DateTime, Float, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Library(Base):
    """Library containing documents."""
    
    __tablename__ = "libraries"
    
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_: Mapped[Dict] = mapped_column("metadata", JSON, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Simple stats
    document_count: Mapped[int] = mapped_column(Integer, default=0)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="library", cascade="all, delete-orphan")
    chunks: Mapped[List["Chunk"]] = relationship("Chunk", back_populates="library", cascade="all, delete-orphan")


class Document(Base):
    """Document containing chunks."""
    
    __tablename__ = "documents"
    
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    library_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    content_type: Mapped[str] = mapped_column(String(100), default="text/plain")
    source_url: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_: Mapped[Dict] = mapped_column("metadata", JSON, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Simple stats
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_status: Mapped[str] = mapped_column(String(50), default="pending")
    
    # Relationships
    library: Mapped["Library"] = relationship("Library", back_populates="documents")
    chunks: Mapped[List["Chunk"]] = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    """Text chunk with vector embedding."""
    
    __tablename__ = "chunks"
    
    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    library_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Content
    text: Mapped[str] = mapped_column(Text, nullable=False)
    text_length: Mapped[int] = mapped_column(Integer, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0)
    
    # Vector embedding
    embedding: Mapped[List[float]] = mapped_column(ARRAY(Float), nullable=True)
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=True)
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=True)
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    metadata_: Mapped[Dict] = mapped_column("metadata", JSON, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
    library: Mapped["Library"] = relationship("Library", back_populates="chunks") 