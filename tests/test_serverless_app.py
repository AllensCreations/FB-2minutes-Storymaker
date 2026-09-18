import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.request
import app
import index


class TestServerlessApp(unittest.TestCase):
    def test_issubclass_base_http_request_handler(self):
        """Vercel's vc_init.py requires issubclass(handler, BaseHTTPRequestHandler)."""
        self.assertTrue(issubclass(app.handler, BaseHTTPRequestHandler))
        self.assertTrue(issubclass(index.handler, BaseHTTPRequestHandler))

    def test_http_server_serves_html(self):
        """Vercel executes handler via HTTPServer in HTTP Handler mode."""
        server = HTTPServer(('127.0.0.1', 0), app.handler)
        port = server.server_address[1]
        t = threading.Thread(target=server.handle_request)
        t.start()

        try:
            req = urllib.request.Request(f'http://127.0.0.1:{port}/')
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                content = resp.read()
                self.assertIn(b'StoryShorts Studio', content)
                self.assertGreater(len(content), 10000)
        finally:
            server.server_close()
            t.join()

    def test_wsgi_app_serves_html(self):
        """Vercel WSGI mode calls app(environ, start_response)."""
        status_received = []
        headers_received = []

        def start_response(status, headers):
            status_received.append(status)
            headers_received.extend(headers)

        chunks = app.app({'PATH_INFO': '/'}, start_response)
        full_body = b''.join(chunks)

        self.assertIn('200 OK', status_received[0])
        self.assertGreater(len(full_body), 10000)
        self.assertIn(b'StoryShorts Studio', full_body)

    def test_lambda_direct_invocation(self):
        """Metaclass allows direct AWS Lambda (event, context) calls."""
        event = {'rawPath': '/', 'headers': {}}
        res = app.handler(event, None)
        self.assertEqual(res['statusCode'], 200)
        self.assertIn('text/html', res['headers']['Content-Type'])
        self.assertGreater(len(res['body']), 10000)
        self.assertIn('StoryShorts Studio', res['body'])

    def test_embedded_fallback_integrity(self):
        """Fallback decompresses to full index.html even without disk access."""
        fallback = app.get_fallback_html()
        self.assertEqual(len(fallback), 60025)
        self.assertIn(b'StoryShorts Studio', fallback)


if __name__ == '__main__':
    unittest.main()
