"""
Main FastAPI application factory and configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings

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

    # Startup reindexing - Temporary. Must be persistent.
    @app.on_event("startup")
    async def startup_reindex():
        """
        Simple startup reindexing following KISS principles.
        Only reindexes existing chunks with embeddings.
        """
        try:
            from app.core.dependencies import get_index_service, get_db
            from app.repositories.async_chunk_repository import AsyncChunkRepository
            from app.repositories.async_library_repository import AsyncLibraryRepository
            
            # Get services
            index_service = get_index_service()
            
            # Get database session
            async for db_session in get_db():
                try:
                    chunk_repo = AsyncChunkRepository(db_session)
                    library_repo = AsyncLibraryRepository(db_session)
                    
                    # Get all libraries
                    libraries = await library_repo.get_all(limit=1000)  # Reasonable limit
                    
                    total_reindexed = 0
                    for library in libraries:
                        # Get indexed chunks for this library
                        chunks = await chunk_repo.get_by_library_id(library.id, limit=10000)
                        indexed_chunks = [c for c in chunks if c.is_indexed and c.embedding]
                        
                        if not indexed_chunks:
                            continue
                            
                        print(f"🔄 Reindexing {len(indexed_chunks)} chunks for library: {library.name}")
                        
                        # Add chunks to index
                        for chunk in indexed_chunks:
                            await index_service.add_chunk(
                                library_id=library.id,
                                chunk_id=chunk.id,
                                embedding=chunk.embedding,
                                metadata={"text_length": chunk.text_length}
                            )
                            total_reindexed += 1
                        
                        # Build the index for this library
                        await index_service.build_library_index(library.id)
                    
                    if total_reindexed > 0:
                        print(f"✅ Startup reindexing complete: {total_reindexed} chunks across {len(libraries)} libraries")
                    else:
                        print("ℹ️  No existing chunks to reindex")
                    
                    break  # Exit the async generator
                    
                except Exception as e:
                    print(f"⚠️  Startup reindexing failed: {e}")
                    break
                    
        except Exception as e:
            print(f"⚠️  Could not initialize startup reindexing: {e}")

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    return app


# Create the FastAPI application instance
app = create_application() 