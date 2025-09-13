#!/usr/bin/env python3
"""
Simple system initialization
"""
import os
import asyncio
import requests
import json
from dotenv import load_dotenv
import neo4j
import weaviate

load_dotenv()

def create_neo4j_indexes():
    print("Creating Neo4j indexes...")
    driver = neo4j.GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
    )

    try:
        with driver.session() as session:
            # Create vector index for documents
            try:
                session.run("""
                CREATE VECTOR INDEX document_embeddings IF NOT EXISTS
                FOR (d:Document)
                ON (d.embedding)
                OPTIONS {
                    indexConfig: {
                        `vector.dimensions`: 384,
                        `vector.similarity_function`: 'cosine'
                    }
                }
                """)
                print("✅ Document vector index created")
            except Exception as e:
                print(f"⚠️ Document vector index: {e}")

            # Create fulltext index
            try:
                session.run("""
                CREATE FULLTEXT INDEX document_fulltext IF NOT EXISTS
                FOR (d:Document)
                ON EACH [d.title, d.content, d.description]
                """)
                print("✅ Document fulltext index created")
            except Exception as e:
                print(f"⚠️ Document fulltext index: {e}")

        print("✅ Neo4j indexes initialized")
        return True

    except Exception as e:
        print(f"❌ Neo4j initialization failed: {e}")
        return False
    finally:
        driver.close()

def create_weaviate_schema():
    print("Creating Weaviate schema...")
    try:
        # Use HTTP API directly
        schema_url = "http://localhost:8081/v1/schema"

        # Check if schema already exists
        response = requests.get(schema_url)
        if response.status_code == 200:
            existing_classes = [cls['class'] for cls in response.json()['classes']]
            if 'Document' in existing_classes:
                print("✅ Document schema already exists")
                return True

        # Create Document schema
        document_schema = {
            "class": "Document",
            "description": "Document class for hybrid knowledge system",
            "vectorizer": "none",  # We'll provide our own vectors
            "properties": [
                {
                    "name": "title",
                    "dataType": ["text"],
                    "description": "Title of the document"
                },
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "Content of the document"
                },
                {
                    "name": "source",
                    "dataType": ["text"],
                    "description": "Source of the document"
                },
                {
                    "name": "doc_id",
                    "dataType": ["text"],
                    "description": "Unique document identifier"
                },
                {
                    "name": "chunk_index",
                    "dataType": ["int"],
                    "description": "Chunk index within the document"
                }
            ],
            "vectorIndexConfig": {
                "distance": "cosine"
            }
        }

        response = requests.post(schema_url, json=document_schema)
        if response.status_code in [200, 422]:  # 422 means already exists
            print("✅ Weaviate Document schema created")
            return True
        else:
            print(f"❌ Weaviate schema creation failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Weaviate schema creation failed: {e}")
        return False

def test_embedding_service():
    print("Testing embedding service...")
    try:
        # Simple sentence transformer test
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        test_embedding = model.encode("This is a test sentence")
        print(f"✅ Embedding service working - dimensions: {len(test_embedding)}")
        return True, len(test_embedding)
    except Exception as e:
        print(f"❌ Embedding service failed: {e}")
        return False, 0

async def main():
    print("🏗️  Simple Hybrid Knowledge System Setup")
    print("=" * 50)

    # Test embedding service first
    embedding_ok, dimensions = test_embedding_service()
    if not embedding_ok:
        print("❌ Cannot continue without embedding service")
        return

    # Initialize Neo4j
    neo4j_ok = create_neo4j_indexes()

    # Initialize Weaviate
    weaviate_ok = create_weaviate_schema()

    print(f"\n📊 Initialization Summary:")
    print(f"Embedding Service: {'✅' if embedding_ok else '❌'} (dimensions: {dimensions})")
    print(f"Neo4j: {'✅' if neo4j_ok else '❌'}")
    print(f"Weaviate: {'✅' if weaviate_ok else '❌'}")

    if all([embedding_ok, neo4j_ok, weaviate_ok]):
        print(f"\n🎉 System initialization completed successfully!")
        print(f"🚀 Ready for hybrid knowledge processing!")
    else:
        print(f"\n⚠️  Some components failed to initialize")

if __name__ == "__main__":
    asyncio.run(main())