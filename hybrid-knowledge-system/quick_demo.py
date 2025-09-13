#!/usr/bin/env python3
"""
Quick Hybrid Knowledge System Demo
"""
import os
import json
import asyncio
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import neo4j
import requests

load_dotenv()

def add_sample_documents():
    """Add sample documents to both Neo4j and Weaviate"""
    print("Adding sample documents...")

    # Sample documents
    documents = [
        {
            "doc_id": "doc_1",
            "title": "Customer Retention Strategies",
            "content": "Customer retention is crucial for SaaS businesses. Key strategies include onboarding optimization, proactive customer success, and churn prediction analytics.",
            "category": "Business Strategy",
            "source": "internal_docs"
        },
        {
            "doc_id": "doc_2",
            "title": "AI Implementation Best Practices",
            "content": "Enterprise AI implementation requires strategic planning, stakeholder alignment, and phased rollouts. Start with pilot projects and establish governance frameworks.",
            "category": "Technology Strategy",
            "source": "tech_docs"
        },
        {
            "doc_id": "doc_3",
            "title": "Digital Marketing ROI Analysis",
            "content": "Measuring digital marketing ROI requires comprehensive tracking across channels. Key metrics include customer acquisition cost and lifetime value.",
            "category": "Marketing Analytics",
            "source": "marketing_docs"
        }
    ]

    # Initialize embedding model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    # Add to Neo4j
    driver = neo4j.GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
    )

    try:
        with driver.session() as session:
            for doc in documents:
                # Create embedding
                embedding = model.encode(doc['content']).tolist()

                # Insert document with embedding
                session.run("""
                MERGE (d:Document {doc_id: $doc_id})
                SET d.title = $title,
                    d.content = $content,
                    d.category = $category,
                    d.source = $source,
                    d.embedding = $embedding
                """, {
                    'doc_id': doc['doc_id'],
                    'title': doc['title'],
                    'content': doc['content'],
                    'category': doc['category'],
                    'source': doc['source'],
                    'embedding': embedding
                })

        print("✅ Documents added to Neo4j")
    finally:
        driver.close()

    # Add to Weaviate
    for doc in documents:
        # Prepare document for Weaviate (without manual embedding - let Weaviate handle it)
        weaviate_doc = {
            "title": doc['title'],
            "content": doc['content'],
            "doc_id": doc['doc_id'],
            "source": doc['source'],
            "chunk_index": 0
        }

        # Insert via HTTP API
        response = requests.post(
            "http://localhost:8081/v1/objects",
            json={
                "class": "Document",
                "properties": weaviate_doc,
                "vector": model.encode(doc['content']).tolist()  # Provide vector manually since we have none vectorizer
            }
        )

        if response.status_code in [200, 201]:
            print(f"✅ Added '{doc['title']}' to Weaviate")
        else:
            print(f"❌ Failed to add '{doc['title']}' to Weaviate: {response.text}")

def search_neo4j(query: str):
    """Search Neo4j using vector similarity"""
    print(f"\n🔍 Neo4j Vector Search: '{query}'")

    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    query_embedding = model.encode(query).tolist()

    driver = neo4j.GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
    )

    try:
        with driver.session() as session:
            result = session.run("""
            CALL db.index.vector.queryNodes('document_embeddings', 3, $query_embedding)
            YIELD node, score
            RETURN node.title as title, node.content as content, node.category as category, score
            ORDER BY score DESC
            """, {'query_embedding': query_embedding})

            for record in result:
                print(f"  📄 {record['title']} (score: {record['score']:.3f})")
                print(f"      {record['content'][:100]}...")
                print(f"      Category: {record['category']}")

    except Exception as e:
        print(f"❌ Neo4j search failed: {e}")
    finally:
        driver.close()

def search_weaviate(query: str):
    """Search Weaviate using semantic search"""
    print(f"\n🔍 Weaviate Semantic Search: '{query}'")

    try:
        # Use direct HTTP API for search
        search_query = {
            "query": query,
            "limit": 3
        }

        response = requests.post(
            "http://localhost:8081/v1/graphql",
            json={
                "query": """
                {
                  Get {
                    Document (
                      nearText: {
                        concepts: ["%s"]
                      }
                      limit: 3
                    ) {
                      title
                      content
                      doc_id
                      _additional {
                        distance
                        certainty
                      }
                    }
                  }
                }
                """ % query
            }
        )

        if response.status_code == 200:
            data = response.json()
            documents = data['data']['Get']['Document']

            for doc in documents:
                certainty = doc['_additional']['certainty']
                print(f"  📄 {doc['title']} (certainty: {certainty:.3f})")
                print(f"      {doc['content'][:100]}...")

        else:
            print(f"❌ Weaviate search failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Weaviate search failed: {e}")

def hybrid_search(query: str):
    """Demonstrate hybrid search combining both systems"""
    print(f"\n🚀 Hybrid Search: '{query}'")
    print("=" * 50)

    # Search both systems
    search_neo4j(query)
    search_weaviate(query)

    print("\n💡 In a full hybrid system, these results would be:")
    print("   • Ranked by relevance scores")
    print("   • Deduplicated by document ID")
    print("   • Enhanced with graph relationships")
    print("   • Cached for performance")

async def main():
    print("🚀 Hybrid Knowledge System Quick Demo")
    print("=" * 50)

    # Add sample data
    add_sample_documents()

    # Wait a moment for indexing
    print("\n⏳ Waiting for indexing...")
    await asyncio.sleep(2)

    # Run test queries
    test_queries = [
        "How to improve customer retention?",
        "AI implementation strategies",
        "Marketing ROI measurement"
    ]

    for query in test_queries:
        hybrid_search(query)
        print("\n" + "="*50)

    print("\n🎉 Demo completed! The hybrid system is working.")
    print("💡 Next steps:")
    print("   • Add more complex documents")
    print("   • Implement relationship extraction")
    print("   • Add caching layer")
    print("   • Build query orchestration")

if __name__ == "__main__":
    asyncio.run(main())