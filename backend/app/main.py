"""
Main FastAPI application factory and configuration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    await startup_reindex()
    yield
    # Shutdown (if needed in the future)


async def startup_reindex():
    """
    Startup reindexing. Uses default algorithm for simplicity.
    Reindexes existing chunks with embeddings.
    TODO: Remove this once we have a persistent reindexing mechanism.
    TODO: Index each library separately with the algorithm that better suits it.
    """
    try:
        from app.core.dependencies import get_index_service
        from app.db.database import get_db_session
        from app.repositories.async_chunk_repository import AsyncChunkRepository
        from app.repositories.async_library_repository import AsyncLibraryRepository
        
        print("🔄 Starting startup reindexing...")
        
        # Get services (singleton pattern)
        index_service = get_index_service()
        
        # Simple database session handling
        async for db_session in get_db_session():
            chunk_repo = AsyncChunkRepository(db_session)
            library_repo = AsyncLibraryRepository(db_session)
            
            # Get libraries with reasonable pagination
            libraries = await library_repo.get_all(limit=100)
            if not libraries:
                print("ℹ️  No libraries found for reindexing")
                return
            
            total_reindexed = 0
            
            # Process each library independently (fault isolation)
            for library in libraries:
                try:
                    # Get chunks with embeddings for this library
                    chunks = await chunk_repo.get_by_library_id(library.id, limit=1000)
                    indexed_chunks = [c for c in chunks if c.is_indexed and c.embedding]
                    
                    if not indexed_chunks:
                        continue
                    
                    print(f"🔄 Reindexing {len(indexed_chunks)} chunks for library: {library.name}")
                    
                    # Add chunks to index (production efficiency - single algorithm)
                    for chunk in indexed_chunks:
                        success = await index_service.add_chunk(
                            library_id=library.id,
                            chunk_id=chunk.id,
                            embedding=chunk.embedding,
                            metadata={"text_length": chunk.text_length},
                            build_all_algorithms=False  # Production: only default algorithm
                        )
                        if success:
                            total_reindexed += 1
                    
                    # Build indexes for this library
                    await index_service.build_library_index(library.id)
                    
                except Exception as e:
                    # Isolated error handling - continue with other libraries
                    print(f"⚠️  Failed to reindex library {library.name}: {e}")
                    continue
            
            if total_reindexed > 0:
                print(f"✅ Startup reindexing complete: {total_reindexed} chunks across {len(libraries)} libraries")
            else:
                print("ℹ️  No chunks needed reindexing")
            
            break  # Exit after successful processing
            
    except Exception as e:
        # Don't crash the app on reindexing failure
        print(f"⚠️  Startup reindexing failed: {e}")
        print("🚀 API starting without reindexing...")


def create_application() -> FastAPI:
    """
    Application factory pattern for creating FastAPI instance.
    """
    settings = get_settings()
    
    app = FastAPI(
        title="StackAI Vector Database API",
        description="A Vector Database for semantic search and document indexing",
        version="1.0.0",
        docs_url="/docs" if settings.environment == "development" else None,
        redoc_url="/redoc" if settings.environment == "development" else None,
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for container orchestration."""
        return {
            "status": "healthy",
            "service": "stack-ai-vector-db-api",
            "version": "1.0.0",
        }

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    return app


# Create the FastAPI application instance
app = create_application() 