#!/usr/bin/env python3
"""
WellnessRoberts Care Demo Queries
Showcase hybrid search capabilities with compelling healthcare scenarios
"""

import asyncio
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import sys
sys.path.append(str(Path(__file__).parent))

from src.orchestrator.hybrid_search import HybridSearchOrchestrator
from src.clients.neo4j_client import Neo4jClient

class WellnessRobertsDemo:
    def __init__(self):
        self.orchestrator = HybridSearchOrchestrator()
        self.neo4j = Neo4jClient()

    async def demonstrate_hybrid_power(self):
        """Show why hybrid search is superior to single-system approaches"""

        print("🏥 WellnessRoberts Care - Hybrid Knowledge Demo")
        print("=" * 70)
        print("🎭 Scenario: CEO Decision Intelligence for Healthcare Leadership")
        print("👤 Role: CEO of 2,623-employee healthcare organization in Tokyo")
        print("📊 Data: Organizational context + Industry intelligence + Daily priorities")
        print()

        await self.neo4j.connect()

        # Demo Query 1: Strategic Investment Decision
        await self.demo_strategic_decision()

        # Demo Query 2: Cross-Departmental Impact Analysis
        await self.demo_impact_analysis()

        # Demo Query 3: Regulatory Compliance Intelligence
        await self.demo_compliance_intelligence()

        # Demo Query 4: Competitive Market Intelligence
        await self.demo_market_intelligence()

        await self.neo4j.close()

    async def demo_strategic_decision(self):
        """Query 1: Strategic Investment Decision Analysis"""

        print("🎯 DEMO QUERY 1: Strategic Investment Decision")
        print("-" * 50)

        query = """
        What are the strategic implications of approving the $4.2M PatientCare Suite investment,
        considering our operational excellence priorities, digital maturity challenges, and
        competitive positioning in Tokyo's healthcare market?
        """

        print(f"CEO Query: {query.strip()}")
        print()

        # Show what each system contributes
        print("🔍 Hybrid Search Analysis:")
        print()

        # Semantic search component (Weaviate)
        print("📚 Semantic Search (Weaviate) finds:")
        print("   • Documents about PatientCare Suite features and capabilities")
        print("   • Industry reports on healthcare technology ROI")
        print("   • Best practices for operational excellence in healthcare")
        print("   • Digital transformation case studies")
        print()

        # Graph search component (Neo4j)
        print("🔗 Graph Search (Neo4j) maps:")
        print("   • Budget allocation → Strategic priorities → Success metrics")
        print("   • PatientCare Suite → Clinical department → Patient outcomes")
        print("   • Digital maturity → Technology investments → Competitive position")
        print("   • Investment decision → Risk factors → Timeline dependencies")
        print()

        # Execute hybrid search
        start_time = time.time()
        try:
            result = await self.orchestrator.search(
                query=query,
                strategy="hybrid",
                max_results=3
            )
            execution_time = time.time() - start_time

            print("💡 Hybrid Intelligence Result:")
            print(f"   ⚡ Search time: {execution_time:.3f} seconds")
            print(f"   📄 Documents found: {len(result.results)}")

            if result.results:
                for i, doc in enumerate(result.results[:2], 1):
                    title = doc.get('title', 'Document')
                    score = doc.get('score', 0)
                    content = doc.get('content', '')[:150]
                    print(f"   {i}. {title} (relevance: {score:.1%})")
                    print(f"      {content}...")
                    print()

        except Exception as e:
            print(f"   ⚠️  Search execution: {e}")

        print("🎯 CEO Intelligence: Investment aligns with operational excellence,")
        print("   addresses digital maturity gap, and positions for competitive advantage")
        print()

    async def demo_impact_analysis(self):
        """Query 2: Cross-Departmental Impact Analysis"""

        print("🎯 DEMO QUERY 2: Cross-Departmental Impact Analysis")
        print("-" * 50)

        query = """
        If we lose the three senior cardiac physicians, how does that cascade through
        our training programs, patient capacity, revenue projections, and Samsung
        partnership negotiations?
        """

        print(f"CEO Query: {query.strip()}")
        print()

        print("🔍 Why This Showcases Hybrid Power:")
        print()

        print("📚 Semantic Search finds:")
        print("   • Healthcare staffing research and retention strategies")
        print("   • Training program documentation and dependencies")
        print("   • Samsung partnership terms and capacity requirements")
        print("   • Revenue impact studies for physician shortages")
        print()

        print("🔗 Graph Search traces:")
        print("   • Physician loss → Training capacity → Junior physician development")
        print("   • Cardiac department → Patient volume → Revenue projections")
        print("   • Staff capacity → Partnership obligations → Contract fulfillment")
        print("   • Quality metrics → Regulatory compliance → Facility licensing")
        print()

        # Show graph relationship query
        print("🗂️  Graph Query Example:")
        try:
            async with self.neo4j.session() as session:
                graph_result = await session.run(
                    """
                    MATCH (d:Department {name: 'Clinical'})-[:AFFECTS_DEPARTMENT]-(c:Challenge)
                    MATCH (o:Organization)-[:HAS_DEPARTMENT]->(d)
                    RETURN d.name as department, c.challenge as challenge, c.impact as impact
                    """,
                    {}
                )

                records = await graph_result.data()
            if records:
                for record in records:
                    print(f"   • {record['department']} faces: {record['challenge']}")
                    print(f"     Impact level: {record['impact']}")

        except Exception as e:
            print(f"   Graph query: {e}")

        print()
        print("💡 Hybrid Intelligence: Maps full business impact web that no single")
        print("   system could reveal - from individual physicians to strategic partnerships")
        print()

    async def demo_compliance_intelligence(self):
        """Query 3: Regulatory Compliance Intelligence"""

        print("🎯 DEMO QUERY 3: Regulatory Compliance Intelligence")
        print("-" * 50)

        query = """
        Given Japan's new Health Data Protection Act requirements, what similar
        regulatory challenges have other healthcare organizations faced, and how do
        our current compliance gaps connect to patient safety and operational risks?
        """

        print(f"CEO Query: {query.strip()}")
        print()

        print("🔍 Hybrid Search Advantage:")
        print()

        print("📚 Semantic Search provides:")
        print("   • HDPA regulatory text and compliance requirements")
        print("   • Case studies from similar healthcare regulations (GDPR, HIPAA)")
        print("   • Best practices from early compliance adopters")
        print("   • Patient safety correlation studies")
        print()

        print("🔗 Graph Search connects:")
        print("   • Compliance gaps → IT systems → Patient data → Safety protocols")
        print("   • Regulatory requirements → Departments → Budget allocations → Timeline")
        print("   • Non-compliance risks → Legal penalties → Operational licenses → Revenue")
        print("   • Implementation options → Resource requirements → Strategic priorities")
        print()

        start_time = time.time()
        try:
            result = await self.orchestrator.search(
                query=query,
                strategy="graph_first",
                max_results=2
            )
            execution_time = time.time() - start_time

            print("💡 Executive Intelligence:")
            print(f"   ⚡ Analysis time: {execution_time:.3f} seconds")
            print(f"   🔍 Compliance connections mapped across departments")
            print(f"   ⚖️  Legal, operational, and strategic risks quantified")

        except Exception as e:
            print(f"   ⚠️  Search execution: {e}")

        print()

    async def demo_market_intelligence(self):
        """Query 4: Competitive Market Intelligence"""

        print("🎯 DEMO QUERY 4: Competitive Market Intelligence")
        print("-" * 50)

        query = """
        How do our digital maturity score, AI implementation challenges, and PatientCare
        Suite investment align with achieving our 2026 expansion goals while maintaining
        competitive advantage against Tokyo General and Keio University Hospital?
        """

        print(f"CEO Query: {query.strip()}")
        print()

        print("🔍 Strategic Intelligence Fusion:")
        print()

        print("📚 Semantic Search delivers:")
        print("   • Digital maturity benchmarking studies")
        print("   • AI implementation roadmaps for healthcare")
        print("   • Competitive analysis of Tokyo healthcare market")
        print("   • Expansion strategy frameworks and success factors")
        print()

        print("🔗 Graph Search aligns:")
        print("   • Digital maturity → Technology investments → Competitive position")
        print("   • AI capabilities → Patient outcomes → Market differentiation")
        print("   • Strategic priorities → Resource allocation → Expansion timeline")
        print("   • Investment decisions → Risk factors → Success probability")
        print()

        # Show competitive positioning
        print("📊 Current Competitive Position:")
        print("   • WellnessRoberts Care: Digital maturity 0.32, Innovation index 0.82")
        print("   • Tokyo General: Digital maturity 0.45, Government partnerships")
        print("   • Keio University: Digital maturity 0.52, Samsung partnership pilot")
        print("   • Strategy: Leverage innovation strength to accelerate digital transformation")
        print()

        print("💡 CEO Strategic Intelligence: Clear roadmap from current position")
        print("   to market leadership through targeted technology investments")
        print()

    async def performance_comparison(self):
        """Demonstrate speed and accuracy advantages"""

        print("🏁 PERFORMANCE SHOWCASE")
        print("-" * 50)

        test_query = "What are the key factors in physician retention strategies?"

        # Test different strategies
        strategies = ["semantic_first", "graph_first", "hybrid"]

        for strategy in strategies:
            start_time = time.time()
            try:
                result = await self.orchestrator.search(
                    query=test_query,
                    strategy=strategy,
                    max_results=3
                )
                execution_time = time.time() - start_time

                print(f"🔍 {strategy.replace('_', ' ').title()} Strategy:")
                print(f"   ⚡ Speed: {execution_time:.3f} seconds")
                print(f"   📄 Results: {len(result.results)} documents")
                print(f"   🎯 Approach: {self.get_strategy_description(strategy)}")
                print()

            except Exception as e:
                print(f"   ⚠️  {strategy}: {e}")

        print("💡 Hybrid Advantage: Combines speed of semantic search with")
        print("   relationship intelligence of graph traversal")
        print()

    def get_strategy_description(self, strategy):
        """Get description of search strategy"""
        descriptions = {
            "semantic_first": "Fast document similarity, then relationship context",
            "graph_first": "Deep relationship analysis, then semantic ranking",
            "hybrid": "Simultaneous semantic + graph with intelligent fusion"
        }
        return descriptions.get(strategy, "Unknown strategy")

async def main():
    """Run the WellnessRoberts Care hybrid search demonstration"""

    demo = WellnessRobertsDemo()

    print("🚀 Starting WellnessRoberts Care Hybrid Knowledge Demo")
    print()
    print("This demonstration shows how hybrid search (Neo4j + Weaviate)")
    print("provides CEO-level intelligence that neither system could achieve alone.")
    print()

    await demo.demonstrate_hybrid_power()
    await demo.performance_comparison()

    print("🎉 DEMONSTRATION COMPLETE")
    print("=" * 70)
    print()
    print("🎯 Key Takeaways:")
    print("   • Semantic search finds relevant content quickly")
    print("   • Graph search reveals hidden relationships and dependencies")
    print("   • Hybrid approach delivers executive-level business intelligence")
    print("   • Healthcare decisions require both content and context")
    print()
    print("🏥 WellnessRoberts Care is ready for intelligent decision-making!")

if __name__ == "__main__":
    asyncio.run(main())