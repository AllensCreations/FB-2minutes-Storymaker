#!/usr/bin/env python3
"""
Serves graphify-out/graph.html on a dynamically assigned random available port
(or user specified port) to avoid overlapping server collisions.
Automatically routes root '/' to '/graph.html'
"""
import argparse
import http.server
import os
import socketserver
import sys
from pathlib import Path

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "graphify-out"))
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from port_helper import find_random_available_port
except Exception:
    def find_random_available_port(host="0.0.0.0", min_port=5100, max_port=9999):
        import socket, random
        for p in random.sample(range(min_port, max_port + 1), 50):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((host, p))
                    return p
            except OSError:
                continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, 0))
            return s.getsockname()[1]


class GraphHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/graph.html"
        return super().do_GET()


def main():
    parser = argparse.ArgumentParser(description="Serve Knowledge Graph with Random Port Assignment")
    parser.add_argument("--port", type=int, default=None, help="Port to serve on (default: randomly assigned)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    args = parser.parse_args()

    if not os.path.exists(os.path.join(BASE_DIR, "graph.html")):
        print(f"Error: graph.html not found in {BASE_DIR}", file=sys.stderr)
        sys.exit(1)

    socketserver.TCPServer.allow_reuse_address = True
    httpd = None
    active_port = None

    if args.port and args.port > 0:
        try:
            httpd = socketserver.TCPServer((args.host, args.port), GraphHandler)
            active_port = args.port
        except OSError:
            print(f"⚠️ Port {args.port} is already in use. Picking a random available port...")

    if httpd is None:
        for _ in range(20):
            p = find_random_available_port(host=args.host, min_port=5100, max_port=9999)
            try:
                httpd = socketserver.TCPServer((args.host, p), GraphHandler)
                active_port = p
                break
            except OSError:
                continue

    if httpd is None:
        print("Error: Could not bind graph server to any available port.", file=sys.stderr)
        sys.exit(1)

    graph_port_file = REPO_ROOT / ".graph_port"
    try:
        graph_port_file.write_text(str(active_port), encoding="utf-8")
    except Exception:
        pass

    print("==================================================")
    print("📊 Interactive Knowledge Graph Server Running")
    print(f"🎲 Random Assigned Port:  {active_port}")
    print(f"👉 Standard URL:          http://localhost:{active_port}")
    print(f"👉 Direct Graph URL:      http://localhost:{active_port}/graph.html")
    print(f"👉 Saved port marker:     {graph_port_file}")
    print("==================================================")

    with httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down graph server.")


if __name__ == "__main__":
    main()

