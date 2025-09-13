#!/usr/bin/env python3
"""
WellnessRoberts Care Data Ingestion Script
Loads healthcare organization data into hybrid knowledge system
"""

import asyncio
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.ingestion.pipeline import IngestionPipeline
from src.clients.neo4j_client import Neo4jClient
from src.clients.weaviate_client import WeaviateClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def create_organizational_graph(neo4j_client):
    """Create organizational structure as graph relationships"""

    # Load organization data
    org_path = Path("examples/wellnessroberts_data/organization_profile.json")
    with open(org_path, 'r') as f:
        org_data = json.load(f)

    print("🏗️  Creating organizational graph structure...")

    # Create organization node
    org = org_data['organization']
    async with neo4j_client.session() as session:
        await session.run(
            """
            MERGE (o:Organization {id: $id})
            SET o.name = $name,
                o.industry = $industry,
                o.size = $size,
                o.revenue_range = $revenue_range,
                o.digital_maturity = $digital_maturity,
                o.innovation_index = $innovation_index
            """,
            {
                'id': org['id'],
                'name': org['name'],
                'industry': org['industry'],
                'size': org['size'],
                'revenue_range': org['revenue_range'],
                'digital_maturity': org['digital_maturity'],
                'innovation_index': org['innovation_index']
            }
        )

    # Create departments with relationships
    for dept in org_data['departments']:
        async with neo4j_client.session() as session:
            await session.run(
            """
            MATCH (o:Organization {id: $org_id})
            MERGE (d:Department {name: $name, organization_id: $org_id})
            SET d.head = $head,
                d.staff_count = $staff_count,
                d.budget_annual = $budget_annual,
                d.strategic_priority = $strategic_priority
            MERGE (o)-[:HAS_DEPARTMENT]->(d)
            """,
            {
                'org_id': org['id'],
                'name': dept['name'],
                'head': dept['head'],
                'staff_count': dept['staff_count'],
                'budget_annual': dept['budget_annual'],
                'strategic_priority': dept['strategic_priority']
            }
        )

    # Create products with relationships
    for product in org_data['products']:
        async with neo4j_client.session() as session:
            await session.run(
            """
            MATCH (o:Organization {id: $org_id})
            MERGE (p:Product {name: $name, organization_id: $org_id})
            SET p.category = $category,
                p.revenue_annual = $revenue_annual,
                p.users = $users,
                p.description = $description
            MERGE (o)-[:OFFERS_PRODUCT]->(p)
            """,
            {
                'org_id': org['id'],
                'name': product['name'],
                'category': product['category'],
                'revenue_annual': product['revenue_annual'],
                'users': product['users'],
                'description': product['description']
            }
        )

    # Create strategic priorities with relationships
    for priority in org_data['strategic_priorities']:
        async with neo4j_client.session() as session:
            await session.run(
            """
            MATCH (o:Organization {id: $org_id})
            MERGE (sp:StrategicPriority {name: $name, organization_id: $org_id})
            SET sp.description = $description,
                sp.target_metrics = $target_metrics,
                sp.budget_allocation = $budget_allocation,
                sp.timeline = $timeline
            MERGE (o)-[:HAS_PRIORITY]->(sp)
            """,
            {
                'org_id': org['id'],
                'name': priority['name'],
                'description': priority['description'],
                'target_metrics': priority['target_metrics'],
                'budget_allocation': priority['budget_allocation'],
                'timeline': priority['timeline']
            }
        )

    # Create challenges with impact relationships
    for challenge in org_data['current_challenges']:
        async with neo4j_client.session() as session:
            await session.run(
            """
            MATCH (o:Organization {id: $org_id})
            MERGE (c:Challenge {challenge: $challenge, organization_id: $org_id})
            SET c.impact = $impact,
                c.timeline_critical = $timeline_critical,
                c.budget_requirement = $budget_requirement
            MERGE (o)-[:FACES_CHALLENGE]->(c)
            """,
            {
                'org_id': org['id'],
                'challenge': challenge['challenge'],
                'impact': challenge['impact'],
                'timeline_critical': challenge['timeline_critical'],
                'budget_requirement': challenge['budget_requirement']
            }
        )

        # Connect challenges to affected departments
        for dept_name in challenge['departments_affected']:
            async with neo4j_client.session() as session:
                await session.run(
                """
                MATCH (c:Challenge {challenge: $challenge}),
                      (d:Department {name: $dept_name})
                MERGE (c)-[:AFFECTS_DEPARTMENT]->(d)
                """,
                {
                    'challenge': challenge['challenge'],
                    'dept_name': dept_name
                }
            )

    print("   ✅ Organizational graph structure created")

