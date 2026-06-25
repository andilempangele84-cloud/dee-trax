#!/usr/bin/env python3
"""
Embedding Routes

API endpoints for text embeddings and vector operations:
- Generate embeddings
- Similarity search
- Vector storage
"""

from typing import List
from fastapi import APIRouter, Request
from pydantic import BaseModel
from loguru import logger

router = APIRouter()


class EmbeddingRequest(BaseModel):
    """Embedding request"""
    text: str
    model: str = None


class BatchEmbeddingRequest(BaseModel):
    """Batch embedding request"""
    texts: List[str]
    model: str = None


class EmbeddingResponse(BaseModel):
    """Embedding response"""
    text: str
    embedding: List[float]
    dimension: int
    model: str


class SearchRequest(BaseModel):
    """Vector search request"""
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    """Search result"""
    id: str
    score: float
    metadata: dict


@router.post("/embed", response_model=EmbeddingResponse)
async def create_embedding(request: Request, embed_req: EmbeddingRequest):
    """
    Generate embedding for text
    """
    try:
        vector_db = request.app.state.vector_db
        
        embedding = vector_db.embed(embed_req.text)
        
        return EmbeddingResponse(
            text=embed_req.text,
            embedding=embedding,
            dimension=len(embedding),
            model=vector_db.embedding_model.get_sentence_embedding_dimension()
        )
    
    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        raise


@router.post("/embed_batch")
async def create_batch_embeddings(request: Request, batch_req: BatchEmbeddingRequest):
    """
    Generate embeddings for multiple texts
    """
    try:
        vector_db = request.app.state.vector_db
        
        embeddings = vector_db.embed_batch(batch_req.texts)
        
        return {
            "embeddings": [
                {
                    "text": text,
                    "embedding": emb,
                    "dimension": len(emb)
                }
                for text, emb in zip(batch_req.texts, embeddings)
            ],
            "count": len(embeddings)
        }
    
    except Exception as e:
        logger.error(f"Batch embedding error: {str(e)}")
        raise


@router.post("/search", response_model=List[SearchResult])
async def search_vectors(request: Request, search_req: SearchRequest):
    """
    Search for similar vectors
    """
    try:
        vector_db = request.app.state.vector_db
        
        results = await vector_db.search(
            query_text=search_req.query,
            top_k=search_req.top_k
        )
        
        return [
            SearchResult(
                id=result.id,
                score=result.score,
                metadata=result.metadata
            )
            for result in results
        ]
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise
