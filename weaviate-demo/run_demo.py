#!/usr/bin/env python3
"""
Easy Demo Launcher - One-click demo runner
"""

import subprocess
import sys
import time
import webbrowser
import requests

def check_weaviate():
    """Check if Weaviate is running"""
    try:
        response = requests.get("http://localhost:8080/v1/meta", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_weaviate():
    """Start Weaviate if not running"""
    print("🐳 Starting Weaviate...")
    try:
        subprocess.run(["docker-compose", "up", "-d"], check=True, capture_output=True)
        print("✅ Weaviate started")
        
        # Wait for Weaviate to be ready
        print("⏳ Waiting for Weaviate to be ready...")
        for i in range(30):
            if check_weaviate():
                print("✅ Weaviate is ready!")
                return True
            time.sleep(1)
            print(f"   Checking... ({i+1}/30)")
        
        print("❌ Weaviate did not start properly")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Weaviate: {e}")
        return False

def main():
    print("🎯 WEAVIATE DEMO LAUNCHER")
    print("=" * 50)
    
    # Check if Weaviate is running
    print("🔍 Checking Weaviate status...")
    if not check_weaviate():
        print("⚠️  Weaviate is not running")
        if not start_weaviate():
            print("\n❌ Demo cannot start without Weaviate")
            print("💡 Try running manually: docker-compose up -d")
            sys.exit(1)
    else:
        print("✅ Weaviate is running")
    
    # Open the demo in browser
    print("\n🚀 Opening demo in browser...")
    webbrowser.open('http://localhost:3000/demo_frontend.html')
    
    print("\n🎉 DEMO READY!")
    print("=" * 50)
    print("📊 Demo URL: http://localhost:3000/demo_frontend.html")
    print("🌐 Weaviate Console: http://localhost:8080/")
    print("📈 GraphQL Playground: http://localhost:8080/v1/graphql")
    
    print("\n💡 DEMO FEATURES:")
    print("   • Interactive document browser")
    print("   • Real-time data visualization") 
    print("   • Beautiful responsive design")
    print("   • Perfect for presentations")
    
    print("\n🛑 Press Ctrl+C to stop")

if __name__ == "__main__":
    main()