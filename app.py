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
