#!/usr/bin/env python3
"""
Vector Database Service

Manages embeddings and vector search across multiple vector databases:
- Pinecone
- Weaviate
- Milvus
- FAISS (local)
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger
from config.environment import settings


@dataclass
class EmbeddingVector:
    """Embedding vector data structure"""
    id: str
    vector: List[float]
    metadata: Dict


@dataclass
class SearchResult:
    """Search result data structure"""
    id: str
    score: float
    metadata: Dict


class VectorDBService:
    """Vector database service for embeddings and similarity search"""
    
    def __init__(self):
        self.embedding_model = None
        self.db_type = settings.VECTOR_DB_TYPE
        self.dimension = settings.EMBEDDING_DIMENSION
    
    async def initialize(self):
        """Initialize vector database and embedding model"""
        logger.info(f"Initializing Vector DB Service ({self.db_type})...")
        
        try:
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f"✅ Embedding model loaded: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
        
        if self.db_type == "pinecone":
            await self._init_pinecone()
        elif self.db_type == "weaviate":
            await self._init_weaviate()
        elif self.db_type == "milvus":
            await self._init_milvus()
        elif self.db_type == "faiss":
            await self._init_faiss()
        else:
            raise ValueError(f"Unknown vector DB type: {self.db_type}")
    
    async def _init_pinecone(self):
        """Initialize Pinecone vector database"""
        try:
            import pinecone
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT,
            )
            self.index = pinecone.Index(settings.PINECONE_INDEX_NAME)
            logger.info("✅ Pinecone vector DB initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise
    
    async def _init_weaviate(self):
        """Initialize Weaviate vector database"""
        try:
            import weaviate
            self.client = weaviate.Client(settings.WEAVIATE_URL)
            logger.info("✅ Weaviate vector DB initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate: {str(e)}")
            raise
    
    async def _init_milvus(self):
        """Initialize Milvus vector database"""
        try:
            from pymilvus import connections
            connections.connect(
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT,
            )
            logger.info("✅ Milvus vector DB initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Milvus: {str(e)}")
            raise
    
    async def _init_faiss(self):
        """Initialize FAISS local vector database"""
        try:
            import faiss
            self.faiss_index = faiss.IndexFlatL2(self.dimension)
            self.faiss_metadata = {}
            logger.info("✅ FAISS vector DB initialized")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {str(e)}")
            raise
    
    async def shutdown(self):
        """Shutdown vector database connections"""
        logger.info("Shutting down Vector DB Service...")
    
    async def health_check(self) -> bool:
        """Check if vector database is available"""
        try:
            if self.db_type == "pinecone":
                stats = self.index.describe_index_stats()
                return stats is not None
            elif self.db_type == "weaviate":
                return self.client.is_ready()
            elif self.db_type == "milvus":
                return True
            elif self.db_type == "faiss":
                return self.faiss_index is not None
            return False
        except Exception as e:
            logger.warning(f"Vector DB health check failed: {str(e)}")
            return False
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text"""
        if self.embedding_model is None:
            raise RuntimeError("Embedding model not initialized")
        
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if self.embedding_model is None:
            raise RuntimeError("Embedding model not initialized")
        
        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()
    
    async def upsert(self, vectors: List[EmbeddingVector]):
        """Insert or update vectors in database"""
        if self.db_type == "pinecone":
            pinecone_vectors = [(v.id, v.vector, v.metadata) for v in vectors]
            self.index.upsert(vectors=pinecone_vectors)
        elif self.db_type == "faiss":
            for v in vectors:
                self.faiss_index.add(np.array([v.vector]))
                self.faiss_metadata[v.id] = v.metadata
    
    async def search(
        self,
        query_text: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict] = None,
    ) -> List[SearchResult]:
        """Search for similar vectors"""
        query_embedding = self.embed(query_text)
        
        if self.db_type == "pinecone":
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
            )
            
            return [
                SearchResult(
                    id=match["id"],
                    score=match["score"],
                    metadata=match["metadata"],
                )
                for match in results["matches"]
            ]
        
        elif self.db_type == "faiss":
            distances, indices = self.faiss_index.search(
                np.array([query_embedding]), top_k
            )
            
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                for metadata_id, metadata in self.faiss_metadata.items():
                    results.append(
                        SearchResult(
                            id=metadata_id,
                            score=float(dist),
                            metadata=metadata,
                        )
                    )
            return results
        
        return []
