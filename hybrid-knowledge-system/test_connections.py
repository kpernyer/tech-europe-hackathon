#!/usr/bin/env python3
"""
Simple connection test script
"""
import os
import asyncio
from dotenv import load_dotenv
import neo4j
import weaviate
import redis

load_dotenv()

async def test_neo4j():
    print("Testing Neo4j...")
    driver = neo4j.GraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
    )
    try:
        with driver.session() as session:
            result = session.run('RETURN "Neo4j Connected!" as message')
            message = result.single()['message']
            print(f"✅ {message}")
            return True
    except Exception as e:
        print(f"❌ Neo4j error: {e}")
        return False
    finally:
        driver.close()

async def test_weaviate():
    print("Testing Weaviate...")
    try:
        # Try HTTP client first
        import requests
        response = requests.get("http://localhost:8081/v1/meta", timeout=5)
        if response.status_code == 200:
            print("✅ Weaviate Connected (HTTP)!")
            return True
        else:
            print(f"❌ Weaviate HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Weaviate error: {e}")
        return False

async def test_redis():
    print("Testing Redis...")
    try:
        r = redis.Redis(host='localhost', port=6380, db=0)
        r.ping()
        print("✅ Redis Connected!")
        return True
    except Exception as e:
        print(f"❌ Redis error: {e}")
        return False

async def main():
    print("🔍 Testing system connections...")
    print("=" * 40)

    neo4j_ok = await test_neo4j()
    weaviate_ok = await test_weaviate()
    redis_ok = await test_redis()

    print("\n📊 Connection Summary:")
    print(f"Neo4j: {'✅' if neo4j_ok else '❌'}")
    print(f"Weaviate: {'✅' if weaviate_ok else '❌'}")
    print(f"Redis: {'✅' if redis_ok else '❌'}")

    if all([neo4j_ok, weaviate_ok, redis_ok]):
        print("\n🎉 All systems are ready!")
        return True
    else:
        print("\n❌ Some systems are not ready")
        return False

if __name__ == "__main__":
    asyncio.run(main())