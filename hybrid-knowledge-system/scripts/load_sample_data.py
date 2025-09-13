#!/usr/bin/env python3
"""
Load Sample Data Script: Populates the system with demo business data
"""

import asyncio
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.ingestion.pipeline import IngestionPipeline
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Sample business knowledge base
SAMPLE_DOCUMENTS = {
    "business_strategy": [
        {
            "title": "Customer Retention Best Practices",
            "content": """
            Customer retention is the cornerstone of sustainable business growth. Research consistently shows that acquiring new customers costs 5-25 times more than retaining existing ones.

            Key Retention Strategies:
            
            1. Personalized Customer Experience
               - Use customer data to personalize interactions
               - Implement dynamic content based on preferences
               - Create targeted communication campaigns
            
            2. Proactive Customer Support
               - Monitor customer health scores
               - Reach out before issues escalate
               - Provide multi-channel support options
            
            3. Value-Added Services
               - Regular feature updates and improvements
               - Educational content and training
               - Exclusive access to beta features
            
            4. Loyalty Programs
               - Reward long-term customers
               - Create tiered benefit structures
               - Gamify the customer experience
            
            Measuring Success:
            - Customer Lifetime Value (CLV)
            - Net Promoter Score (NPS)
            - Churn rate and retention metrics
            - Customer satisfaction scores
            
            Companies with strong retention programs see 2.5x revenue growth and 40% higher customer satisfaction compared to competitors.
            """,
            "domain": "strategy",
            "type": "best_practices"
        },
        {
            "title": "Digital Transformation Roadmap",
            "content": """
            Digital transformation is essential for modern business competitiveness. A structured approach ensures successful implementation and measurable ROI.

            Phase 1: Assessment and Planning (Months 1-2)
            - Current state analysis
            - Technology gap assessment
            - Stakeholder alignment
            - Resource allocation planning
            
            Phase 2: Foundation Building (Months 3-6)
            - Cloud infrastructure setup
            - Data governance framework
            - Security and compliance protocols
            - Change management program
            
            Phase 3: Implementation (Months 7-18)
            - Core system migrations
            - Process automation deployment
            - AI/ML platform integration
            - Employee training programs
            
            Phase 4: Optimization (Months 19-24)
            - Performance monitoring
            - Continuous improvement cycles
            - Advanced analytics implementation
            - Innovation pipeline development
            
            Success Metrics:
            - Operational efficiency gains: 25-40%
            - Customer experience improvements: 30-50%
            - Revenue impact: 15-25% increase
            - Time-to-market reduction: 40-60%
            
            Critical success factors include leadership commitment, employee engagement, and iterative approach to implementation.
            """,
            "domain": "strategy",
            "type": "roadmap"
        }
    ],
    
    "market_intelligence": [
        {
            "title": "Q4 2024 Market Trends Analysis",
            "content": """
            The Q4 2024 market landscape reveals significant shifts in consumer behavior and business priorities.

            Consumer Behavior Trends:
            
            1. Digital-First Expectations (85% of consumers)
               - Mobile-optimized experiences mandatory
               - Real-time customer service expectations
               - Omnichannel consistency requirements
            
            2. Sustainability Focus (72% factor in decisions)
               - Eco-friendly product preferences
               - Corporate social responsibility importance
               - Circular economy adoption
            
            3. Value-Conscious Purchasing (78% price-sensitive)
               - Quality-price balance optimization
               - Subscription model preferences
               - Bulk purchasing trends
            
            Technology Adoption Patterns:
            - AI integration: 65% of businesses planning implementation
            - Cloud migration: 80% partial or complete adoption
            - Automation tools: 45% increase in deployment
            
            Competitive Landscape:
            - Market consolidation in key sectors
            - Startup disruption in traditional industries
            - Platform-based business models growing
            
            Investment Priorities:
            1. Customer experience technology (40%)
            2. Data analytics and AI (35%)
            3. Process automation (30%)
            4. Cybersecurity infrastructure (25%)
            
            Risk factors include economic uncertainty, regulatory changes, and talent acquisition challenges.
            """,
            "domain": "market_research",
            "type": "trend_analysis"
        }
    ],
    
    "financial_analysis": [
        {
            "title": "Technology ROI Analysis 2024",
            "content": """
            Technology investments continue to deliver strong returns when properly executed and measured.

            Investment Categories and ROI:
            
            1. Artificial Intelligence/Machine Learning
               - Average ROI: 300% over 24 months
               - Payback period: 8-12 months
               - Key applications: Customer service, predictive analytics, process optimization
               - Success rate: 70% of implementations
            
            2. Process Automation
               - Average ROI: 250% over 18 months
               - Payback period: 6-9 months
               - Key applications: Data processing, customer onboarding, compliance
               - Success rate: 85% of implementations
            
            3. Cloud Infrastructure
               - Average ROI: 200% over 36 months
               - Payback period: 12-18 months
               - Key benefits: Scalability, disaster recovery, collaboration
               - Success rate: 90% of migrations
            
            4. Customer Analytics Platforms
               - Average ROI: 180% over 12 months
               - Payback period: 4-8 months
               - Key applications: Personalization, retention, acquisition
               - Success rate: 75% of implementations
            
            Critical Success Factors:
            - Clear business objectives and KPIs
            - Executive sponsorship and change management
            - Employee training and adoption programs
            - Iterative implementation approach
            - Regular performance monitoring
            
            Risk Mitigation Strategies:
            - Pilot programs before full deployment
            - Vendor due diligence and references
            - Contingency planning and backup systems
            - Compliance and security assessment
            
            Budget allocation recommendations: 60% implementation, 25% training, 15% contingency.
            """,
            "domain": "finance",
            "type": "roi_analysis"
        }
    ]
}

