"""
Unit tests for Turso (libSQL Edge SQLite) Client.
Tests pipeline execution, schema initialization, duplicate checking, and story operations.
"""

import io
import json
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import turso_client


class TestTursoClient(unittest.TestCase):
    def setUp(self):
        with turso_client._SCHEMA_INIT_LOCK:
            turso_client._INITIALIZED_TURSO_URLS.clear()

    def test_normalize_turso_url(self):
        self.assertEqual(
            turso_client.normalize_turso_url("libsql://my-db.turso.io"),
            "https://my-db.turso.io"
        )
        self.assertEqual(
            turso_client.normalize_turso_url("libsql://my-db.turso.io/"),
            "https://my-db.turso.io"
        )
        self.assertEqual(
            turso_client.normalize_turso_url("my-db.turso.io"),
            "https://my-db.turso.io"
        )
        self.assertEqual(
            turso_client.normalize_turso_url("https://my-db.turso.io"),
            "https://my-db.turso.io"
        )
        self.assertEqual(turso_client.normalize_turso_url(""), "")

    @patch("urllib.request.urlopen")
    def test_execute_turso_pipeline_success(self, mock_urlopen):
        mock_resp_data = {
            "results": [
                {
                    "type": "ok",
                    "response": {
                        "type": "execute",
                        "result": {
                            "cols": [{"name": "count"}],
                            "rows": [[{"type": "integer", "value": "1"}]]
                        }
                    }
                }
            ]
        }
        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps(mock_resp_data).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_cm

        res = turso_client.execute_turso_pipeline(
            "https://test-db.turso.io",
            "mock-auth-token",
            [("SELECT COUNT(*) FROM stories;", None)]
        )
        self.assertEqual(res, mock_resp_data)

        # Verify request structure
        call_args = mock_urlopen.call_args[0]
        req = call_args[0]
        self.assertEqual(req.full_url, "https://test-db.turso.io/v2/pipeline")
        self.assertEqual(req.headers.get("Authorization"), "Bearer mock-auth-token")
        self.assertEqual(req.headers.get("Content-type"), "application/json")

    @patch("urllib.request.urlopen")
    def test_execute_turso_pipeline_with_typed_args(self, mock_urlopen):
        mock_cm = MagicMock()
        mock_cm.read.return_value = b'{"results": []}'
        mock_urlopen.return_value.__enter__.return_value = mock_cm

        turso_client.execute_turso_pipeline(
            "test-db.turso.io",
            "token",
            [("INSERT INTO stories (a, b, c, d, e) VALUES (?, ?, ?, ?, ?);", ["text", 42, 3.14, True, None])]
        )

        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data.decode("utf-8"))
        stmt_args = payload["requests"][0]["stmt"]["args"]
        self.assertEqual(stmt_args[0], {"type": "text", "value": "text"})
        self.assertEqual(stmt_args[1], {"type": "integer", "value": "42"})
        self.assertEqual(stmt_args[2], {"type": "float", "value": 3.14})
        self.assertEqual(stmt_args[3], {"type": "integer", "value": "1"})
        self.assertEqual(stmt_args[4], {"type": "null"})

    @patch("urllib.request.urlopen")
    def test_execute_turso_pipeline_http_error(self, mock_urlopen):
        err = urllib.error.HTTPError(
            url="https://test.turso.io/v2/pipeline",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=io.BytesIO(b'{"message": "Invalid auth token"}')
        )
        mock_urlopen.side_effect = err

        with self.assertRaises(RuntimeError) as ctx:
            turso_client.execute_turso_pipeline("https://test.turso.io", "bad_token", [("SELECT 1;", None)])
        self.assertIn("Turso API HTTP 401", str(ctx.exception))

    @patch("turso_client.execute_turso_pipeline")
    def test_init_turso_schema(self, mock_exec):
        mock_exec.return_value = {"results": []}
        turso_client.init_turso_schema("https://test.turso.io", "token")
        mock_exec.assert_called_once()
        all_sqls = [sql for sql, _ in mock_exec.call_args.args[2]]
        self.assertTrue(any("CREATE TABLE IF NOT EXISTS stories" in s for s in all_sqls))
        self.assertTrue(any("uploaded_to_fb_ig" in s for s in all_sqls))
        self.assertTrue(any("uploaded_to_youtube" in s for s in all_sqls))

    @patch("turso_client.execute_turso_pipeline")
    def test_schema_initialization_is_cached_per_normalized_endpoint(self, mock_exec):
        mock_exec.return_value = {"results": []}

        turso_client.init_turso_schema("libsql://test.turso.io/", "token")
        turso_client.init_turso_schema("https://test.turso.io", "token")
        self.assertEqual(mock_exec.call_count, 1)
        self.assertEqual(len(mock_exec.call_args.args[2]), 4)

        turso_client.init_turso_schema("https://another.turso.io", "token")
        self.assertEqual(mock_exec.call_count, 2)

    @patch("turso_client.execute_turso_pipeline")
    def test_schema_initialization_retries_after_transport_failure(self, mock_exec):
        mock_exec.side_effect = [RuntimeError("temporary failure"), {"results": []}]

        turso_client.init_turso_schema("https://retry.turso.io", "token")
        turso_client.init_turso_schema("https://retry.turso.io", "token")

        self.assertEqual(mock_exec.call_count, 2)

    @patch("turso_client.execute_turso_pipeline")
    def test_turso_test_connection(self, mock_exec):
        mock_exec.return_value = {"results": [{"type": "ok"}]}
        res = turso_client.turso_test_connection("https://test.turso.io", "token")
        self.assertTrue(res["ok"])
        self.assertIn("Connected to Turso database successfully", res["message"])
        sql_statements = [
            statement
            for call in mock_exec.call_args_list
            for statement, _ in call.args[2]
        ]
        self.assertFalse(any("INSERT INTO stories" in statement for statement in sql_statements))

    @patch("turso_client.execute_turso_pipeline")
    def test_turso_log_story(self, mock_exec):
        mock_exec.return_value = {"results": [{"type": "ok"}]}
        turso_client.turso_log_story(
            "https://test.turso.io",
            "token",
            "forest.mp4",
            "Deep in the forest",
            "#magic #forest",
            "ready",
            "pending",
            "pending",
            "/Storymaker_Exports/forest.mp4"
        )
        self.assertTrue(mock_exec.called)
        statements = mock_exec.call_args[0][2]
        sql, args = statements[0]
        self.assertIn("INSERT INTO stories", sql)
        self.assertIn("ON CONFLICT(filename) DO UPDATE", sql)
        self.assertEqual(args, ["forest.mp4", "Deep in the forest", "#magic #forest", "/Storymaker_Exports/forest.mp4", "ready", "pending", "pending"])

    @patch("turso_client.execute_turso_pipeline")
    def test_turso_check_duplicate_true(self, mock_exec):
        mock_exec.return_value = {
            "results": [
                {
                    "type": "ok",
                    "response": {
                        "type": "execute",
                        "result": {
                            "cols": [{"name": "filename"}],
                            "rows": [[{"type": "text", "value": "forest.mp4"}]]
                        }
                    }
                }
            ]
        }
        exists = turso_client.turso_check_duplicate("https://test.turso.io", "token", "forest.mp4")
        self.assertTrue(exists)

    @patch("turso_client.execute_turso_pipeline")
    def test_turso_check_duplicate_false(self, mock_exec):
        mock_exec.return_value = {
            "results": [
                {
                    "type": "ok",
                    "response": {
                        "type": "execute",
                        "result": {
                            "cols": [{"name": "filename"}],
                            "rows": []
                        }
                    }
                }
            ]
        }
        exists = turso_client.turso_check_duplicate("https://test.turso.io", "token", "notfound.mp4")
        self.assertFalse(exists)

    @patch("turso_client.execute_turso_pipeline")
    def test_turso_delete_story(self, mock_exec):
        mock_exec.return_value = {"results": [{"type": "ok"}]}
        turso_client.turso_delete_story("https://test.turso.io", "token", "forest.mp4")
        sql, args = mock_exec.call_args[0][2][0]
        self.assertIn("DELETE FROM stories", sql)
        self.assertEqual(args, ["forest.mp4"])

    @patch("turso_client.execute_turso_pipeline")
    def test_turso_update_status(self, mock_exec):
        mock_exec.return_value = {"results": [{"type": "ok"}]}
        turso_client.turso_update_status(
            "https://test.turso.io",
            "token",
            "forest.mp4",
            status="published",
            uploaded_to_fb_ig="published",
            uploaded_to_youtube="pending"
        )
        sql, args = mock_exec.call_args[0][2][0]
        self.assertIn("UPDATE stories SET", sql)
        self.assertIn("uploaded_to_fb_ig = ?", sql)
        self.assertIn("uploaded_to_youtube = ?", sql)
        self.assertEqual(args, ["published", "published", "pending", "forest.mp4"])

    @patch("turso_client.execute_turso_pipeline")
    def test_turso_list_stories(self, mock_exec):
        mock_exec.return_value = {
            "results": [
                {
                    "type": "ok",
                    "response": {
                        "type": "execute",
                        "result": {
                            "cols": [
                                {"name": "filename"},
                                {"name": "caption"},
                                {"name": "status"},
                                {"name": "uploaded_to_fb_ig"},
                                {"name": "uploaded_to_youtube"}
                            ],
                            "rows": [
                                [
                                    {"type": "text", "value": "story_1.mp4"},
                                    {"type": "text", "value": "A wonderful journey"},
                                    {"type": "text", "value": "published"},
                                    {"type": "text", "value": "published"},
                                    {"type": "text", "value": "pending"}
                                ]
                            ]
                        }
                    }
                }
            ]
        }
        stories = turso_client.turso_list_stories("https://test.turso.io", "token", limit=10)
        self.assertEqual(len(stories), 1)
        self.assertEqual(stories[0]["filename"], "story_1.mp4")
        self.assertEqual(stories[0]["caption"], "A wonderful journey")
        self.assertEqual(stories[0]["status"], "published")
        self.assertEqual(stories[0]["uploaded_to_fb_ig"], "published")
        self.assertEqual(stories[0]["uploaded_to_youtube"], "pending")


if __name__ == "__main__":
    unittest.main()
