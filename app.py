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
