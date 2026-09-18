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
