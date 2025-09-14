"""
Neo4j Client: Handles graph database operations with vector search capabilities
"""

import os
from typing import List, Dict, Optional, Any, Tuple
import asyncio
from contextlib import asynccontextmanager

from neo4j import AsyncGraphDatabase, AsyncDriver
from neo4j.exceptions import Neo4jError

from src.utils.logger import get_logger
from src.utils.embeddings import EmbeddingService

logger = get_logger(__name__)

class Neo4jClient:
    """
    Async Neo4j client with vector search and graph traversal capabilities.
    Optimized for hybrid knowledge retrieval systems.
    """
    
    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: str = "neo4j"
    ):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "hybridpass123")
        self.database = database
        self.driver: Optional[AsyncDriver] = None
        self.embedding_service = EmbeddingService()
        
    async def connect(self):
        """Initialize Neo4j connection"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60
            )
            
            # Verify connectivity
            await self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
            
        except Neo4jError as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")
    
    @asynccontextmanager
    async def session(self):
        """Async context manager for Neo4j sessions"""
        if not self.driver:
            await self.connect()
            
        async with self.driver.session(database=self.database) as session:
            yield session
    
    async def create_vector_index(
        self,
        index_name: str,
        node_label: str,
        property_name: str,
        dimensions: int = 384,
        similarity_function: str = "cosine"
    ) -> bool:
        """Create vector index for semantic search"""
        
        create_index_query = f"""
        CREATE VECTOR INDEX {index_name} IF NOT EXISTS
        FOR (n:{node_label})
        ON (n.{property_name})
        OPTIONS {{
            indexConfig: {{
                `vector.dimensions`: {dimensions},
                `vector.similarity_function`: '{similarity_function}'
            }}
        }}
        """
        
        try:
            async with self.session() as session:
                await session.run(create_index_query)
                logger.info(f"Vector index '{index_name}' created successfully")
                return True
        except Neo4jError as e:
            logger.error(f"Failed to create vector index: {e}")
            return False
    
    async def vector_search(
        self,
        query_vector: List[float],
        index_name: str,
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        
        vector_query = f"""
        CALL db.index.vector.queryNodes($index_name, $limit, $query_vector)
        YIELD node, score
        WHERE score >= $score_threshold
        RETURN elementId(node) as id, node, score
        ORDER BY score DESC
        """
        
        try:
            async with self.session() as session:
                result = await session.run(
                    vector_query,
                    index_name=index_name,
                    limit=limit,
                    query_vector=query_vector,
                    score_threshold=score_threshold
                )
                
                records = await result.data()
                return [
                    {
                        'id': record['id'],
                        'node': dict(record['node']),
                        'score': record['score'],
                        'source': 'neo4j_vector'
                    }
                    for record in records
                ]
        except Neo4jError as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def hybrid_search(
        self,
        query: str,
        context_domains: Optional[List[str]] = None,
        limit: int = 25,
        vector_weight: float = 0.6,
        fulltext_weight: float = 0.4
    ) -> List[Dict[str, Any]]:
        """Perform hybrid vector + fulltext search in Neo4j"""
        
        # Generate query embedding
        query_embedding = await self.embedding_service.embed_text(query)
        
        # Build domain filter
        domain_filter = ""
        if context_domains:
            domain_list = "', '".join(context_domains)
            domain_filter = f"AND n.domain IN ['{domain_list}']"
        
        hybrid_query = f"""
        CALL {{
            // Vector search component
            CALL db.index.vector.queryNodes('document_embeddings', $limit, $query_vector) 
            YIELD node as vectorNode, score as vectorScore
            WHERE vectorScore >= 0.5 {domain_filter}
            
            WITH vectorNode, vectorScore * $vector_weight as weightedVectorScore
            
            // Fulltext search component  
            CALL db.index.fulltext.queryNodes('document_fulltext', $query)
            YIELD node as fulltextNode, score as fulltextScore
            WHERE fulltextNode.id = vectorNode.id
            
            WITH vectorNode as node, 
                 weightedVectorScore + (fulltextScore * $fulltext_weight) as combinedScore,
                 vectorScore, fulltextScore
            
            RETURN elementId(node) as id, node, combinedScore, vectorScore, fulltextScore
            ORDER BY combinedScore DESC
            LIMIT $limit
        }}
        """
        
        try:
            async with self.session() as session:
                result = await session.run(
                    hybrid_query,
                    query=query,
                    query_vector=query_embedding,
                    limit=limit,
                    vector_weight=vector_weight,
                    fulltext_weight=fulltext_weight
                )
                
                records = await result.data()
                return [
                    {
                        'id': record['id'],
                        'content': record['node'].get('content', ''),
                        'title': record['node'].get('title', ''),
                        'metadata': {k: v for k, v in record['node'].items() if k not in ['content', 'title', 'embedding']},
                        'score': record['combinedScore'],
                        'vector_score': record['vectorScore'],
                        'fulltext_score': record['fulltextScore'],
                        'source': 'neo4j_hybrid'
                    }
                    for record in records
                ]
        except Neo4jError as e:
            logger.error(f"Hybrid search failed: {e}")
            return []
    
    async def expand_from_entities(
        self,
        entity_ids: List[str],
        max_hops: int = 2,
        relationship_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Graph traversal from specific entities"""
        
        # Build relationship filter
        rel_filter = ""
        if relationship_types:
            rel_types = "|".join(relationship_types)
            rel_filter = f":{rel_types}"
        
        expansion_query = f"""
        UNWIND $entity_ids as entityId
        MATCH (start) WHERE elementId(start) = entityId
        
        MATCH path = (start)-[r{rel_filter}*1..$max_hops]-(connected)
        WHERE connected <> start
        
        WITH connected, path, 
             reduce(score = 1.0, rel in relationships(path) | score * 0.8) as pathScore
        
        RETURN elementId(connected) as id,
               connected,
               pathScore,
               length(path) as hops,
               [rel in relationships(path) | type(rel)] as relationshipPath
        ORDER BY pathScore DESC
        LIMIT 50
        """
        
        try:
            async with self.session() as session:
                result = await session.run(
                    expansion_query,
                    entity_ids=entity_ids,
                    max_hops=max_hops
                )
                
                records = await result.data()
                return [
                    {
                        'id': record['id'],
                        'content': record['connected'].get('content', ''),
                        'title': record['connected'].get('title', ''),
                        'metadata': dict(record['connected']),
                        'score': record['pathScore'],
                        'hops': record['hops'],
                        'relationship_path': record['relationshipPath'],
                        'source': 'neo4j_expansion'
                    }
                    for record in records
                ]
        except Neo4jError as e:
            logger.error(f"Entity expansion failed: {e}")
            return []
    
    async def graph_search(
        self,
        entities: List[str],
        query_intent: str,
        max_hops: int = 2,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Graph-based search starting from identified entities"""
        
        if not entities:
            return []
        
        # Generate intent embedding for relevance scoring
        intent_embedding = await self.embedding_service.embed_text(query_intent)
        
        graph_search_query = """
        UNWIND $entities as entityName
        
        // Find entity nodes by name or aliases
        MATCH (e) 
        WHERE toLower(e.name) CONTAINS toLower(entityName) 
           OR toLower(e.title) CONTAINS toLower(entityName)
           OR any(alias in e.aliases WHERE toLower(alias) CONTAINS toLower(entityName))
        
        // Traverse relationships to find related content
        MATCH path = (e)-[*1..$max_hops]-(related)
        WHERE related.content IS NOT NULL
        
        // Calculate path-based relevance
        WITH related, path,
             reduce(score = 1.0, rel in relationships(path) | 
                    score * CASE type(rel) 
                            WHEN 'RELATES_TO' THEN 0.9
                            WHEN 'PART_OF' THEN 0.8  
                            WHEN 'SIMILAR_TO' THEN 0.7
                            ELSE 0.6 END
             ) as pathRelevance,
             length(path) as pathLength
        
        // Combine with content similarity if embeddings exist
        WITH related, pathRelevance, pathLength,
             CASE WHEN related.embedding IS NOT NULL 
                  THEN gds.similarity.cosine(related.embedding, $intent_vector)
                  ELSE 0.0 END as contentSimilarity
        
        // Final scoring
        WITH related, 
             (pathRelevance * 0.4 + contentSimilarity * 0.6) as finalScore,
             pathRelevance, contentSimilarity, pathLength
        
        WHERE finalScore > 0.3
        
        RETURN elementId(related) as id,
               related.content as content,
               related.title as title,
               related{.*} as metadata,
               finalScore as score,
               pathRelevance,
               contentSimilarity,
               pathLength
        ORDER BY finalScore DESC
        LIMIT $limit
        """
        
        try:
            async with self.session() as session:
                result = await session.run(
                    graph_search_query,
                    entities=entities,
                    intent_vector=intent_embedding,
                    max_hops=max_hops,
                    limit=limit
                )
                
                records = await result.data()
                return [
                    {
                        'id': record['id'],
                        'content': record['content'],
                        'title': record['title'],
                        'metadata': record['metadata'],
                        'score': record['score'],
                        'path_relevance': record['pathRelevance'],
                        'content_similarity': record['contentSimilarity'],
                        'path_length': record['pathLength'],
                        'source': 'neo4j_graph'
                    }
                    for record in records
                ]
        except Neo4jError as e:
            logger.error(f"Graph search failed: {e}")
            return []
    
    async def extract_entities_from_query(self, query: str) -> List[str]:
        """Extract named entities from query using graph knowledge"""
        
        entity_extraction_query = """
        WITH split(toLower($query), ' ') as queryWords
        
        // Find entities mentioned in query
        MATCH (e) 
        WHERE any(word in queryWords WHERE 
                  toLower(e.name) CONTAINS word 
                  OR any(alias in coalesce(e.aliases, []) WHERE toLower(alias) CONTAINS word)
              )
        
        // Score by relevance
        WITH e, 
             size([word in queryWords WHERE 
                   toLower(e.name) CONTAINS word 
                   OR any(alias in coalesce(e.aliases, []) WHERE toLower(alias) CONTAINS word)
                  ]) as matchCount
        
        WHERE matchCount > 0
        
        RETURN e.name as entity, matchCount
        ORDER BY matchCount DESC
        LIMIT 10
        """
        
        try:
            async with self.session() as session:
                result = await session.run(entity_extraction_query, query=query)
                records = await result.data()
                return [record['entity'] for record in records]
        except Neo4jError as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    async def get_context_for_entities(self, entity_ids: List[str]) -> List[Dict[str, Any]]:
        """Get contextual information for specific entities"""
        
        context_query = """
        UNWIND $entity_ids as entityId
        MATCH (e) WHERE elementId(e) = entityId
        
        // Get direct relationships with context
        OPTIONAL MATCH (e)-[r]-(related)
        WHERE related.content IS NOT NULL OR related.description IS NOT NULL
        
        WITH e, collect({
            relationship: type(r),
            related_entity: related.name,
            related_content: coalesce(related.content, related.description, ''),
            related_type: labels(related)[0]
        }) as directContext
        
        // Get community/cluster information if available
        OPTIONAL MATCH (e)-[:BELONGS_TO]->(cluster)
        
        RETURN elementId(e) as id,
               e.name as name,
               e.content as content,
               directContext,
               collect(cluster.name) as clusters
        """
        
        try:
            async with self.session() as session:
                result = await session.run(context_query, entity_ids=entity_ids)
                records = await result.data()
                
                return [
                    {
                        'id': record['id'],
                        'name': record['name'],
                        'content': record['content'],
                        'direct_context': record['directContext'],
                        'clusters': record['clusters'],
                        'source': 'neo4j_context'
                    }
                    for record in records
                ]
        except Neo4jError as e:
            logger.error(f"Context retrieval failed: {e}")
            return []
    
    async def create_fulltext_index(
        self,
        index_name: str,
        node_labels: List[str],
        properties: List[str]
    ) -> bool:
        """Create fulltext search index"""
        
        labels_str = ", ".join([f"'{label}'" for label in node_labels])
        props_str = ", ".join([f"'{prop}'" for prop in properties])
        
        # For Neo4j 5.x, create fulltext index with proper syntax
        if len(node_labels) == 1:
            create_fulltext_query = f"""
            CREATE FULLTEXT INDEX {index_name} IF NOT EXISTS
            FOR (n:{node_labels[0]})
            ON EACH [n.{properties[0]}]
            """
        else:
            # Multiple labels need to be handled differently
            label_union = "|".join(node_labels)
            create_fulltext_query = f"""
            CREATE FULLTEXT INDEX {index_name} IF NOT EXISTS
            FOR (n:{label_union})
            ON EACH [n.{properties[0]}]
            """
        
        try:
            async with self.session() as session:
                await session.run(create_fulltext_query)
                logger.info(f"Fulltext index '{index_name}' created successfully")
                return True
        except Neo4jError as e:
            logger.error(f"Failed to create fulltext index: {e}")
            return False
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for monitoring"""
        
        stats_query = """
        CALL apoc.meta.stats() YIELD labels, relTypesCount, propertyKeyCount, nodeCount, relCount
        RETURN labels, relTypesCount, propertyKeyCount, nodeCount, relCount
        """
        
        try:
            async with self.session() as session:
                result = await session.run(stats_query)
                record = await result.single()
                return dict(record) if record else {}
        except Neo4jError as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}