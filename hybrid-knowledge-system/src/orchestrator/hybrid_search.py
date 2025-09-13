"""
Hybrid Search Orchestrator: Coordinates queries between Neo4j and Weaviate
for optimal semantic search + graph traversal performance.
"""

import asyncio
import time
from typing import Dict, List, Optional, Union, Literal
from dataclasses import dataclass
from enum import Enum

from src.clients.neo4j_client import Neo4jClient
from src.clients.weaviate_client import WeaviateClient
from src.utils.logger import get_logger
from src.utils.cache import CacheManager

logger = get_logger(__name__)

class SearchStrategy(str, Enum):
    SEMANTIC_FIRST = "semantic_first"
    GRAPH_FIRST = "graph_first" 
    BALANCED = "balanced"
    MULTI_STEP = "multi_step"

@dataclass
class SearchResult:
    query: str
    strategy: SearchStrategy
    results: List[Dict]
    sources: Dict[str, int]
    metadata: Dict
    execution_time: float
    confidence_score: float
    
    @property
    def summary(self) -> str:
        return f"Found {len(self.results)} results in {self.execution_time:.2f}s using {self.strategy.value} strategy"

@dataclass
class HybridConfig:
    semantic_weight: float = 0.5
    graph_weight: float = 0.5
    similarity_threshold: float = 0.7
    max_hops: int = 2
    max_results: int = 50
    enable_caching: bool = True
    fusion_strategy: Literal["reciprocal_rank", "weighted", "linear"] = "reciprocal_rank"

