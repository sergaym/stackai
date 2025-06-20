"""Vector search endpoints using custom indexing algorithms"""

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_search_service
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.search_service import SearchService

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def search_chunks(
    request: SearchRequest,
    algorithm: str = Query("hnsw", description="Vector index algorithm: hnsw, lsh, or brute_force"),
    search_service: SearchService = Depends(get_search_service),
) -> SearchResponse:
    """
    Perform vector similarity search using custom indexing algorithms.
    
    Supports three custom algorithms:
    - HNSW: Hierarchical Navigable Small World (best performance)
    - LSH: Locality Sensitive Hashing (high dimensions)  
    - Brute-Force: Linear search baseline (exact results)
    """
    
    # Map algorithm parameter to IndexType
    from app.indexes.index_manager import IndexType
    algorithm_map = {
        "hnsw": IndexType.HNSW,
        "lsh": IndexType.LSH,
        "brute_force": IndexType.BRUTE_FORCE
    }
    
    index_type = algorithm_map.get(algorithm.lower())
    
    # Search using SearchService (handles complete workflow)
    search_results = await search_service.search_by_text(
        library_id=request.library_id,
        query_text=request.query,
        k=request.k,
        index_type=index_type
    )
    
    # Convert to response format
    results = []
    for result in search_results:
        results.append(SearchResult(
            chunk_id=result.chunk_id,
            text=result.text,
            similarity_score=result.similarity_score,
            document_name=result.document_name
        ))
    
    # Get index stats
    index_stats = await search_service.get_search_stats(request.library_id)
    
    return SearchResponse(
        query=request.query,
        results=results,
        total_results=len(results),
        algorithm_used=algorithm.upper(),
        index_stats=index_stats
    )


