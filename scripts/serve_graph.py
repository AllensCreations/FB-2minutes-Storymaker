#!/usr/bin/env python3
"""
Serves graphify-out/graph.html on http://localhost:5099
Automatically routes root '/' to '/graph.html'
"""
import http.server
import socketserver
import os
import sys

PORT = 5099
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "graphify-out"))

class GraphHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/graph.html"
        return super().do_GET()

def main():
    if not os.path.exists(os.path.join(BASE_DIR, "graph.html")):
        print(f"Error: graph.html not found in {BASE_DIR}", file=sys.stderr)
        sys.exit(1)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), GraphHandler) as httpd:
        print(f"Interactive knowledge graph live at http://localhost:{PORT}")
        print(f"Direct URL: http://localhost:{PORT}/graph.html")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    main()