class HybridSearchOrchestrator:
    """
    Orchestrates hybrid search across Neo4j (graph + vector) and Weaviate (semantic).
    
    Key Features:
    - Multi-strategy query execution
    - Intelligent result fusion
    - Performance optimization via caching
    - Compound learning through iterative refinement
    """
    
    def __init__(
        self,
        neo4j_client: Optional[Neo4jClient] = None,
        weaviate_client: Optional[WeaviateClient] = None,
        cache_manager: Optional[CacheManager] = None,
        config: Optional[HybridConfig] = None
    ):
        self.neo4j = neo4j_client or Neo4jClient()
        self.weaviate = weaviate_client or WeaviateClient()
        self.cache = cache_manager or CacheManager()
        self.config = config or HybridConfig()
        
    async def search(
        self,
        query: str,
        strategy: Union[SearchStrategy, str] = SearchStrategy.BALANCED,
        context_domains: Optional[List[str]] = None,
        filters: Optional[Dict] = None,
        **kwargs
    ) -> SearchResult:
        """
        Execute hybrid search using specified strategy.
        
        Args:
            query: Natural language search query
            strategy: Search strategy to use
            context_domains: Domain filters for scoped search
            filters: Additional filters for results
            **kwargs: Strategy-specific parameters
        """
        start_time = time.time()
        
        # Normalize strategy
        if isinstance(strategy, str):
            strategy = SearchStrategy(strategy)
            
        # Check cache first
        cache_key = self._generate_cache_key(query, strategy, context_domains, filters)
        if self.config.enable_caching:
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for query: {query[:50]}...")
                return cached_result
        
        # Execute search based on strategy
        logger.info(f"Executing {strategy.value} search for: {query[:100]}...")
        
        try:
            if strategy == SearchStrategy.SEMANTIC_FIRST:
                result = await self._semantic_first_search(query, context_domains, filters, **kwargs)
            elif strategy == SearchStrategy.GRAPH_FIRST:
                result = await self._graph_first_search(query, context_domains, filters, **kwargs)
            elif strategy == SearchStrategy.MULTI_STEP:
                result = await self._multi_step_search(query, context_domains, filters, **kwargs)
            else:  # BALANCED
                result = await self._balanced_search(query, context_domains, filters, **kwargs)
            
            # Calculate execution time and confidence
            execution_time = time.time() - start_time
            confidence_score = self._calculate_confidence(result, strategy)
            
            search_result = SearchResult(
                query=query,
                strategy=strategy,
                results=result.get('results', []),
                sources=result.get('sources', {}),
                metadata=result.get('metadata', {}),
                execution_time=execution_time,
                confidence_score=confidence_score
            )
            
            # Cache result
            if self.config.enable_caching:
                await self.cache.set(cache_key, search_result)
                
            logger.info(f"Search completed: {len(search_result.results)} results in {execution_time:.2f}s")
            return search_result
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return SearchResult(
                query=query,
                strategy=strategy,
                results=[],
                sources={},
                metadata={'error': str(e)},
                execution_time=time.time() - start_time,
                confidence_score=0.0
            )
    
    async def _semantic_first_search(
        self, 
        query: str, 
        context_domains: Optional[List[str]], 
        filters: Optional[Dict],
        **kwargs
    ) -> Dict:
        """Weaviate semantic search → Neo4j graph expansion"""
        
        # Step 1: Semantic search in Weaviate
        weaviate_results = await self.weaviate.semantic_search(
            query=query,
            limit=kwargs.get('semantic_limit', 20),
            threshold=self.config.similarity_threshold,
            filters=filters
        )
        
        # Step 2: Extract entity IDs for Neo4j expansion
        entity_ids = [r.get('entity_id') for r in weaviate_results if r.get('entity_id')]
        
        # Step 3: Graph traversal from semantic results
        graph_results = []
        if entity_ids:
            graph_results = await self.neo4j.expand_from_entities(
                entity_ids=entity_ids,
                max_hops=kwargs.get('max_hops', self.config.max_hops),
                relationship_types=kwargs.get('relationship_types', None)
            )
        
        # Step 4: Fuse results
        fused_results = self._fuse_results(
            weaviate_results, 
            graph_results,
            weights={'semantic': 0.7, 'graph': 0.3}
        )
        
        return {
            'results': fused_results,
            'sources': {'weaviate': len(weaviate_results), 'neo4j': len(graph_results)},
            'metadata': {'strategy_details': 'semantic_first', 'fusion_method': self.config.fusion_strategy}
        }
    
    async def _graph_first_search(
        self, 
        query: str, 
        context_domains: Optional[List[str]], 
        filters: Optional[Dict],
        **kwargs
    ) -> Dict:
        """Neo4j graph search → Weaviate semantic refinement"""
        
        # Step 1: Extract entities from query
        query_entities = await self.neo4j.extract_entities_from_query(query)
        
        # Step 2: Graph traversal from identified entities
        graph_results = await self.neo4j.graph_search(
            entities=query_entities,
            query_intent=query,
            max_hops=kwargs.get('max_hops', self.config.max_hops),
            limit=kwargs.get('graph_limit', 30)
        )
        
        # Step 3: Semantic refinement of graph results
        weaviate_results = []
        if graph_results:
            content_fragments = [r.get('content', '') for r in graph_results]
            weaviate_results = await self.weaviate.refine_results(
                query=query,
                candidates=content_fragments,
                threshold=self.config.similarity_threshold
            )
        
        # Step 4: Fuse results
        fused_results = self._fuse_results(
            weaviate_results,
            graph_results, 
            weights={'graph': 0.8, 'semantic': 0.2}
        )
        
        return {
            'results': fused_results,
            'sources': {'neo4j': len(graph_results), 'weaviate': len(weaviate_results)},
            'metadata': {'strategy_details': 'graph_first', 'identified_entities': query_entities}
        }
    
    async def _balanced_search(
        self, 
        query: str, 
        context_domains: Optional[List[str]], 
        filters: Optional[Dict],
        **kwargs
    ) -> Dict:
        """Parallel execution of both approaches → intelligent fusion"""
        
        # Execute both searches in parallel
        semantic_task = self.weaviate.semantic_search(
            query=query,
            limit=kwargs.get('limit', 25),
            threshold=self.config.similarity_threshold,
            filters=filters
        )
        
        graph_task = self.neo4j.hybrid_search(
            query=query,
            context_domains=context_domains,
            limit=kwargs.get('limit', 25)
        )
        
        weaviate_results, neo4j_results = await asyncio.gather(semantic_task, graph_task)
        
        # Intelligent fusion based on query characteristics
        fusion_weights = self._determine_fusion_weights(query, weaviate_results, neo4j_results)
        
        fused_results = self._fuse_results(
            weaviate_results,
            neo4j_results,
            weights=fusion_weights
        )
        
        return {
            'results': fused_results,
            'sources': {'weaviate': len(weaviate_results), 'neo4j': len(neo4j_results)},
            'metadata': {
                'strategy_details': 'balanced_parallel',
                'fusion_weights': fusion_weights,
                'total_candidates': len(weaviate_results) + len(neo4j_results)
            }
        }
    
    async def _multi_step_search(
        self, 
        query: str, 
        context_domains: Optional[List[str]], 
        filters: Optional[Dict],
        **kwargs
    ) -> Dict:
        """Multi-step retrieval with iterative refinement"""
        
        steps_results = []
        current_query = query
        
        for step in range(kwargs.get('max_steps', 3)):
            logger.info(f"Multi-step search - Step {step + 1}")
            
            # Step 1: Initial broad retrieval
            broad_results = await self.weaviate.semantic_search(
                query=current_query,
                limit=50,
                threshold=0.6  # Lower threshold for broader recall
            )
            
            # Step 2: Graph-based context expansion
            if broad_results:
                entity_ids = [r.get('entity_id') for r in broad_results[:10]]
                context_results = await self.neo4j.get_context_for_entities(entity_ids)
                
                # Step 3: Refine query based on found context
                if step < kwargs.get('max_steps', 3) - 1:
                    current_query = await self._refine_query_with_context(
                        original_query=query,
                        context=context_results
                    )
            
            steps_results.append({
                'step': step + 1,
                'query': current_query,
                'results': broad_results,
                'context_expansion': len(context_results) if 'context_results' in locals() else 0
            })
        
        # Final fusion of all step results
        all_results = []
        for step_result in steps_results:
            all_results.extend(step_result['results'])
        
        # Remove duplicates and rank
        final_results = self._deduplicate_and_rank(all_results, query)
        
        return {
            'results': final_results,
            'sources': {'multi_step_total': len(all_results), 'final_unique': len(final_results)},
            'metadata': {
                'strategy_details': 'multi_step_iterative',
                'steps_executed': len(steps_results),
                'query_evolution': [s['query'] for s in steps_results]
            }
        }
    
    def _fuse_results(
        self, 
        weaviate_results: List[Dict], 
        neo4j_results: List[Dict],
        weights: Dict[str, float]
    ) -> List[Dict]:
        """Fuse results from multiple sources using specified strategy"""
        
        if self.config.fusion_strategy == "reciprocal_rank":
            return self._reciprocal_rank_fusion(weaviate_results, neo4j_results, weights)
        elif self.config.fusion_strategy == "weighted":
            return self._weighted_fusion(weaviate_results, neo4j_results, weights)
        else:  # linear
            return self._linear_fusion(weaviate_results, neo4j_results, weights)
    
    def _reciprocal_rank_fusion(
        self, 
        weaviate_results: List[Dict], 
        neo4j_results: List[Dict],
        weights: Dict[str, float]
    ) -> List[Dict]:
        """Reciprocal Rank Fusion (RRF) for combining ranked lists"""
        
        k = 60  # RRF constant
        fused_scores = {}
        
        # Process Weaviate results
        for i, result in enumerate(weaviate_results):
            doc_id = result.get('id', f"weaviate_{i}")
            score = weights.get('semantic', 0.5) / (k + i + 1)
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + score
            result['fusion_score'] = fused_scores[doc_id]
            result['source'] = 'weaviate'
        
        # Process Neo4j results  
        for i, result in enumerate(neo4j_results):
            doc_id = result.get('id', f"neo4j_{i}")
            score = weights.get('graph', 0.5) / (k + i + 1)
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + score
            result['fusion_score'] = fused_scores[doc_id]
            result['source'] = 'neo4j'
        
        # Combine and sort by fusion score
        all_results = weaviate_results + neo4j_results
        return sorted(all_results, key=lambda x: x.get('fusion_score', 0), reverse=True)[:self.config.max_results]
    
    def _weighted_fusion(self, weaviate_results: List[Dict], neo4j_results: List[Dict], weights: Dict[str, float]) -> List[Dict]:
        """Simple weighted combination of results"""
        # Implementation for weighted fusion
        pass
    
    def _linear_fusion(self, weaviate_results: List[Dict], neo4j_results: List[Dict], weights: Dict[str, float]) -> List[Dict]:
        """Linear combination fusion"""
        # Implementation for linear fusion  
        pass
    
    def _determine_fusion_weights(self, query: str, weaviate_results: List[Dict], neo4j_results: List[Dict]) -> Dict[str, float]:
        """Dynamically determine optimal fusion weights based on query characteristics"""
        
        # Analyze query for graph vs semantic indicators
        graph_keywords = ['relationship', 'connected', 'related', 'impact', 'cause', 'effect', 'network']
        semantic_keywords = ['similar', 'like', 'meaning', 'concept', 'understanding']
        
        query_lower = query.lower()
        graph_signals = sum(1 for kw in graph_keywords if kw in query_lower)
        semantic_signals = sum(1 for kw in semantic_keywords if kw in query_lower)
        
        # Analyze result quality
        weaviate_avg_score = sum(r.get('score', 0) for r in weaviate_results) / max(len(weaviate_results), 1)
        neo4j_avg_score = sum(r.get('score', 0) for r in neo4j_results) / max(len(neo4j_results), 1)
        
        # Calculate adaptive weights
        if graph_signals > semantic_signals and neo4j_avg_score > weaviate_avg_score:
            return {'graph': 0.7, 'semantic': 0.3}
        elif semantic_signals > graph_signals and weaviate_avg_score > neo4j_avg_score:
            return {'semantic': 0.7, 'graph': 0.3}
        else:
            return {'graph': 0.5, 'semantic': 0.5}
    
    def _calculate_confidence(self, result: Dict, strategy: SearchStrategy) -> float:
        """Calculate confidence score for search results"""
        
        results = result.get('results', [])
        if not results:
            return 0.0
        
        # Base confidence on result count and average scores
        result_count_factor = min(len(results) / 10, 1.0)  # Normalized to 10 results
        avg_score = sum(r.get('score', 0) for r in results) / len(results)
        
        # Strategy-specific adjustments
        strategy_multiplier = {
            SearchStrategy.SEMANTIC_FIRST: 0.9,
            SearchStrategy.GRAPH_FIRST: 0.85,
            SearchStrategy.BALANCED: 1.0,
            SearchStrategy.MULTI_STEP: 0.95
        }.get(strategy, 1.0)
        
        return min(result_count_factor * avg_score * strategy_multiplier, 1.0)
    
    def _generate_cache_key(self, query: str, strategy: SearchStrategy, context_domains: Optional[List[str]], filters: Optional[Dict]) -> str:
        """Generate cache key for query results"""
        import hashlib
        
        key_components = [
            query,
            strategy.value,
            str(sorted(context_domains)) if context_domains else "",
            str(sorted(filters.items())) if filters else ""
        ]
        
        key_string = "|".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _refine_query_with_context(self, original_query: str, context: List[Dict]) -> str:
        """Refine query based on retrieved context for multi-step search"""
        # Placeholder - would integrate with LLM for query refinement
        return original_query
    
    def _deduplicate_and_rank(self, results: List[Dict], query: str) -> List[Dict]:
        """Remove duplicates and rank final results"""
        seen_ids = set()
        unique_results = []
        
        for result in results:
            doc_id = result.get('id', result.get('entity_id', ''))
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                unique_results.append(result)
        
        # Re-rank based on relevance to original query
        # Placeholder for more sophisticated ranking
        return sorted(unique_results, key=lambda x: x.get('score', 0), reverse=True)[:self.config.max_results]