STRUCTURED_DATA = [
    # KPI Metrics
    {
        "name": "Customer Satisfaction Score",
        "type": "KPI",
        "category": "Customer Experience",
        "current_value": 8.7,
        "target_value": 9.0,
        "unit": "1-10 scale",
        "frequency": "Monthly",
        "description": "Average customer satisfaction rating across all touchpoints",
        "owner": "Customer Success Team",
        "related_initiatives": ["retention_program", "service_excellence", "omnichannel_experience"]
    },
    {
        "name": "Net Promoter Score",
        "type": "KPI",
        "category": "Customer Loyalty",
        "current_value": 65,
        "target_value": 75,
        "unit": "-100 to +100",
        "frequency": "Quarterly",
        "description": "Customer loyalty and recommendation likelihood metric",
        "owner": "Marketing Team",
        "related_initiatives": ["customer_advocacy", "product_improvement", "brand_experience"]
    },
    {
        "name": "Customer Lifetime Value",
        "type": "KPI",
        "category": "Revenue",
        "current_value": 2450.00,
        "target_value": 2800.00,
        "unit": "USD",
        "frequency": "Monthly",
        "description": "Average revenue generated per customer over their lifecycle",
        "owner": "Revenue Operations",
        "related_initiatives": ["retention_program", "upselling", "customer_success"]
    },
    
    # Strategic Initiatives
    {
        "name": "Digital Transformation Initiative",
        "type": "Strategic Project",
        "category": "Technology",
        "status": "In Progress",
        "completion_percentage": 65,
        "budget": 2500000,
        "budget_used": 1625000,
        "start_date": "2024-01-15",
        "target_completion": "2025-06-30",
        "description": "Company-wide digital transformation focusing on customer experience and operational efficiency",
        "stakeholders": ["IT Department", "Operations", "Customer Success", "Finance"],
        "key_milestones": ["Infrastructure Setup", "Process Automation", "AI Integration", "Training Completion"]
    },
    {
        "name": "Customer Experience Enhancement Program",
        "type": "Strategic Project", 
        "category": "Customer Experience",
        "status": "Planning",
        "completion_percentage": 15,
        "budget": 1200000,
        "budget_used": 180000,
        "start_date": "2024-11-01",
        "target_completion": "2025-12-31",
        "description": "Comprehensive program to improve customer touchpoints and satisfaction",
        "stakeholders": ["Customer Success", "Marketing", "Product", "Sales"],
        "key_milestones": ["Journey Mapping", "Touchpoint Optimization", "Feedback System", "Measurement Framework"]
    },
    
    # Market Intelligence
    {
        "name": "Enterprise Software Market Analysis",
        "type": "Market Research",
        "category": "Competitive Intelligence",
        "market_size": 45000000000,
        "growth_rate": 12.5,
        "our_market_share": 3.2,
        "position": 3,
        "description": "Comprehensive analysis of the enterprise software market position",
        "key_competitors": ["Microsoft", "Salesforce", "Oracle", "SAP", "Adobe"],
        "market_trends": ["AI Integration", "Cloud-First", "Low-Code Platforms", "Industry Specialization"],
        "opportunities": ["SMB Market", "Vertical Solutions", "AI-Powered Features", "Partner Ecosystem"]
    },
    {
        "name": "Customer Segment Analysis",
        "type": "Customer Research",
        "category": "Market Intelligence",
        "total_customers": 15420,
        "segments": {
            "Enterprise": {"count": 2840, "revenue_share": 65, "satisfaction": 8.9},
            "Mid-Market": {"count": 6180, "revenue_share": 28, "satisfaction": 8.5},
            "SMB": {"count": 6400, "revenue_share": 7, "satisfaction": 8.2}
        },
        "description": "Customer segmentation analysis with satisfaction and revenue metrics",
        "growth_opportunities": ["Enterprise expansion", "SMB automation", "Mid-market retention"]
    }
]

