#!/usr/bin/env python3
"""
Simple Weaviate connectivity and basic functionality test
"""

import weaviate
import time
from weaviate.classes.config import Configure, Property, DataType

def test_weaviate():
    print("🚀 Testing Weaviate Connection")
    print("=" * 40)
    
    try:
        # Connect to Weaviate
        client = weaviate.connect_to_local(skip_init_checks=True)
        print("✅ Connected to Weaviate successfully!")
        
        # Test readiness
        if client.is_ready():
            print("✅ Weaviate is ready")
        else:
            print("⚠️ Weaviate not ready yet")
            
        # Create a simple test collection
        collection_name = "TestDocs"
        
        # Delete if exists
        if client.collections.exists(collection_name):
            client.collections.delete(collection_name)
            print(f"🗑️ Deleted existing {collection_name} collection")
        
        # Create new collection
        collection = client.collections.create(
            name=collection_name,
            properties=[
                Property(name="title", data_type=DataType.TEXT),
                Property(name="content", data_type=DataType.TEXT),
            ],
            vectorizer_config=Configure.Vectorizer.none()  # No automatic vectorization
        )
        print(f"✅ Created {collection_name} collection")
        
        # Add test documents
        test_docs = [
            {
                "title": "Customer Retention",
                "content": "Strategies for keeping customers happy and loyal to your business."
            },
            {
                "title": "Digital Marketing",
                "content": "Modern approaches to online marketing and customer engagement."
            },
            {
                "title": "Data Analytics",
                "content": "Using data to make informed business decisions and predictions."
            }
        ]
        
        # Insert documents
        uuids = collection.data.insert_many(test_docs)
        print(f"✅ Inserted {len(uuids)} test documents")
        
        # Test basic retrieval
        results = collection.query.fetch_objects(limit=5)
        print(f"✅ Retrieved {len(results.objects)} documents")
        
        # Display results
        print("\n📋 Test Documents:")
        for i, obj in enumerate(results.objects, 1):
            print(f"  {i}. {obj.properties['title']}")
            print(f"     {obj.properties['content'][:50]}...")
        
        # Test keyword search (if available)
        try:
            keyword_results = collection.query.bm25(
                query="customer",
                limit=3
            )
            print(f"\n🔍 Keyword search for 'customer': {len(keyword_results.objects)} results")
            for obj in keyword_results.objects:
                print(f"  - {obj.properties['title']}")
        except Exception as e:
            print(f"⚠️ Keyword search not available: {e}")
        
        # Cleanup
        client.collections.delete(collection_name)
        print(f"🗑️ Cleaned up {collection_name} collection")
        
        client.close()
        print("\n🎉 Weaviate test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_weaviate()