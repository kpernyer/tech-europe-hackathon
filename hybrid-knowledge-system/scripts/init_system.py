#!/usr/bin/env python3
"""
System Initialization Script: Sets up schemas, indexes, and basic configuration
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.clients.neo4j_client import Neo4jClient
from src.clients.weaviate_client import WeaviateClient
from src.utils.embeddings import EmbeddingService
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def main():
    """Initialize the hybrid knowledge system"""
    
    print("🏗️  Initializing Hybrid Knowledge System")
    print("=" * 50)
    
    # Initialize services
    neo4j = Neo4jClient()
    weaviate = WeaviateClient()
    embedding_service = EmbeddingService()
    
    try:
        # Test embedding service
        print("🧠 Testing embedding service...")
        health = await embedding_service.health_check()
        if health['status'] == 'healthy':
            print(f"   ✅ {health['provider']} model: {health['model']}")
            print(f"   📏 Dimensions: {health['dimensions']}")
        else:
            print(f"   ❌ Embedding service error: {health['error']}")
            return
        
        # Connect to Neo4j
        print("\n🔗 Connecting to Neo4j...")
        await neo4j.connect()
        
        # Connect to Weaviate
        print("🔗 Connecting to Weaviate...")
        await weaviate.connect()
        
        # Create Neo4j indexes
        print("\n📊 Creating Neo4j indexes...")
        
        # Vector index for documents
        success = await neo4j.create_vector_index(
            index_name="document_embeddings",
            node_label="Document",
            property_name="embedding",
            dimensions=embedding_service.get_dimensions(),
            similarity_function="cosine"
        )
        if success:
            print("   ✅ Document vector index created")
        else:
            print("   ❌ Document vector index creation failed")
        
        # Vector index for entities
        success = await neo4j.create_vector_index(
            index_name="entity_embeddings",
            node_label="Entity",
            property_name="embedding",
            dimensions=embedding_service.get_dimensions(),
            similarity_function="cosine"
        )
        if success:
            print("   ✅ Entity vector index created")
        else:
            print("   ❌ Entity vector index creation failed")
        
        # Fulltext index
        success = await neo4j.create_fulltext_index(
            index_name="document_fulltext",
            node_labels=["Document", "Entity", "Record"],
            properties=["content", "title", "description", "name"]
        )
        if success:
            print("   ✅ Fulltext index created")
        else:
            print("   ❌ Fulltext index creation failed")
        
        # Create Weaviate schema
        print("\n🏗️  Creating Weaviate schema...")
        success = await weaviate.create_schema("Document", force_recreate=False)
        if success:
            print("   ✅ Weaviate Document schema created")
        else:
            print("   ❌ Weaviate schema creation failed")
        
        # Test system connectivity
        print("\n🔍 Testing system health...")
        
        # Neo4j health check
        neo4j_stats = await neo4j.get_database_stats()
        if neo4j_stats:
            print(f"   ✅ Neo4j: {neo4j_stats.get('nodeCount', 0)} nodes, {neo4j_stats.get('relCount', 0)} relationships")
        else:
            print("   ❌ Neo4j health check failed")
        
        # Weaviate health check
        weaviate_health = await weaviate.health_check()
        if weaviate_health.get('ready', False):
            doc_count = await weaviate.get_document_count()
            print(f"   ✅ Weaviate: Ready, {doc_count} documents")
        else:
            print("   ❌ Weaviate health check failed")
        
        print(f"\n🎉 System initialization completed successfully!")
        print(f"🚀 Ready for hybrid knowledge processing!")
        
        # Display system info
        print(f"\n📋 System Configuration:")
        print(f"   Neo4j URI: {neo4j.uri}")
        print(f"   Weaviate URL: {weaviate.config.url}")
        print(f"   Embedding Model: {embedding_service.get_model_info()['model_name']}")
        print(f"   Vector Dimensions: {embedding_service.get_dimensions()}")
        
    except Exception as e:
        logger.error(f"System initialization failed: {e}")
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)
    
    finally:
        # Close connections
        await neo4j.close()
        await weaviate.close()

if __name__ == "__main__":
    asyncio.run(main())