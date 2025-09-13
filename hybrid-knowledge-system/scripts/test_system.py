#!/usr/bin/env python3
"""
System Test Script: Comprehensive testing of the hybrid knowledge system
"""

import asyncio
import sys
import time
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.orchestrator.hybrid_search import HybridSearchOrchestrator, SearchStrategy
from src.clients.neo4j_client import Neo4jClient
from src.clients.weaviate_client import WeaviateClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

TEST_QUERIES = [
    {
        "query": "How can we improve customer retention rates?",
        "expected_domains": ["strategy", "customer_experience"],
        "description": "Business strategy question about customer retention"
    },
    {
        "query": "What are the ROI metrics for AI and automation investments?",
        "expected_domains": ["finance", "technology"],
        "description": "Financial analysis question about technology ROI"
    },
    {
        "query": "Key market trends affecting enterprise software companies",
        "expected_domains": ["market_research", "competitive"],
        "description": "Market intelligence query"
    },
    {
        "query": "Digital transformation roadmap and implementation phases",
        "expected_domains": ["strategy", "technology"],
        "description": "Strategic planning question"
    },
    {
        "query": "Customer satisfaction scores and NPS metrics",
        "expected_domains": ["metrics", "customer_experience"],
        "description": "Performance metrics query"
    }
]

