#!/usr/bin/env python3
"""
Step 2: Create Document Schema in Weaviate
"""

import requests
import json

def step2_create_schema():
    print("🏗️  STEP 2: Creating Document Schema")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    # Define what kind of documents we want to store
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
                "description": "Main document content"
            },
            {
                "name": "category",
                "dataType": ["text"],
                "description": "Business category (Strategy, Marketing, etc.)"
            },
            {
                "name": "created_date",
                "dataType": ["date"],
                "description": "When the document was created"
            }
        ],
        "vectorizer": "none"  # We're not using automatic embeddings yet
    }
    
    try:
        print("📋 Schema Definition:")
        print(f"   📝 Class Name: {schema['class']}")
        print(f"   📄 Description: {schema['description']}")
        print(f"   🏷️  Properties:")
        for prop in schema['properties']:
            print(f"      • {prop['name']} ({prop['dataType'][0]}): {prop['description']}")
        print(f"   🤖 Vectorizer: {schema['vectorizer']} (no automatic embeddings)")
        
        # Delete existing schema if it exists (for clean demo)
        print(f"\n🗑️  Checking for existing schema...")
        delete_response = requests.delete(f"{base_url}/v1/schema/BusinessDocument")
        if delete_response.status_code == 200:
            print("   Deleted existing BusinessDocument schema")
        
        # Create new schema
        print(f"\n🏗️  Creating new schema...")
        response = requests.post(f"{base_url}/v1/schema", json=schema)
        
        if response.status_code == 200:
            print("✅ SCHEMA CREATED SUCCESSFULLY!")
            
            # Verify it was created
            verify_response = requests.get(f"{base_url}/v1/schema")
            if verify_response.status_code == 200:
                schema_data = verify_response.json()
                classes = [cls["class"] for cls in schema_data.get("classes", [])]
                print(f"📊 Available Classes: {', '.join(classes)}")
            
            return True
            
        else:
            print(f"❌ SCHEMA CREATION FAILED!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ SCHEMA CREATION FAILED!")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    success = step2_create_schema()
    if success:
        print("\n🎉 Step 2 Complete! Document schema is ready.")
        print("📝 Next: Run step3_add_data.py to add sample documents")
    else:
        print("\n🛠️  Fix the schema issue before proceeding.")