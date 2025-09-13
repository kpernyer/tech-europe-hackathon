#!/usr/bin/env python3
"""
Step 1: Test Connection to Weaviate
"""

import requests
import json

def step1_connect():
    print("🔗 STEP 1: Testing Connection to Weaviate")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    
    try:
        # Test basic connection
        print(f"📡 Connecting to: {base_url}")
        response = requests.get(f"{base_url}/v1/meta")
        
        if response.status_code == 200:
            meta = response.json()
            print("✅ CONNECTION SUCCESSFUL!")
            print(f"   🏷️  Weaviate Version: {meta.get('version', 'unknown')}")
            print(f"   🏠 Hostname: {meta.get('hostname', 'unknown')}")
            print(f"   📦 Modules Available: {', '.join(meta.get('modules', {}).keys())}")
            
            return True
        else:
            print(f"❌ CONNECTION FAILED!")
            print(f"   Status Code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION FAILED!")
        print("   Cannot reach Weaviate at http://localhost:8080")
        print("   💡 Make sure Docker container is running:")
        print("   docker-compose up -d weaviate")
        return False
    except Exception as e:
        print(f"❌ CONNECTION FAILED!")
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    success = step1_connect()
    if success:
        print("\n🎉 Step 1 Complete! Weaviate is running and accessible.")
        print("📝 Next: Run step2_schema.py to create a document schema")
    else:
        print("\n🛠️  Fix the connection issue before proceeding.")