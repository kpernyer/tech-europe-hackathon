"""
Embedding Service: Handles text embedding generation for semantic search
"""

import os
import asyncio
from typing import List, Optional, Union
import numpy as np
from functools import lru_cache

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger(__name__)

class EmbeddingService:
    """
    Service for generating text embeddings using various providers.
    Supports both local sentence-transformers and OpenAI embeddings.
    """
    
    def __init__(
        self,
        provider: str = "sentence_transformers",
        model_name: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        cache_size: int = 1000
    ):
        self.provider = provider.lower()
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        
        # Model configuration
        if self.provider == "sentence_transformers":
            self.model_name = model_name or os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            self.model = None
            self.dimensions = 384  # Default for all-MiniLM-L6-v2
        elif self.provider == "openai":
            self.model_name = model_name or os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            self.dimensions = 1536 if "3-small" in self.model_name else 3072
            if self.openai_api_key:
                openai.api_key = self.openai_api_key
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")
        
        self.cache_size = cache_size
        
        # Initialize the model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model"""
        try:
            if self.provider == "sentence_transformers":
                if not SENTENCE_TRANSFORMERS_AVAILABLE:
                    raise ImportError("sentence-transformers not installed")
                
                logger.info(f"Loading sentence-transformers model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                
                # Get actual dimensions
                test_embedding = self.model.encode(["test"])
                self.dimensions = len(test_embedding[0])
                
                logger.info(f"Model loaded successfully. Dimensions: {self.dimensions}")
                
            elif self.provider == "openai":
                if not OPENAI_AVAILABLE:
                    raise ImportError("openai package not installed")
                if not self.openai_api_key:
                    raise ValueError("OpenAI API key required for OpenAI embeddings")
                
                logger.info(f"Using OpenAI embeddings model: {self.model_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    @lru_cache(maxsize=1000)
    def _cached_embed_text(self, text: str) -> List[float]:
        """Cached version of text embedding (synchronous)"""
        return self._embed_text_sync(text)
    
    def _embed_text_sync(self, text: str) -> List[float]:
        """Synchronous text embedding"""
        try:
            if self.provider == "sentence_transformers":
                if not self.model:
                    self._initialize_model()
                
                embedding = self.model.encode([text], convert_to_tensor=False)[0]
                return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
                
            elif self.provider == "openai":
                response = openai.embeddings.create(
                    model=self.model_name,
                    input=text,
                    encoding_format="float"
                )
                return response.data[0].embedding
                
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return [0.0] * self.dimensions
    
    async def embed_text(self, text: str, use_cache: bool = True) -> List[float]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            return [0.0] * self.dimensions
        
        # Clean text
        clean_text = text.strip()
        
        if use_cache:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._cached_embed_text, clean_text)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._embed_text_sync, clean_text)
    
    async def embed_texts(self, texts: List[str], batch_size: int = 32, use_cache: bool = True) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not texts:
            return []
        
        # Clean texts
        clean_texts = [text.strip() for text in texts if text and text.strip()]
        
        if not clean_texts:
            return []
        
        embeddings = []
        
        try:
            if self.provider == "sentence_transformers":
                # Process in batches
                for i in range(0, len(clean_texts), batch_size):
                    batch = clean_texts[i:i + batch_size]
                    
                    if use_cache:
                        # Process cached items individually
                        batch_embeddings = []
                        for text in batch:
                            embedding = await self.embed_text(text, use_cache=True)
                            batch_embeddings.append(embedding)
                        embeddings.extend(batch_embeddings)
                    else:
                        # Process batch together
                        loop = asyncio.get_event_loop()
                        batch_embeddings = await loop.run_in_executor(
                            None, 
                            lambda: self.model.encode(batch, convert_to_tensor=False).tolist()
                        )
                        embeddings.extend(batch_embeddings)
            
            elif self.provider == "openai":
                # OpenAI has rate limits, so process in smaller batches
                openai_batch_size = min(batch_size, 100)  # OpenAI limit
                
                for i in range(0, len(clean_texts), openai_batch_size):
                    batch = clean_texts[i:i + openai_batch_size]
                    
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None,
                        lambda: openai.embeddings.create(
                            model=self.model_name,
                            input=batch,
                            encoding_format="float"
                        )
                    )
                    
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)
                    
                    # Small delay to respect rate limits
                    await asyncio.sleep(0.1)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            # Return zero vectors as fallback
            return [[0.0] * self.dimensions for _ in clean_texts]
    
    async def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0
    
    async def find_most_similar(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[tuple]:
        """Find most similar embeddings to query"""
        similarities = []
        
        for i, candidate in enumerate(candidate_embeddings):
            similarity = await self.cosine_similarity(query_embedding, candidate)
            similarities.append((i, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def get_dimensions(self) -> int:
        """Get embedding dimensions"""
        return self.dimensions
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            'provider': self.provider,
            'model_name': self.model_name,
            'dimensions': self.dimensions,
            'cache_size': self.cache_size
        }
    
    async def health_check(self) -> dict:
        """Check if embedding service is working"""
        try:
            test_text = "This is a test sentence for health check."
            embedding = await self.embed_text(test_text)
            
            return {
                'status': 'healthy',
                'provider': self.provider,
                'model': self.model_name,
                'dimensions': len(embedding),
                'test_embedding_length': len(embedding)
            }
        except Exception as e:
            return {
                'status': 'error',
                'provider': self.provider,
                'model': self.model_name,
                'error': str(e)
            }