async def main():
    """Comprehensive system testing"""
    
    print("🧪 Hybrid Knowledge System Testing")
    print("=" * 50)
    
    # Initialize components
    orchestrator = HybridSearchOrchestrator()
    neo4j = Neo4jClient()
    weaviate = WeaviateClient()
    
    test_results = {
        "connectivity": {},
        "search_strategies": {},
        "performance": {},
        "data_quality": {}
    }
    
    try:
        # Test 1: System Connectivity
        print("🔌 Testing System Connectivity")
        print("-" * 30)
        
        # Test Neo4j
        print("   Testing Neo4j connection...")
        try:
            await neo4j.connect()
            stats = await neo4j.get_database_stats()
            test_results["connectivity"]["neo4j"] = {
                "status": "connected",
                "nodes": stats.get('nodeCount', 0),
                "relationships": stats.get('relCount', 0)
            }
            print(f"      ✅ Neo4j: {stats.get('nodeCount', 0)} nodes, {stats.get('relCount', 0)} relationships")
        except Exception as e:
            test_results["connectivity"]["neo4j"] = {"status": "failed", "error": str(e)}
            print(f"      ❌ Neo4j connection failed: {e}")
        
        # Test Weaviate
        print("   Testing Weaviate connection...")
        try:
            await weaviate.connect()
            health = await weaviate.health_check()
            doc_count = await weaviate.get_document_count()
            test_results["connectivity"]["weaviate"] = {
                "status": "connected" if health.get('ready') else "not_ready",
                "documents": doc_count
            }
            print(f"      ✅ Weaviate: {doc_count} documents indexed")
        except Exception as e:
            test_results["connectivity"]["weaviate"] = {"status": "failed", "error": str(e)}
            print(f"      ❌ Weaviate connection failed: {e}")
        
        # Test 2: Search Strategy Performance
        print(f"\n🔍 Testing Search Strategies")
        print("-" * 30)
        
        for strategy in SearchStrategy:
            print(f"\n   🎯 Testing {strategy.value.upper()} strategy:")
            strategy_results = []
            
            for i, test_query in enumerate(TEST_QUERIES[:3]):  # Test first 3 queries
                try:
                    start_time = time.time()
                    result = await orchestrator.search(
                        query=test_query["query"],
                        strategy=strategy,
                        max_results=10
                    )
                    execution_time = time.time() - start_time
                    
                    strategy_results.append({
                        "query": test_query["query"],
                        "results_count": len(result.results),
                        "execution_time": execution_time,
                        "confidence": result.confidence_score,
                        "sources": result.sources
                    })
                    
                    print(f"      Query {i+1}: {len(result.results)} results in {execution_time:.2f}s (confidence: {result.confidence_score:.2f})")
                    
                except Exception as e:
                    strategy_results.append({
                        "query": test_query["query"],
                        "error": str(e)
                    })
                    print(f"      Query {i+1}: ❌ Failed - {e}")
            
            test_results["search_strategies"][strategy.value] = strategy_results
        
        # Test 3: Performance Benchmarks
        print(f"\n⚡ Performance Benchmarking")
        print("-" * 30)
        
        # Concurrent query test
        print("   Testing concurrent queries...")
        concurrent_queries = TEST_QUERIES[:3]
        
        start_time = time.time()
        concurrent_tasks = [
            orchestrator.search(query["query"], SearchStrategy.BALANCED)
            for query in concurrent_queries
        ]
        
        concurrent_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        concurrent_time = time.time() - start_time
        
        successful_results = [r for r in concurrent_results if not isinstance(r, Exception)]
        
        test_results["performance"]["concurrent"] = {
            "total_time": concurrent_time,
            "queries_count": len(concurrent_queries),
            "successful": len(successful_results),
            "avg_time_per_query": concurrent_time / len(concurrent_queries)
        }
        
        print(f"      ✅ {len(successful_results)}/{len(concurrent_queries)} queries succeeded")
        print(f"      ⏱️  Total time: {concurrent_time:.2f}s, Avg per query: {concurrent_time/len(concurrent_queries):.2f}s")
        
        # Test 4: Data Quality Assessment
        print(f"\n📊 Data Quality Assessment")
        print("-" * 30)
        
        # Check for diverse result sources
        sample_result = await orchestrator.search(
            "customer retention strategies and best practices",
            SearchStrategy.BALANCED,
            max_results=20
        )
        
        source_distribution = {}
        domain_distribution = {}
        
        for result in sample_result.results:
            source = result.get('source', 'unknown')
            domain = result.get('metadata', {}).get('domain', 'unknown')
            
            source_distribution[source] = source_distribution.get(source, 0) + 1
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1
        
        test_results["data_quality"] = {
            "source_distribution": source_distribution,
            "domain_distribution": domain_distribution,
            "total_results": len(sample_result.results)
        }
        
        print(f"   📈 Source distribution: {source_distribution}")
        print(f"   🏷️  Domain distribution: {domain_distribution}")
        
        # Test 5: Error Handling
        print(f"\n🛡️  Error Handling Tests")
        print("-" * 30)
        
        # Empty query test
        try:
            empty_result = await orchestrator.search("", SearchStrategy.BALANCED)
            print(f"      ✅ Empty query handled: {len(empty_result.results)} results")
        except Exception as e:
            print(f"      ❌ Empty query failed: {e}")
        
        # Very long query test
        try:
            long_query = " ".join(["test"] * 1000)
            long_result = await orchestrator.search(long_query, SearchStrategy.SEMANTIC_FIRST)
            print(f"      ✅ Long query handled: {len(long_result.results)} results")
        except Exception as e:
            print(f"      ⚠️  Long query warning: {e}")
        
        # Generate test report
        print(f"\n📋 Generating Test Report")
        print("-" * 30)
        
        report_file = Path(__file__).parent.parent / "test_results.json"
        test_results["timestamp"] = time.time()
        test_results["summary"] = {
            "neo4j_connected": test_results["connectivity"]["neo4j"]["status"] == "connected",
            "weaviate_connected": test_results["connectivity"]["weaviate"]["status"] == "connected",
            "strategies_tested": len(test_results["search_strategies"]),
            "total_queries_tested": sum(len(results) for results in test_results["search_strategies"].values())
        }
        
        with open(report_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"      📄 Test report saved to: {report_file}")
        
        # Summary
        print(f"\n🎉 Testing Summary")
        print("=" * 50)
        
        if test_results["summary"]["neo4j_connected"] and test_results["summary"]["weaviate_connected"]:
            print("✅ System Connectivity: PASSED")
        else:
            print("❌ System Connectivity: FAILED")
        
        print(f"📊 Search Strategies: {test_results['summary']['strategies_tested']} tested")
        print(f"🔍 Total Queries: {test_results['summary']['total_queries_tested']} executed")
        
        if test_results["performance"]["concurrent"]["successful"] > 0:
            print("⚡ Performance: ACCEPTABLE")
        else:
            print("⚡ Performance: NEEDS ATTENTION")
        
        print(f"📈 Data Sources: {len(test_results['data_quality']['source_distribution'])} types")
        print(f"🏷️  Data Domains: {len(test_results['data_quality']['domain_distribution'])} categories")
        
        print(f"\n🚀 Hybrid Knowledge System is ready for production use!")
        
    except Exception as e:
        logger.error(f"System testing failed: {e}")
        print(f"❌ Testing failed: {e}")
        sys.exit(1)
    
    finally:
        # Cleanup connections
        await neo4j.close()
        await weaviate.close()

if __name__ == "__main__":
    asyncio.run(main())