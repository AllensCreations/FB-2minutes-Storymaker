import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import tempfile
import urllib.request
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch
import app
import index
import web.server as story_server
from web.server import _story_output_filename


class TestServerlessApp(unittest.TestCase):
    def test_apply_caption_word_timings_requires_matching_scene(self):
        scene = SimpleNamespace(
            text="one two", start_time=0.0, end_time=2.0, duration=2.0,
            caption_word_times=[]
        )
        timeline = SimpleNamespace(scenes=[scene])
        timing = {
            "text": "one two", "start": 0, "end": 2,
            "words": [[0.2, 0.4], [1.0, 1.2]]
        }

        story_server._apply_caption_word_timings(timeline, [timing])
        self.assertEqual(scene.caption_word_times, [(0.2, 0.4), (1.0, 1.2)])

        scene.caption_word_times = []
        story_server._apply_caption_word_timings(timeline, [{
            **timing, "text": "different text"
        }])
        self.assertEqual(scene.caption_word_times, [])

    def test_story_filename_has_only_one_mp4_extension(self):
        self.assertEqual(_story_output_filename("A Story.mp4", "item-1"), "a-story.mp4")
        self.assertEqual(_story_output_filename("A Story.MP4.mp4", "item-1"), "a-story.mp4")

    def test_publish_queue_api_returns_job_snapshot(self):
        with patch.dict(story_server.ITEM_RENDER_STATES, {
            "item-1": {
                "job_type": "publish", "status": "running", "progress": 42,
                "title": "A Story", "message": "Rendering",
                "updated_at": 123, "logs": [{"time": 123, "message": "Rendering", "progress": 42}]
            },
            "item-2": {"job_type": "render", "status": "running", "progress": 10}
        }, clear=True):
            server = HTTPServer(("127.0.0.1", 0), story_server.StorymakerRequestHandler)
            thread = threading.Thread(target=server.handle_request)
            thread.start()
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{server.server_port}/api/publish-queue"
                ) as response:
                    data = json.loads(response.read())
                self.assertEqual(len(data["jobs"]), 1)
                self.assertEqual(data["jobs"][0]["item_id"], "item-1")
                self.assertEqual(data["jobs"][0]["progress"], 42)
                self.assertEqual(data["jobs"][0]["logs"][0]["message"], "Rendering")
                self.assertEqual(data["jobs"][0]["updated_at"], 123)
            finally:
                server.server_close()
                thread.join()

    def test_auto_publish_api_queues_background_job(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            item_dir = Path(temp_dir) / "item-1"
            item_dir.mkdir()
            (item_dir / "voiceover.wav").write_bytes(b"audio")
            (item_dir / "rendered_video.webm").write_bytes(b"browser render")

            class FakeManager:
                items_dir = Path(temp_dir)

                def get_item(self, item_id):
                    return {
                        "id": item_id, "title": "Queued story", "audio_file": "voiceover.wav",
                        "scenes": [{"text": "A scene"}]
                    }

                def broadcast_event(self, *args):
                    pass

            server = HTTPServer(("127.0.0.1", 0), story_server.StorymakerRequestHandler)
            thread = threading.Thread(target=server.handle_request)
            thread.start()
            payload = {
                "db_token": "test-token", "turso_db_url": "https://db.example",
                "turso_auth_token": "test-auth", "rendered_video_extension": "webm"
            }
            with (
                patch.object(story_server, "default_manager", FakeManager()),
                patch.dict(story_server.ITEM_RENDER_STATES, {}, clear=True),
                patch("gemini_service.read_env_settings", return_value={}),
                patch.object(story_server, "check_turso_duplicate", return_value=False),
                patch.object(story_server, "check_dropbox_duplicate", return_value=False),
                patch.object(story_server.threading, "Thread") as job_thread,
            ):
                try:
                    request = urllib.request.Request(
                        f"http://127.0.0.1:{server.server_port}/api/items/item-1/auto-publish",
                        data=json.dumps(payload).encode(),
                        headers={"Content-Type": "application/json"},
                        method="POST"
                    )
                    with urllib.request.urlopen(request) as response:
                        data = json.loads(response.read())
                    self.assertTrue(data["ok"])
                    self.assertEqual(data["title"], "Queued story")
                    self.assertEqual(data["filename"], "queued-story.webm")
                    job_thread.return_value.start.assert_called_once()
                    self.assertEqual(job_thread.call_args.kwargs["args"][-1], "webm")
                    self.assertEqual(story_server.ITEM_RENDER_STATES["item-1"]["status"], "starting")
                finally:
                    server.server_close()
                    thread.join()

    def test_auto_publish_renders_over_existing_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            items_dir = root / "items"
            item_folder = items_dir / "item-1"
            item_folder.mkdir(parents=True)
            (item_folder / "voiceover.wav").write_bytes(b"audio")
            output_dir = root / "output"
            output_dir.mkdir()
            output_path = output_dir / "current-story.mp4"
            output_path.write_bytes(b"stale render")

            class FakeManager:
                def __init__(self):
                    self.items_dir = items_dir

                def get_item(self, item_id):
                    return {"id": item_id, "title": "Current Story", "audio_file": "voiceover.wav"}

                def broadcast_event(self, *args):
                    pass

                def mark_publish_complete(self, *args):
                    pass

            with (
                patch.object(story_server, "default_manager", FakeManager()),
                patch.object(story_server, "OUTPUT_DIR", output_dir),
                patch.object(story_server, "SpeechCueAlignEngine") as aligner_class,
                patch.object(story_server, "SceneDurationDirector") as director_class,
                patch.dict(story_server.ITEM_RENDER_STATES, {}, clear=True),
                patch("exporter.VideoExporter") as exporter_class,
            ):
                aligner_class.return_value.get_audio_duration.return_value = 2
                aligner_class.return_value.align_speech_with_script.return_value = object()
                director_class.return_value.build_timeline.return_value = SimpleNamespace(scenes=[])
                exporter_class.return_value.export_video.side_effect = (
                    lambda **kwargs: Path(kwargs["output_path"]).write_bytes(b"fresh render")
                )

                story_server.auto_publish_story_item_thread("item-1", {})

            exporter_class.return_value.export_video.assert_called_once()
            self.assertEqual(output_path.read_bytes(), b"fresh render")

    def test_browser_render_is_saved_before_publish_queueing(self):
        repo_root = Path(__file__).resolve().parent.parent
        for page in ("index.html", "web/index.html", "AR.html"):
            with self.subTest(page=page):
                source = (repo_root / page).read_text(encoding="utf-8")
                self.assertIn("async function renderStudioVideoForQueue()", source)
                self.assertIn("await renderStudioVideoForQueue()", source)
                self.assertIn("`/api/items/${itemId}/save-render`", source)
                self.assertIn("rendered_video_extension: renderedVideo.extension", source)
                self.assertIn("`/api/items/${item.id}/rendered-video-info`", source)
                self.assertIn("Queue Saved Render", source)
                self.assertIn("Recent queue activity", source)
                self.assertIn("data-queue-elapsed", source)
                self.assertNotIn("renderAndAutoPublish", source)

    def test_saved_browser_render_info_and_invalidation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            item_dir = Path(temp_dir) / "item-1"
            item_dir.mkdir()
            rendered_path = item_dir / "rendered_video.mp4"
            rendered_path.write_bytes(b"saved render")

            class FakeManager:
                items_dir = Path(temp_dir)

                def get_item(self, item_id):
                    return {"id": item_id} if item_id == "item-1" else None

                def get_item_file_path(self, item_id, filename):
                    path = self.items_dir / item_id / filename
                    return path if path.is_file() else None

                def save_item_cuts(self, item_id, cuts, timings, texts):
                    return {"id": item_id}

                def save_item_audio(self, item_id, audio_bytes, filename):
                    return {"id": item_id, "audio_url": "/audio.wav"}

            manager = FakeManager()

            def request(path, data=None, content_type=None):
                server = HTTPServer(("127.0.0.1", 0), story_server.StorymakerRequestHandler)
                thread = threading.Thread(target=server.handle_request)
                thread.start()
                headers = {"Content-Type": content_type} if content_type else {}
                try:
                    with patch.object(story_server, "default_manager", manager):
                        req = urllib.request.Request(
                            f"http://127.0.0.1:{server.server_port}{path}",
                            data=data,
                            headers=headers,
                            method="POST" if data is not None else "GET"
                        )
                        with urllib.request.urlopen(req) as response:
                            return json.loads(response.read())
                finally:
                    server.server_close()
                    thread.join()

            info = request("/api/items/item-1/rendered-video-info")
            self.assertEqual(
                info,
                {
                    "ok": True, "item_id": "item-1", "available": True,
                    "extension": "mp4", "bytes": len(b"saved render")
                }
            )

            timeline_result = request(
                "/api/items/item-1/save-timeline",
                data=json.dumps({"cuts": [0, 1]}).encode(),
                content_type="application/json"
            )
            self.assertTrue(timeline_result["ok"])
            self.assertFalse(rendered_path.exists())

            rendered_webm = item_dir / "rendered_video.webm"
            rendered_webm.write_bytes(b"another saved render")
            audio_result = request(
                "/api/items/item-1/save-audio",
                data=b"replacement audio",
                content_type="audio/wav"
            )
            self.assertTrue(audio_result["ok"])
            self.assertFalse(rendered_webm.exists())

    def test_save_browser_render_api_persists_video_under_item(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            item_dir = Path(temp_dir) / "item-1"
            item_dir.mkdir()

            class FakeManager:
                items_dir = Path(temp_dir)

                def get_item(self, item_id):
                    return {"id": item_id} if item_id == "item-1" else None

            server = HTTPServer(("127.0.0.1", 0), story_server.StorymakerRequestHandler)
            thread = threading.Thread(target=server.handle_request)
            thread.start()
            with patch.object(story_server, "default_manager", FakeManager()):
                try:
                    request = urllib.request.Request(
                        f"http://127.0.0.1:{server.server_port}/api/items/item-1/save-render",
                        data=b"browser rendered webm",
                        headers={"Content-Type": "video/webm"},
                        method="POST"
                    )
                    with urllib.request.urlopen(request) as response:
                        data = json.loads(response.read())
                    self.assertTrue(data["ok"])
                    self.assertEqual((item_dir / "rendered_video.webm").read_bytes(), b"browser rendered webm")
                finally:
                    server.server_close()
                    thread.join()

    def test_publish_worker_uploads_browser_render_without_ffmpeg(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            item_dir = root / "items" / "item-1"
            item_dir.mkdir(parents=True)
            (item_dir / "rendered_video.webm").write_bytes(b"browser render")
            output_dir = root / "output"
            output_dir.mkdir()

            class FakeManager:
                items_dir = root / "items"

                def get_item(self, item_id):
                    return {"id": item_id, "title": "Browser Story"}

                def broadcast_event(self, *args):
                    pass

                def mark_publish_complete(self, *args):
                    pass

            with (
                patch.object(story_server, "default_manager", FakeManager()),
                patch.object(story_server, "OUTPUT_DIR", output_dir),
                patch.dict(story_server.ITEM_RENDER_STATES, {}, clear=True),
                patch("exporter.VideoExporter") as exporter_class,
                patch.object(story_server, "upload_file_to_dropbox") as upload,
            ):
                story_server.auto_publish_story_item_thread(
                    "item-1", {"token": "test-token"}, rendered_video_extension="webm"
                )
                job = story_server.ITEM_RENDER_STATES["item-1"]
                self.assertEqual(job["status"], "done")
                self.assertTrue(any(
                    "Dropbox upload complete" in log["message"] for log in job["logs"]
                ))
                self.assertTrue(any(
                    "waiting for Dropbox response" in log["message"] for log in job["logs"]
                ))

            exporter_class.assert_not_called()
            upload.assert_called_once()
            self.assertEqual(upload.call_args.args[1].read_bytes(), b"browser render")

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
        self.assertEqual(len(fallback), 62921)
        self.assertIn(b'StoryShorts Studio', fallback)


if __name__ == '__main__':
    unittest.main()
