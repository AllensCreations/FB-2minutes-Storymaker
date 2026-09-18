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
import json
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
    for cand in [BASE_DIR / clean, Path.cwd() / clean]:
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
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), handler)
    print(f'Starting local server on http://localhost:{port}')
    server.serve_forever()
