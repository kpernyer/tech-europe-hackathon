#!/usr/bin/env python3
"""
Demo Server - Serves the beautiful Weaviate frontend with CORS handling
"""

import http.server
import socketserver
import webbrowser
import threading
import time
from urllib.parse import urlparse

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def start_demo_server(port=3333):
    """Start the demo server"""
    print(f"🚀 WEAVIATE DEMO SERVER")
    print("=" * 50)
    print(f"🌐 Starting demo server on port {port}")
    
    try:
        with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
            print(f"✅ Demo server running at: http://localhost:{port}")
            print(f"📄 Enhanced Demo: http://localhost:{port}/enhanced_demo.html")
            print(f"📄 Simple Frontend: http://localhost:{port}/demo_frontend.html")
            print("\n🎯 DEMO FEATURES:")
            print("   • Beautiful visual interface for Weaviate data")
            print("   • Real-time document browser")
            print("   • Schema visualization")
            print("   • Direct links to Weaviate console")
            print("   • Responsive design perfect for presentations")
            
            print(f"\n💡 Opening demo in your browser...")
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(1)
                webbrowser.open(f'http://localhost:{port}/enhanced_demo.html')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            print(f"\n🛑 Press Ctrl+C to stop the server")
            print("-" * 50)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Demo server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use")
            print(f"💡 Try a different port or stop the other service")
            alternative_port = port + 1
            print(f"🔄 Trying port {alternative_port}...")
            start_demo_server(alternative_port)
        else:
            print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_demo_server()