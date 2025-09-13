#!/usr/bin/env python3
"""
Step 3: Add Sample Business Documents to Weaviate
"""

import requests
import json
from datetime import datetime

def step3_add_documents():
    print("📊 STEP 3: Adding Sample Business Documents")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Sample business documents - realistic content for demo
    documents = [
        {
            "title": "Customer Retention Strategies for 2024",
            "content": "Customer retention is critical for sustainable business growth. Key strategies include personalized communication, loyalty programs, proactive customer support, and regular feedback collection. Companies with strong retention programs see 25% higher revenue growth.",
            "category": "Business Strategy",
            "created_date": "2024-01-15T10:30:00Z"
        },
        {
            "title": "Digital Marketing ROI Measurement", 
            "content": "Measuring digital marketing return on investment requires tracking customer acquisition costs, lifetime value, conversion rates, and attribution across multiple channels. Analytics tools help optimize campaign performance and budget allocation.",
            "category": "Marketing",
            "created_date": "2024-02-01T14:15:00Z"
        },
        {
            "title": "AI Implementation Framework for Enterprises",
            "content": "Successful AI implementation requires clear business objectives, quality data preparation, stakeholder alignment, and phased rollout. Organizations should start with pilot projects, establish governance frameworks, and scale gradually based on results.",
            "category": "Technology",
            "created_date": "2024-02-15T09:45:00Z"
        },
        {
            "title": "Financial Planning and Budget Optimization",
            "content": "Effective financial planning includes comprehensive budgeting, accurate forecasting, scenario analysis, and regular performance reviews. Automation tools can streamline processes, improve accuracy, and provide real-time insights for decision making.",
            "category": "Finance",
            "created_date": "2024-01-30T11:20:00Z"
        },
        {
            "title": "Supply Chain Risk Management Solutions",
            "content": "Supply chain optimization focuses on reducing costs, improving efficiency, and increasing resilience. Key areas include inventory management, supplier relationship management, logistics coordination, and risk mitigation strategies.",
            "category": "Operations",
            "created_date": "2024-02-10T16:00:00Z"
        }
    ]
    
    try:
        print(f"📚 Preparing to add {len(documents)} documents:")
        for i, doc in enumerate(documents, 1):
            print(f"   {i}. {doc['title']} ({doc['category']})")
        
        added_count = 0
        failed_count = 0
        
        print(f"\n📝 Adding documents one by one...")
        
        for i, doc in enumerate(documents, 1):
            print(f"\n   📄 Document {i}: {doc['title']}")
            print(f"      Category: {doc['category']}")
            print(f"      Content: {doc['content'][:80]}...")
            
            # Create the object in Weaviate
            weaviate_object = {
                "class": "BusinessDocument",
                "properties": doc
            }
            
            response = requests.post(f"{base_url}/v1/objects", json=weaviate_object)
            
            if response.status_code in [200, 201]:
                result = response.json()
                document_id = result.get("id", "unknown")
                print(f"      ✅ Added successfully! ID: {document_id[:8]}...")
                added_count += 1
            else:
                print(f"      ❌ Failed to add: {response.status_code}")
                print(f"         Error: {response.text}")
                failed_count += 1
        
        print(f"\n📊 RESULTS:")
        print(f"   ✅ Successfully added: {added_count}")
        print(f"   ❌ Failed to add: {failed_count}")
        
        if added_count > 0:
            # Verify documents were added
            print(f"\n🔍 Verifying documents in database...")
            
            graphql_query = {
                "query": """
                {
                    Get {
                        BusinessDocument {
                            title
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
                print(f"   📋 Found {len(docs)} documents in database:")
                for doc in docs:
                    print(f"      • {doc['title']} ({doc['category']})")
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ DOCUMENT ADDITION FAILED!")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    success = step3_add_documents()
    if success:
        print("\n🎉 Step 3 Complete! Sample documents are loaded.")
        print("📝 Next: Run step4_search.py to test searching")
    else:
        print("\n🛠️  Fix the data loading issue before proceeding.")