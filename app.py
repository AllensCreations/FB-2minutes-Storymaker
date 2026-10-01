"""
Vercel Serverless Entrypoint for FB 2minutes Storymaker
Compatible with:
1. Vercel HTTP Handler (BaseHTTPRequestHandler subclass)
2. Vercel WSGI / ASGI (app / application callable)
3. Direct AWS Lambda invocation (event, context)
4. Local testing via http.server or wsgi
"""

import base64
import gzip
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
FALLBACK_GZIP_B64 = """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"""

_cached_fallback = None

def get_fallback_html():
    global _cached_fallback
    if _cached_fallback is None:
        try:
            _cached_fallback = gzip.decompress(base64.b64decode(FALLBACK_GZIP_B64))
        except Exception:
            _cached_fallback = b"""<!DOCTYPE html><html><head><title>FB 2minutes Storymaker</title></head><body><h1>FB 2minutes Storymaker</h1><p>Online and ready.</p></body></html>"""
    return _cached_fallback

def resolve_asset(path_str):
    """Resolve requested path to bytes and content-type."""
    clean = path_str.split('?')[0].split('#')[0].strip('/')
    
    # 1. Check index routes
    if not clean or clean in ('index.html', 'index', 'web', 'web/'):
        for cand in [BASE_DIR / 'index.html', Path.cwd() / 'index.html', BASE_DIR / 'web' / 'index.html']:
            if cand.is_file():
                try:
                    return cand.read_bytes(), 'text/html; charset=utf-8'
                except Exception:
                    pass
        return get_fallback_html(), 'text/html; charset=utf-8'

    # 2. Check direct file requests
    for cand in [BASE_DIR / clean, BASE_DIR / 'web' / clean, Path.cwd() / clean]:
        if cand.is_file() and not cand.name.endswith('.py') and not cand.name.endswith('.pyc'):
            ctype, _ = mimetypes.guess_type(str(cand))
            if not ctype:
                if cand.suffix in ('.html', '.htm'):
                    ctype = 'text/html; charset=utf-8'
                elif cand.suffix == '.js':
                    ctype = 'application/javascript; charset=utf-8'
                elif cand.suffix == '.css':
                    ctype = 'text/css; charset=utf-8'
                elif cand.suffix == '.json':
                    ctype = 'application/json; charset=utf-8'
                else:
                    ctype = 'application/octet-stream'
            elif 'text/' in ctype and 'charset' not in ctype:
                ctype += '; charset=utf-8'
            try:
                return cand.read_bytes(), ctype
            except Exception:
                pass

    # 3. Fallback to index.html for SPA routes
    return get_fallback_html(), 'text/html; charset=utf-8'


class HandlerMeta(type(BaseHTTPRequestHandler)):
    """Metaclass enabling both BaseHTTPRequestHandler inheritance and direct Lambda handler(event, context) calls."""
    def __call__(cls, *args, **kwargs):
        if len(args) == 2 and isinstance(args[0], dict) and not callable(args[1]):
            # Called as Lambda handler(event, context)
            event, context = args
            path = event.get('rawPath') or event.get('path') or '/'
            content, ctype = resolve_asset(path)
            is_b64 = not (ctype.startswith('text/') or 'javascript' in ctype or 'json' in ctype)
            body = base64.b64encode(content).decode('ascii') if is_b64 else content.decode('utf-8', errors='replace')
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': ctype,
                    'Access-Control-Allow-Origin': '*',
                    'Content-Length': str(len(content))
                },
                'isBase64Encoded': is_b64,
                'body': body
            }
        return super().__call__(*args, **kwargs)


class handler(BaseHTTPRequestHandler, metaclass=HandlerMeta):
    """Vercel HTTP Handler inheriting from BaseHTTPRequestHandler."""
    def do_GET(self):
        content, ctype = resolve_asset(self.path)
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content)

    def do_HEAD(self):
        content, ctype = resolve_asset(self.path)
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS, POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, x-api-key')
        self.end_headers()

    def log_message(self, format, *args):
        pass


def wsgi_app(environ, start_response):
    """WSGI application entrypoint for WSGI servers and Vercel WSGI adapter."""
    path_info = environ.get('PATH_INFO', '/') if environ else '/'
    content, ctype = resolve_asset(path_info)
    start_response('200 OK', [
        ('Content-Type', ctype),
        ('Content-Length', str(len(content))),
        ('Access-Control-Allow-Origin', '*')
    ])
    return [content]


app = wsgi_app
application = wsgi_app

if __name__ == '__main__':
    import sys
    import time
    src_dir = BASE_DIR / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from port_helper import find_random_available_port, save_active_port

    try:
        from web.server import StorymakerRequestHandler
        server_handler = StorymakerRequestHandler
    except Exception:
        server_handler = handler

    try:
        from http.server import ThreadingHTTPServer
        server_cls = ThreadingHTTPServer
    except Exception:
        server_cls = HTTPServer

    server_cls.allow_reuse_address = True
    server = None
    active_port = None
    bind_host = os.environ.get('HOST', '0.0.0.0')

    # If PORT env var is explicitly provided, try it first
    env_port_str = os.environ.get('PORT')
    if env_port_str:
        try:
            target_port = int(env_port_str)
            server = server_cls((bind_host, target_port), server_handler)
            active_port = target_port
        except OSError:
            print(f"⚠️ Warning: Environment port {env_port_str} is in use. Picking random available port...")

    # Otherwise assign random available port
    if server is None:
        for _ in range(20):
            try:
                p = find_random_available_port(host=bind_host, min_port=5000, max_port=9999)
                server = server_cls((bind_host, p), server_handler)
                active_port = p
                break
            except OSError:
                continue


    if server is None:
        raise RuntimeError("Failed to bind server to any available port.")

    save_active_port(active_port)
    cache_buster = int(time.time())
    print("==================================================")
    print("🎬 FB-2minutes Storymaker Server Running")
    print(f"🎲 Random Assigned Port:  {active_port}")
    print(f"👉 Direct URL (No Cache): http://localhost:{active_port}/?v={cache_buster}")
    print(f"👉 Standard URL:          http://localhost:{active_port}")
    print(f"👉 Saved port marker:     {BASE_DIR / '.active_port'}")
    print("==================================================")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()
