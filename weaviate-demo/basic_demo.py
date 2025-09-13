#!/usr/bin/env python3
"""
Basic Weaviate Demo - No API Keys Required
Demonstrates core Weaviate functionality using REST API only
"""

import requests
import json
import time

def test_weaviate_rest():
    """Test Weaviate using REST API - no gRPC, no API keys needed"""
    
    print("🚀 Weaviate Basic Demo - REST API")
    print("=" * 40)
    
    base_url = "http://localhost:8080"
    
    try:
        # 1. Test connection
        response = requests.get(f"{base_url}/v1/meta")
        if response.status_code == 200:
            meta = response.json()
            print(f"✅ Connected to Weaviate {meta.get('version', 'unknown')}")
        else:
            print(f"❌ Connection failed: {response.status_code}")
            return False
        
        # 2. Create a simple schema
        schema = {
            "class": "BusinessDocument",
            "description": "Business documents for semantic search demo",
            "properties": [
                {
                    "name": "title",
                    "dataType": ["text"],
                    "description": "Document title"
                },
                {
                    "name": "content", 
                    "dataType": ["text"],
                    "description": "Document content"
                },
                {
                    "name": "category",
                    "dataType": ["text"],
                    "description": "Business category"
                }
            ],
            "vectorizer": "none"  # No automatic vectorization
        }
        
        # Delete existing schema if it exists
        requests.delete(f"{base_url}/v1/schema/BusinessDocument")
        
        # Create new schema
        response = requests.post(f"{base_url}/v1/schema", json=schema)
        if response.status_code in [200, 422]:  # 422 means already exists
            print("✅ Created BusinessDocument schema")
        else:
            print(f"⚠️ Schema creation: {response.status_code} - {response.text}")
        
        # 3. Add sample documents
        documents = [
            {
                "title": "Customer Retention Strategies",
                "content": "Effective customer retention requires understanding customer needs, providing excellent service, and building long-term relationships. Key strategies include loyalty programs, personalized communication, and proactive support.",
                "category": "Business Strategy"
            },
            {
                "title": "Digital Marketing ROI Analysis", 
                "content": "Measuring digital marketing return on investment involves tracking customer acquisition costs, lifetime value, conversion rates, and attribution across multiple channels. Analytics tools help optimize campaign performance.",
                "category": "Marketing"
            },
            {
                "title": "AI Implementation Framework",
                "content": "Successful AI implementation requires clear business objectives, quality data preparation, stakeholder alignment, and phased rollout. Organizations should start with pilot projects and scale gradually.",
                "category": "Technology"
            },
            {
                "title": "Financial Planning Best Practices",
                "content": "Effective financial planning includes budgeting, forecasting, scenario analysis, and regular performance reviews. Automation tools can streamline processes and improve accuracy.",
                "category": "Finance"
            },
            {
                "title": "Supply Chain Optimization",
                "content": "Supply chain optimization focuses on reducing costs, improving efficiency, and increasing resilience. Key areas include inventory management, supplier relationships, and logistics coordination.",
                "category": "Operations"
            }
        ]
        
        added_count = 0
        for doc in documents:
            response = requests.post(f"{base_url}/v1/objects", json={
                "class": "BusinessDocument",
                "properties": doc
            })
            if response.status_code in [200, 201]:
                added_count += 1
        
        print(f"✅ Added {added_count}/{len(documents)} documents")
        
        # 4. Test GraphQL query (keyword search)
        graphql_query = {
            "query": """
            {
                Get {
                    BusinessDocument(limit: 3, where: {
                        path: ["content"],
                        operator: Like,
                        valueText: "*customer*"
                    }) {
                        title
                        content
                        category
                    }
                }
            }
            """
        }
        
        response = requests.post(f"{base_url}/v1/graphql", json=graphql_query)
        if response.status_code == 200:
            results = response.json()
            docs = results.get("data", {}).get("Get", {}).get("BusinessDocument", [])
            print(f"\n🔍 Keyword search for 'customer': {len(docs)} results")
            for i, doc in enumerate(docs, 1):
                print(f"  {i}. {doc['title']}")
                print(f"     Category: {doc['category']}")
        
        # 5. Test aggregation
        agg_query = {
            "query": """
            {
                Aggregate {
                    BusinessDocument {
                        meta {
                            count
                        }
                        category {
                            count
                            topOccurrences {
                                value
                                occurs
                            }
                        }
                    }
                }
            }
            """
        }
        
        response = requests.post(f"{base_url}/v1/graphql", json=agg_query)
        if response.status_code == 200:
            results = response.json()
            agg_data = results.get("data", {}).get("Aggregate", {}).get("BusinessDocument", [])
            if agg_data:
                total_count = agg_data[0].get("meta", {}).get("count", 0)
                categories = agg_data[0].get("category", {}).get("topOccurrences", [])
                print(f"\n📊 Database Statistics:")
                print(f"  Total documents: {total_count}")
                print(f"  Categories:")
                for cat in categories:
                    print(f"    - {cat['value']}: {cat['occurs']} docs")
        
        # 6. Show available classes
        response = requests.get(f"{base_url}/v1/schema")
        if response.status_code == 200:
            schema_data = response.json()
            classes = [cls["class"] for cls in schema_data.get("classes", [])]
            print(f"\n📋 Available Classes: {', '.join(classes)}")
        
        # 7. Cleanup
        requests.delete(f"{base_url}/v1/schema/BusinessDocument")
        print("🗑️ Cleaned up test data")
        
        print("\n🎉 Weaviate basic demo completed successfully!")
        print("\n💡 Key Capabilities Demonstrated:")
        print("  ✅ Schema creation and management")
        print("  ✅ Document insertion and storage") 
        print("  ✅ GraphQL keyword search")
        print("  ✅ Data aggregation and statistics")
        print("  ✅ REST API operations")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Weaviate at http://localhost:8080")
        print("💡 Make sure Weaviate is running: docker-compose up -d weaviate")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

if __name__ == "__main__":
    test_weaviate_rest()