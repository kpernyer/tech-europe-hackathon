#!/usr/bin/env python3
"""
Quick Start Example: Demonstrates the hybrid Neo4j + Weaviate knowledge system
"""

import asyncio
from pathlib import Path

# Add src to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.orchestrator.hybrid_search import HybridSearchOrchestrator, SearchStrategy
from src.ingestion.pipeline import IngestionPipeline
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def main():
    """Demonstrate the hybrid knowledge system"""
    
    print("🚀 Starting Hybrid Knowledge System Demo")
    print("=" * 50)
    
    # Initialize the system
    orchestrator = HybridSearchOrchestrator()
    pipeline = IngestionPipeline()
    
    try:
        # Initialize connections
        print("🔌 Initializing system connections...")
        await pipeline.initialize()
        
        # Load sample data
        print("📊 Loading sample business data...")
        await load_sample_data(pipeline)
        
        # Demo different search strategies
        print("\n🔍 Testing Search Strategies")
        print("-" * 30)
        
        await demo_search_strategies(orchestrator)
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")
    
    finally:
        # Cleanup
        await pipeline.cleanup()

async def load_sample_data(pipeline: IngestionPipeline):
    """Load sample business data for demonstration"""
    
    # Sample business documents
    sample_documents = [
        {
            'title': 'Customer Retention Strategy',
            'content': '''
            Customer retention is crucial for sustainable business growth. 
            Key factors include customer satisfaction, product quality, and service excellence.
            
            Research shows that retaining existing customers is 5-25x more cost-effective than acquiring new ones.
            Top retention strategies include:
            - Personalized communication
            - Loyalty programs
            - Proactive customer support
            - Regular feedback collection
            
            Companies with strong retention programs see 2.5x revenue growth compared to competitors.
            ''',
            'domain': 'business_strategy',
            'document_type': 'strategy_guide'
        },
        {
            'title': 'Market Analysis Q4 2024',
            'content': '''
            Q4 2024 market analysis reveals significant trends in consumer behavior.
            
            Key findings:
            - 40% increase in digital adoption
            - Shift toward sustainable products (+35%)
            - Price sensitivity remains high (78% of consumers)
            
            Market opportunities:
            1. Digital-first customer experience
            2. Sustainable product lines
            3. Value-based pricing strategies
            
            Competitive landscape shows consolidation in key segments.
            ''',
            'domain': 'market_research',
            'document_type': 'analysis'
        },
        {
            'title': 'Technology Investment ROI',
            'content': '''
            Technology investments in AI and automation show strong ROI patterns.
            
            Investment categories:
            - AI/ML platforms: 300% ROI over 2 years
            - Process automation: 250% ROI over 18 months
            - Customer analytics: 180% ROI over 1 year
            
            Success factors:
            - Clear business objectives
            - Change management support
            - Measurable performance metrics
            
            Risk factors include technology adoption challenges and skill gaps.
            ''',
            'domain': 'technology',
            'document_type': 'financial_analysis'
        }
    ]
    
    # Structured business data
    structured_data = [
        {
            'name': 'Customer Satisfaction Score',
            'metric_type': 'KPI',
            'current_value': 8.7,
            'target_value': 9.0,
            'description': 'Average customer satisfaction rating on 1-10 scale',
            'department': 'Customer Success',
            'related_initiatives': ['retention_program', 'service_excellence']
        },
        {
            'name': 'Digital Transformation Initiative',
            'project_type': 'Strategic',
            'status': 'In Progress',
            'budget': 2500000,
            'description': 'Company-wide digital transformation focusing on customer experience and operational efficiency',
            'stakeholders': ['IT', 'Operations', 'Customer Success'],
            'expected_completion': '2025-Q2'
        },
        {
            'name': 'Market Share Analysis',
            'analysis_type': 'Competitive',
            'market_segment': 'Enterprise Software',
            'current_position': 3,
            'market_size': 45000000000,
            'description': 'Analysis of competitive position in enterprise software market',
            'key_competitors': ['Microsoft', 'Salesforce', 'Oracle']
        }
    ]
    
    # Ingest sample documents
    for doc in sample_documents:
        # Create temporary file for ingestion
        temp_file = Path(f"/tmp/sample_{doc['title'].replace(' ', '_')}.txt")
        temp_file.write_text(doc['content'])
        
        await pipeline.ingest_documents(
            source_path=temp_file,
            domain=doc['domain'],
            metadata={
                'document_type': doc['document_type'],
                'sample_data': True
            }
        )
        
        # Clean up temp file
        temp_file.unlink()
    
    # Ingest structured data
    await pipeline.ingest_structured_data(
        data=structured_data,
        source_name='business_metrics',
        domain='business_intelligence'
    )
    
    print("✅ Sample data loaded successfully")

async def demo_search_strategies(orchestrator: HybridSearchOrchestrator):
    """Demonstrate different search strategies"""
    
    test_queries = [
        {
            'query': 'How to improve customer retention and reduce churn?',
            'description': 'Business strategy question'
        },
        {
            'query': 'What are the key market trends affecting our industry?',
            'description': 'Market intelligence query'
        },
        {
            'query': 'ROI analysis for technology investments',
            'description': 'Financial analysis request'
        },
        {
            'query': 'Customer satisfaction metrics and improvement initiatives',
            'description': 'Performance metrics query'
        }
    ]
    
    strategies = [
        SearchStrategy.SEMANTIC_FIRST,
        SearchStrategy.GRAPH_FIRST,
        SearchStrategy.BALANCED,
        SearchStrategy.MULTI_STEP
    ]
    
    for i, test_query in enumerate(test_queries[:2]):  # Test first 2 queries
        print(f"\n📝 Query {i+1}: {test_query['query']}")
        print(f"💡 Context: {test_query['description']}")
        print("-" * 60)
        
        for strategy in strategies:
            try:
                result = await orchestrator.search(
                    query=test_query['query'],
                    strategy=strategy,
                    max_results=5
                )
                
                print(f"\n🎯 {strategy.value.upper()} Strategy:")
                print(f"   Results: {len(result.results)}")
                print(f"   Time: {result.execution_time:.2f}s")
                print(f"   Confidence: {result.confidence_score:.2f}")
                print(f"   Sources: {result.sources}")
                
                if result.results:
                    print(f"   Top result: {result.results[0].get('title', 'N/A')[:50]}...")
                
            except Exception as e:
                print(f"   ❌ {strategy.value} failed: {e}")
        
        print()

if __name__ == "__main__":
    asyncio.run(main())