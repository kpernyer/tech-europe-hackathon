#!/usr/bin/env python3
"""
Setup OpenAI-enabled Schema for Weaviate Demo
"""

import requests
import json

def setup_openai_schema():
    print("🔧 SETTING UP OPENAI-ENABLED SCHEMA")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    try:
        # Delete existing schema if it exists
        print("🗑️  Removing existing schema...")
        delete_response = requests.delete(f"{base_url}/v1/schema/BusinessDocument")
        if delete_response.status_code == 200:
            print("   ✅ Deleted existing BusinessDocument schema")
        else:
            print("   ℹ️  No existing schema to delete")
        
        # Create new schema with OpenAI vectorization
        print("\n🏗️  Creating OpenAI-enabled schema...")
        schema = {
            "class": "BusinessDocument",
            "description": "Business documents for semantic search with OpenAI embeddings",
            "vectorizer": "text2vec-openai",
            "moduleConfig": {
                "text2vec-openai": {
                    "model": "text-embedding-3-small",
                    "modelVersion": "text-embedding-3-small",
                    "type": "text"
                },
                "generative-openai": {
                    "model": "gpt-3.5-turbo"
                }
            },
            "properties": [
                {
                    "name": "title",
                    "dataType": ["text"],
                    "description": "Document title",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": True
                        }
                    }
                },
                {
                    "name": "content", 
                    "dataType": ["text"],
                    "description": "Main document content",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": False
                        }
                    }
                },
                {
                    "name": "category",
                    "dataType": ["text"],
                    "description": "Business category",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": False,
                            "vectorizePropertyName": True
                        }
                    }
                },
                {
                    "name": "created_date",
                    "dataType": ["date"],
                    "description": "When the document was created",
                    "moduleConfig": {
                        "text2vec-openai": {
                            "skip": True
                        }
                    }
                }
            ]
        }
        
        response = requests.post(f"{base_url}/v1/schema", json=schema)
        
        if response.status_code == 200:
            print("✅ OPENAI SCHEMA CREATED SUCCESSFULLY!")
            print("   🤖 Vectorizer: text2vec-openai")
            print("   📝 Embedding Model: text-embedding-3-small")
            print("   🧠 Generative Model: gpt-3.5-turbo")
            
            # Verify schema creation
            verify_response = requests.get(f"{base_url}/v1/schema")
            if verify_response.status_code == 200:
                schema_data = verify_response.json()
                classes = [cls["class"] for cls in schema_data.get("classes", [])]
                print(f"   📊 Available Classes: {', '.join(classes)}")
            
            print("\n🎯 READY FOR SEMANTIC SEARCH!")
            print("   • Documents will be automatically vectorized with OpenAI embeddings")
            print("   • Semantic search will use true vector similarity")
            print("   • Generative AI capabilities enabled")
            
            return True
            
        else:
            print(f"❌ SCHEMA CREATION FAILED!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ SCHEMA SETUP FAILED!")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    success = setup_openai_schema()
    if success:
        print("\n🎉 OpenAI Integration Complete!")
        print("📝 Next: Run your demo and inject documents - they will be automatically vectorized!")
    else:
        print("\n🛠️  Fix the setup issue before proceeding.")