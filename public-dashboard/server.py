#!/usr/bin/env python3
"""
Simple HTTP server to host Bhashini QoS Dashboards publicly
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 8080
HOST = '0.0.0.0'  # Bind to all interfaces for public access

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for public access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Serve index.html for root path
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

def main():
    # Change to the directory containing this script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print(f"🚀 Starting Bhashini QoS Dashboard Server")
    print(f"📍 Server running at: http://{HOST}:{PORT}")
    print(f"🌐 Public access: http://localhost:{PORT}")
    print(f"📁 Serving files from: {script_dir}")
    print(f"📊 Dashboard portal: http://localhost:{PORT}/index.html")
    print(f"🔌 Grafana backend: http://localhost:3010")
    print(f"\n💡 To access from other devices on your network:")
    print(f"   Use your computer's IP address instead of localhost")
    print(f"   Example: http://192.168.1.100:{PORT}")
    print(f"\n⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
            print(f"✅ Server started successfully!")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use. Try a different port:")
            print(f"   python server.py --port {PORT + 1}")
        else:
            print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--port':
        try:
            PORT = int(sys.argv[2])
        except (IndexError, ValueError):
            print("Usage: python server.py [--port PORT_NUMBER]")
            sys.exit(1)
    
    main()