async def main():
    """Load comprehensive sample data into the hybrid system"""
    
    print("📊 Loading Sample Business Data")
    print("=" * 40)
    
    # Initialize ingestion pipeline
    pipeline = IngestionPipeline()
    
    try:
        # Initialize system
        print("🔌 Initializing system...")
        await pipeline.initialize()
        
        # Create samples directory
        samples_dir = Path(__file__).parent.parent / "examples" / "sample_data"
        samples_dir.mkdir(exist_ok=True, parents=True)
        
        # Load document data
        print("\n📄 Loading business documents...")
        document_count = 0
        
        for domain, documents in SAMPLE_DOCUMENTS.items():
            print(f"   📁 Processing {domain} documents...")
            
            for doc in documents:
                # Create temporary file
                filename = f"{doc['title'].replace(' ', '_').lower()}.txt"
                temp_file = samples_dir / filename
                temp_file.write_text(doc['content'])
                
                # Ingest document
                stats = await pipeline.ingest_documents(
                    source_path=temp_file,
                    domain=domain,
                    metadata={
                        'document_type': doc['type'],
                        'sample_data': True,
                        'category': domain
                    }
                )
                
                document_count += stats.documents_processed
                print(f"      ✅ {doc['title']}: {stats.chunks_created} chunks")
        
        # Load structured data
        print(f"\n📊 Loading structured business data...")
        
        stats = await pipeline.ingest_structured_data(
            data=STRUCTURED_DATA,
            source_name="business_intelligence",
            extract_relationships=True,
            domain="business_metrics"
        )
        
        print(f"   ✅ Processed {stats.documents_processed} structured records")
        print(f"   🔗 Created {stats.relationships_created} relationships")
        print(f"   🏷️  Extracted {stats.entities_extracted} entities")
        
        # Display final statistics
        final_stats = await pipeline.get_ingestion_stats()
        print(f"\n📈 Final Statistics:")
        print(f"   📄 Documents processed: {document_count}")
        print(f"   ✂️  Total chunks created: {final_stats['processing_stats']['chunks_created']}")
        print(f"   🧠 Embeddings generated: {final_stats['processing_stats']['embeddings_generated']}")
        print(f"   🗃️  Neo4j nodes: {final_stats['neo4j_stats'].get('nodeCount', 0)}")
        print(f"   🔍 Weaviate documents: {final_stats['weaviate_document_count']}")
        
        if final_stats['processing_stats']['errors']:
            print(f"   ⚠️  Errors: {len(final_stats['processing_stats']['errors'])}")
        
        print(f"\n🎉 Sample data loading completed successfully!")
        print(f"🔍 System ready for hybrid search queries!")
        
        # Save sample queries for testing
        sample_queries = [
            "How can we improve customer retention rates?",
            "What are the key market trends affecting our business?", 
            "ROI analysis for our technology investments",
            "Customer satisfaction metrics and improvement opportunities",
            "Digital transformation best practices and roadmap",
            "Competitive analysis in the enterprise software market",
            "Budget allocation for customer experience improvements"
        ]
        
        queries_file = samples_dir / "sample_queries.json"
        queries_file.write_text(json.dumps(sample_queries, indent=2))
        print(f"💡 Sample queries saved to: {queries_file}")
        
    except Exception as e:
        logger.error(f"Sample data loading failed: {e}")
        print(f"❌ Loading failed: {e}")
        sys.exit(1)
    
    finally:
        # Cleanup
        await pipeline.cleanup()

if __name__ == "__main__":
    asyncio.run(main())