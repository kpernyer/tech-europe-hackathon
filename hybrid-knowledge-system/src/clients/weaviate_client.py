"""
Weaviate Client: Handles vector database operations for semantic search
"""

import os
import asyncio
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass

import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import Filter, MetadataQuery
from weaviate.collections.classes.filters import _Filters
from weaviate.exceptions import WeaviateBaseError

from src.utils.logger import get_logger
from src.utils.embeddings import EmbeddingService

logger = get_logger(__name__)

@dataclass
class WeaviateConfig:
    url: str = "http://localhost:8080"
    api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    default_class: str = "Document"
    vector_dimensions: int = 384

class WeaviateClient:
    """
    Async-compatible Weaviate client optimized for semantic search
    in hybrid knowledge retrieval systems.
    """
    
    def __init__(self, config: Optional[WeaviateConfig] = None):
        self.config = config or WeaviateConfig(
            url=os.getenv("WEAVIATE_URL", "http://localhost:8080"),
            api_key=os.getenv("WEAVIATE_API_KEY"),
            openai_api_key=os.getenv("WEAVIATE_OPENAI_API_KEY")
        )
        
        self.client: Optional[weaviate.WeaviateClient] = None
        self.embedding_service = EmbeddingService()
        
    async def connect(self):
        """Initialize Weaviate connection"""
        try:
            # Configure authentication
            auth_config = None
            if self.config.api_key:
                auth_config = weaviate.auth.AuthApiKey(api_key=self.config.api_key)
            
            # Additional headers for OpenAI integration
            additional_headers = {}
            if self.config.openai_api_key:
                additional_headers["X-OpenAI-Api-Key"] = self.config.openai_api_key
            
            # Connect without auth for local development
            if auth_config:
                self.client = weaviate.WeaviateClient(
                    url=self.config.url,
                    auth_client_secret=auth_config,
                    additional_headers=additional_headers
                )
            else:
                self.client = weaviate.connect_to_local(
                    host=self.config.url.replace("http://", "").replace("https://", "")
                )
            
            # Test connection
            await self._test_connection()
            logger.info(f"Connected to Weaviate at {self.config.url}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Weaviate: {e}")
            raise
    
    async def close(self):
        """Close Weaviate connection"""
        if self.client:
            self.client.close()
            logger.info("Weaviate connection closed")
    
    async def _test_connection(self):
        """Test Weaviate connectivity"""
        try:
            # Run in executor to make it async
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: self.client.is_ready())
        except Exception as e:
            raise Exception(f"Weaviate connection test failed: {e}")
    
    async def create_schema(self, class_name: str = None, force_recreate: bool = False) -> bool:
        """Create Weaviate schema for hybrid search"""
        
        if not self.client:
            await self.connect()
        
        class_name = class_name or self.config.default_class
        
        try:
            # Check if class exists
            if self.client.collections.exists(class_name):
                if force_recreate:
                    logger.info(f"Deleting existing class: {class_name}")
                    self.client.collections.delete(class_name)
                else:
                    logger.info(f"Class {class_name} already exists")
                    return True
            
            # Create collection with schema
            collection = self.client.collections.create(
                name=class_name,
                properties=[
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="entity_id", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                    Property(name="document_type", data_type=DataType.TEXT),
                    Property(name="domain", data_type=DataType.TEXT),
                    Property(name="created_at", data_type=DataType.DATE),
                    Property(name="metadata", data_type=DataType.OBJECT),
                    Property(name="chunk_index", data_type=DataType.INT),
                    Property(name="parent_document_id", data_type=DataType.TEXT),
                ],
                vectorizer_config=Configure.Vectorizer.text2vec_transformers(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                ),
                # Alternative: Use OpenAI embeddings if configured
                # vectorizer_config=Configure.Vectorizer.text2vec_openai(
                #     model="text-embedding-3-small"
                # ),
                vector_index_config=Configure.VectorIndex.hnsw(
                    distance_metric="cosine",
                    dynamic_ef_factor=8,
                    dynamic_ef_max=500,
                    ef_construction=128,
                    max_connections=32,
                    vector_cache_max_objects=100000
                ),
                generative_config=Configure.Generative.openai() if self.config.openai_api_key else None
            )
            
            logger.info(f"Created Weaviate class: {class_name}")
            return True
            
        except WeaviateBaseError as e:
            logger.error(f"Failed to create Weaviate schema: {e}")
            return False
    
    async def semantic_search(
        self,
        query: str,
        class_name: Optional[str] = None,
        limit: int = 25,
        threshold: float = 0.7,
        filters: Optional[Dict] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """Perform semantic similarity search"""
        
        if not self.client:
            await self.connect()
        
        class_name = class_name or self.config.default_class
        
        try:
            collection = self.client.collections.get(class_name)
            
            # Build where filter
            where_filter = None
            if filters:
                where_conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        where_conditions.append(Filter.by_property(key).contains_any(value))
                    else:
                        where_conditions.append(Filter.by_property(key).equal(value))
                
                if len(where_conditions) == 1:
                    where_filter = where_conditions[0]
                elif len(where_conditions) > 1:
                    where_filter = Filter.all_of(where_conditions)
            
            # Execute search
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: collection.query.near_text(
                    query=query,
                    limit=limit,
                    distance=1.0 - threshold,  # Convert similarity to distance
                    where=where_filter,
                    include_vector=False,
                    return_metadata=MetadataQuery(distance=True, certainty=True)
                )
            )
            
            results = []
            for obj in response.objects:
                result = {
                    'id': str(obj.uuid),
                    'content': obj.properties.get('content', ''),
                    'title': obj.properties.get('title', ''),
                    'entity_id': obj.properties.get('entity_id'),
                    'source': obj.properties.get('source', 'weaviate'),
                    'document_type': obj.properties.get('document_type'),
                    'domain': obj.properties.get('domain'),
                    'metadata': obj.properties.get('metadata', {}),
                    'score': obj.metadata.certainty if obj.metadata else 0.0,
                    'distance': obj.metadata.distance if obj.metadata else 1.0,
                    'weaviate_source': 'semantic_search'
                }
                
                # Filter by similarity threshold
                if result['score'] >= threshold:
                    results.append(result)
            
            logger.info(f"Semantic search returned {len(results)} results")
            return results
            
        except WeaviateBaseError as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def refine_results(
        self,
        query: str,
        candidates: List[str],
        threshold: float = 0.7,
        class_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Refine/rerank candidate results using semantic similarity"""
        
        if not candidates:
            return []
        
        # Generate query embedding
        query_embedding = await self.embedding_service.embed_text(query)
        
        # Generate embeddings for candidates
        candidate_embeddings = await self.embedding_service.embed_texts(candidates)
        
        # Calculate similarities
        results = []
        for i, (candidate, embedding) in enumerate(zip(candidates, candidate_embeddings)):
            similarity = await self.embedding_service.cosine_similarity(query_embedding, embedding)
            
            if similarity >= threshold:
                results.append({
                    'id': f'refined_{i}',
                    'content': candidate,
                    'score': similarity,
                    'source': 'weaviate_refined',
                    'original_index': i
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Refined {len(candidates)} candidates to {len(results)} results")
        return results
    
    async def hybrid_search_with_keywords(
        self,
        query: str,
        keywords: List[str],
        class_name: Optional[str] = None,
        limit: int = 25,
        alpha: float = 0.7  # Weight for vector search vs keyword search
    ) -> List[Dict[str, Any]]:
        """Hybrid search combining vector similarity and keyword matching"""
        
        if not self.client:
            await self.connect()
        
        class_name = class_name or self.config.default_class
        
        try:
            collection = self.client.collections.get(class_name)
            
            # Execute hybrid search
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: collection.query.hybrid(
                    query=query,
                    alpha=alpha,  # 0 = pure keyword, 1 = pure vector
                    limit=limit,
                    return_metadata=MetadataQuery(score=True, explain_score=True)
                )
            )
            
            results = []
            for obj in response.objects:
                result = {
                    'id': str(obj.uuid),
                    'content': obj.properties.get('content', ''),
                    'title': obj.properties.get('title', ''),
                    'entity_id': obj.properties.get('entity_id'),
                    'metadata': obj.properties.get('metadata', {}),
                    'score': obj.metadata.score if obj.metadata else 0.0,
                    'source': 'weaviate_hybrid',
                    'score_explanation': obj.metadata.explain_score if obj.metadata else None
                }
                results.append(result)
            
            logger.info(f"Hybrid search returned {len(results)} results")
            return results
            
        except WeaviateBaseError as e:
            logger.error(f"Hybrid search failed: {e}")
            return []
    
    async def add_document(
        self,
        content: str,
        title: str = "",
        entity_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        class_name: Optional[str] = None
    ) -> str:
        """Add a document to Weaviate"""
        
        if not self.client:
            await self.connect()
        
        class_name = class_name or self.config.default_class
        
        try:
            collection = self.client.collections.get(class_name)
            
            properties = {
                'content': content,
                'title': title,
                'entity_id': entity_id,
                'source': 'manual_upload',
                'metadata': metadata or {},
                'created_at': str(asyncio.get_event_loop().time())
            }
            
            # Add additional metadata fields
            if metadata:
                for key in ['document_type', 'domain', 'parent_document_id', 'chunk_index']:
                    if key in metadata:
                        properties[key] = metadata[key]
            
            loop = asyncio.get_event_loop()
            uuid = await loop.run_in_executor(
                None,
                lambda: collection.data.insert(properties)
            )
            
            logger.info(f"Added document to Weaviate: {uuid}")
            return str(uuid)
            
        except WeaviateBaseError as e:
            logger.error(f"Failed to add document: {e}")
            raise
    
    async def batch_add_documents(
        self,
        documents: List[Dict[str, Any]],
        class_name: Optional[str] = None,
        batch_size: int = 100
    ) -> List[str]:
        """Batch add multiple documents to Weaviate"""
        
        if not self.client:
            await self.connect()
        
        class_name = class_name or self.config.default_class
        
        try:
            collection = self.client.collections.get(class_name)
            added_uuids = []
            
            # Process in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                # Prepare batch data
                batch_objects = []
                for doc in batch:
                    properties = {
                        'content': doc.get('content', ''),
                        'title': doc.get('title', ''),
                        'entity_id': doc.get('entity_id'),
                        'source': doc.get('source', 'batch_upload'),
                        'document_type': doc.get('document_type', ''),
                        'domain': doc.get('domain', ''),
                        'metadata': doc.get('metadata', {}),
                        'created_at': str(asyncio.get_event_loop().time())
                    }
                    batch_objects.append(properties)
                
                # Execute batch insert
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: collection.data.insert_many(batch_objects)
                )
                
                if hasattr(result, 'uuids'):
                    added_uuids.extend([str(uuid) for uuid in result.uuids])
                
                logger.info(f"Batch {i//batch_size + 1}: Added {len(batch)} documents")
            
            logger.info(f"Batch operation completed: {len(added_uuids)} documents added")
            return added_uuids
            
        except WeaviateBaseError as e:
            logger.error(f"Batch add failed: {e}")
            return []
    
    async def update_document(
        self,
        document_id: str,
        properties: Dict[str, Any],
        class_name: Optional[str] = None
    ) -> bool:
        """Update document properties"""
        
        if not self.client:
            await self.connect()
        
        class_name = class_name or self.config.default_class
        
        try:
            collection = self.client.collections.get(class_name)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: collection.data.update(
                    uuid=document_id,
                    properties=properties
                )
            )
            
            logger.info(f"Updated document: {document_id}")
            return True
            
        except WeaviateBaseError as e:
            logger.error(f"Failed to update document: {e}")
            return False
    
    async def delete_document(
        self,
        document_id: str,
        class_name: Optional[str] = None
    ) -> bool:
        """Delete a document from Weaviate"""
        
        if not self.client:
            await self.connect()
        
        class_name = class_name or self.config.default_class
        
        try:
            collection = self.client.collections.get(class_name)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: collection.data.delete_by_id(document_id)
            )
            
            logger.info(f"Deleted document: {document_id}")
            return True
            
        except WeaviateBaseError as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    async def get_document_count(self, class_name: Optional[str] = None) -> int:
        """Get total document count"""
        
        if not self.client:
            await self.connect()
        
        class_name = class_name or self.config.default_class
        
        try:
            collection = self.client.collections.get(class_name)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: collection.aggregate.over_all(total_count=True)
            )
            
            return response.total_count if hasattr(response, 'total_count') else 0
            
        except WeaviateBaseError as e:
            logger.error(f"Failed to get document count: {e}")
            return 0
    
    async def get_schema_info(self) -> Dict[str, Any]:
        """Get Weaviate schema information"""
        
        if not self.client:
            await self.connect()
        
        try:
            loop = asyncio.get_event_loop()
            schema = await loop.run_in_executor(
                None,
                lambda: self.client.schema.get()
            )
            
            return schema
            
        except WeaviateBaseError as e:
            logger.error(f"Failed to get schema info: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Weaviate health and performance metrics"""
        
        if not self.client:
            await self.connect()
        
        try:
            # Test basic connectivity and get cluster status
            loop = asyncio.get_event_loop()
            
            is_ready = await loop.run_in_executor(None, lambda: self.client.is_ready())
            is_live = await loop.run_in_executor(None, lambda: self.client.is_live())
            
            # Get cluster nodes info
            cluster_status = await loop.run_in_executor(
                None,
                lambda: self.client.cluster.get_nodes_status()
            )
            
            return {
                'ready': is_ready,
                'live': is_live,
                'cluster_status': cluster_status,
                'timestamp': asyncio.get_event_loop().time()
            }
            
        except WeaviateBaseError as e:
            logger.error(f"Health check failed: {e}")
            return {'ready': False, 'live': False, 'error': str(e)}