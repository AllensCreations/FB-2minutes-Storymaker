import json
import os
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "api"))

from render import handler


class DummyResponseStream:
    def __init__(self):
        self.data = bytearray()

    def write(self, b):
        self.data.extend(b)

    def get_json(self):
        return json.loads(self.data.decode("utf-8"))


class TestApiGateway(unittest.TestCase):

    def setUp(self):
        self.mock_rfile = BytesIO()
        self.mock_wfile = DummyResponseStream()

    def create_handler(self, method, path, headers=None, body=b""):
        req = MagicMock()
        h = handler.__new__(handler)
        h.rfile = BytesIO(body)
        h.wfile = DummyResponseStream()
        h.headers = headers or {}
        h.command = method
        h.path = path
        h.send_response = MagicMock()
        h.send_header = MagicMock()
        h.end_headers = MagicMock()
        return h

    def test_get_documentation(self):
        h = self.create_handler("GET", "/api/render")
        h.do_GET()
        h.send_response.assert_called_with(200)
        resp = h.wfile.get_json()
        self.assertEqual(resp["status"], "online")
        self.assertIn("endpoints", resp)

    def test_post_unauthorized_when_secret_set(self):
        with patch.dict(os.environ, {"API_SECRET_KEY": "supersecret123"}):
            h = self.create_handler(
                "POST", "/api/render",
                headers={"Content-Length": "2", "x-api-key": "wrong_key"},
                body=b"{}"
            )
            h.do_POST()
            h.send_response.assert_called_with(401)
            resp = h.wfile.get_json()
            self.assertFalse(resp["ok"])
            self.assertIn("Unauthorized", resp["error"])

    @patch("urllib.request.urlopen")
    def test_post_authorized_dispatches_successfully(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 204
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        payload = {
            "title": "Story Title",
            "description": "Story Description",
            "scheduled_time": "2026-09-20T18:00:00Z",
            "script": "Scene 1: Hi\n(Next image)\nScene 2: Bye",
            "make_webhook_url": "https://hook.make.com/123"
        }
        body_bytes = json.dumps(payload).encode("utf-8")

        with patch.dict(os.environ, {
            "API_SECRET_KEY": "mysecret",
            "GH_PAT": "ghp_mocktoken123",
            "GITHUB_REPOSITORY": "AllensCreations/FB-2minutes-Storymaker"
        }):
            h = self.create_handler(
                "POST", "/api/render",
                headers={
                    "Content-Length": str(len(body_bytes)),
                    "x-api-key": "mysecret"
                },
                body=body_bytes
            )
            h.do_POST()
            h.send_response.assert_called_with(202)
            resp = h.wfile.get_json()
            self.assertTrue(resp["ok"])
            self.assertEqual(resp["status"], "queued")
            self.assertEqual(resp["scenes_detected"], 2)
            self.assertEqual(resp["title"], "Story Title")


if __name__ == "__main__":
    unittest.main()
