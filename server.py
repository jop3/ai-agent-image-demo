#!/usr/bin/env python3
"""
Simple HTTP server to serve the web interface
"""

import http.server
import socketserver
import os
from pathlib import Path

PORT = int(os.getenv("HTTP_PORT", "8000"))
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🌐 HTTP Server igång på http://localhost:{PORT}")
        print(f"📂 Serverar filer från: {DIRECTORY}")
        print("\n🚀 Öppna http://localhost:8000 i din webbläsare")
        print("🎤 Tryck Ctrl+C för att stoppa\n")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Stänger ner servern...")
