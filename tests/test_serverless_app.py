import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import tempfile
import urllib.request
from pathlib import Path
from unittest.mock import patch
import app
import index
import web.server as story_server
from web.server import _story_output_filename


class TestServerlessApp(unittest.TestCase):
    def test_story_filename_has_only_one_mp4_extension(self):
        self.assertEqual(_story_output_filename("A Story.mp4", "item-1"), "a-story.mp4")
        self.assertEqual(_story_output_filename("A Story.MP4.mp4", "item-1"), "a-story.mp4")

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
                director_class.return_value.build_timeline.return_value = []
                exporter_class.return_value.export_video.side_effect = (
                    lambda **kwargs: Path(kwargs["output_path"]).write_bytes(b"fresh render")
                )

                story_server.auto_publish_story_item_thread("item-1", {})

            exporter_class.return_value.export_video.assert_called_once()
            self.assertEqual(output_path.read_bytes(), b"fresh render")

    def test_browser_autopublish_uses_container_matching_extension(self):
        repo_root = Path(__file__).resolve().parent.parent
        for page in ("index.html", "web/index.html", "AR.html"):
            with self.subTest(page=page):
                source = (repo_root / page).read_text(encoding="utf-8")
                self.assertIn("const outputExtension = mimeType.includes('mp4') ? 'mp4' : 'webm';", source)
                self.assertIn("const publishMeta = { ...meta, filename: outputFilename };", source)
                self.assertIn("const weights = chunks.map(chunk =>", source)
                self.assertNotIn("new File([videoBlob], meta.filename, { type: 'video/mp4' })", source)

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