async def main():
    """Load WellnessRoberts Care data into hybrid knowledge system"""

    print("🏥 Loading WellnessRoberts Care Data")
    print("=" * 60)

    # Initialize services
    neo4j = Neo4jClient()
    weaviate = WeaviateClient()
    pipeline = IngestionPipeline()

    try:
        # Connect to services
        print("🔌 Connecting to services...")
        await neo4j.connect()
        await weaviate.connect()
        print("   ✅ All services connected")

        # Create organizational graph structure
        await create_organizational_graph(neo4j)

        # Load document data
        print("\n📄 Loading organizational documents...")

        data_dir = Path("examples/wellnessroberts_data")
        documents = [
            {
                "path": data_dir / "daily_priorities.txt",
                "category": "executive_briefing",
                "domain": "organizational_priorities"
            },
            {
                "path": data_dir / "healthcare_industry_context.txt",
                "category": "industry_analysis",
                "domain": "healthcare_market"
            }
        ]

        total_chunks = 0
        for doc in documents:
            print(f"   📁 Processing {doc['path'].name}...")

            result = await pipeline.ingest_documents(
                source_path=str(doc["path"]),
                metadata={
                    "organization": "WellnessRoberts Care",
                    "category": doc["category"],
                    "domain": doc["domain"],
                    "source": "organizational_data"
                }
            )

            chunks_created = result.get('chunks_created', 0)
            total_chunks += chunks_created
            print(f"      ✅ {doc['path'].name}: {chunks_created} chunks")

        # Test hybrid search capabilities
        print(f"\n🔍 Testing hybrid search with {total_chunks} total chunks...")

        # Import here to avoid circular imports
        from src.orchestrator.hybrid_search import HybridSearchOrchestrator
        orchestrator = HybridSearchOrchestrator()

        test_queries = [
            "What are the strategic implications of the PatientCare Suite investment?",
            "How does physician retention relate to patient safety and quality metrics?",
            "What are the compliance requirements for Japan's Health Data Protection Act?"
        ]

        for query in test_queries:
            print(f"\n   Query: {query}")
            try:
                result = await orchestrator.search(
                    query=query,
                    strategy="semantic_first",
                    max_results=3
                )
                print(f"   ✅ Found {len(result.results)} results")
                if result.results:
                    top_result = result.results[0]
                    print(f"   📄 Top result: {top_result.get('title', 'Unknown')} (score: {top_result.get('score', 0):.3f})")
            except Exception as e:
                print(f"   ⚠️  Search test failed: {e}")

        print(f"\n📊 Loading Summary:")
        print(f"   🏢 Organization: WellnessRoberts Care")
        print(f"   🏗️  Graph nodes: Organization + Departments + Products + Priorities + Challenges")
        print(f"   📄 Documents: {len(documents)} organizational documents")
        print(f"   ✂️  Chunks: {total_chunks} searchable chunks")
        print(f"   🔍 Search: Hybrid semantic + graph capabilities ready")

        print(f"\n🎯 Ready for demo with compelling healthcare queries!")
        print(f"   • Strategic decision analysis")
        print(f"   • Cross-departmental impact mapping")
        print(f"   • Regulatory compliance intelligence")
        print(f"   • Competitive market insights")

    except Exception as e:
        logger.error(f"WellnessRoberts data loading failed: {e}")
        print(f"❌ Loading failed: {e}")
    finally:
        await neo4j.close()
        await weaviate.close()

if __name__ == "__main__":
    asyncio.run(main())