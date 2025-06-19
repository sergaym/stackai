"""Simple embedding service using Cohere API."""

import logging
from typing import List
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using Cohere API."""
    if not texts:
        return []
    
    if not settings.cohere_api_key:
        # Simple mock for development
        return [[0.1] * 1024 for _ in texts]
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.cohere.com/v2/embed",
            headers={
                "Authorization": f"Bearer {settings.cohere_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "texts": texts,
                "model": "embed-english-v3.0",
                "embedding_types": ["float"],
                "input_type": "search_document"
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["embeddings"]["float"]
        else:
            logger.error(f"Cohere API error: {response.status_code}")
            # Return mock embeddings on error
            return [[0.1] * 1024 for _ in texts]


async def generate_query_embedding(query: str) -> List[float]:
    """Generate embedding for search query."""
    embeddings = await generate_embeddings([query])
    return embeddings[0] if embeddings else [0.1] * 1024 