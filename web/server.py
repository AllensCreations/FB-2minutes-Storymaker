"""
Local Web Server & API for FB 2minutes Storymaker
Provides a zero-dependency HTTP server with REST endpoints for:
- Asset inspection & status
- Storyboard scenes & visuals browsing
- In-browser video rendering with live progress
- Media streaming for video (with HTTP 206 partial content support) and audio
"""

import json
import mimetypes
import os
import re
import sys
import threading
import time
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from align_engine import SpeechCueAlignEngine
from duration_director import SceneDurationDirector
from deps_helper import ensure_pillow, ensure_ffmpeg

WEB_DIR = Path(__file__).resolve().parent
ASSETS_DIR = REPO_ROOT / "assets"
SCRIPTS_DIR = ASSETS_DIR / "scripts"
VOICE_DIR = ASSETS_DIR / "voice-over"
VISUALS_DIR = ASSETS_DIR / "visuals"
OUTPUT_DIR = ASSETS_DIR / "output"
PROCESSED_DIR = ASSETS_DIR / "processed"


# Global rendering state tracker
RENDER_STATE = {
    "status": "idle",       # idle | running | done | error
    "progress": 0.0,
    "message": "Ready to generate.",
    "current_frame": 0,
    "total_frames": 0,
    "elapsed_sec": 0.0,
    "eta_sec": 0.0,
    "error": None,
    "video_ready": False,
    "started_at": 0.0
}
RENDER_LOCK = threading.Lock()


def get_assets_status():
    """Check existence and metadata of required assets."""
    has_voice = any(VOICE_DIR.glob("*.mp3")) or any(VOICE_DIR.glob("*.wav"))
    has_script = any(SCRIPTS_DIR.glob("*.txt"))
    has_visuals = any(VISUALS_DIR.glob("*.zip")) or any((VISUALS_DIR / "raw_frames").glob("*.png"))
    has_video = (OUTPUT_DIR / "final_story.mp4").exists()

    video_stat = None
    if has_video:
        vp = OUTPUT_DIR / "final_story.mp4"
        video_stat = {
            "size_bytes": vp.stat().st_size,
            "size_mb": round(vp.stat().st_size / (1024 * 1024), 2),
            "modified": vp.stat().st_mtime
        }

    return {
        "voice_over": {"found": has_voice, "path": "assets/voice-over/narration.mp3"},
        "script": {"found": has_script, "path": "assets/scripts/story.txt"},
        "visuals": {"found": has_visuals, "path": "assets/visuals/story_visuals.zip"},
        "video": {"found": has_video, "path": "assets/output/final_story.mp4", "details": video_stat}
    }


def get_story_scenes():
    """Extract structured story scenes and their paired visual assets."""
    script_file = SCRIPTS_DIR / "story.txt"
    if not script_file.exists():
        return []

    with open(script_file, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"\[(Scene\s*[^\]]+)\]\s*\n([^\[]+)", re.MULTILINE)
    matches = pattern.findall(content)

    scenes = []
    for idx, (title, text) in enumerate(matches):
        img_name = f"scene_{idx + 1}.png"
        img_file = VISUALS_DIR / "raw_frames" / img_name
        scenes.append({
            "index": idx,
            "title": title.strip(),
            "text": " ".join(text.strip().split()),
            "image_exists": img_file.exists(),
            "thumbnail_url": f"/media/thumbnail?scene={idx + 1}"
        })
    return scenes


def run_pipeline_thread():
    """Background thread function that executes the full rendering pipeline."""
    global RENDER_STATE
    with RENDER_LOCK:
        RENDER_STATE["status"] = "running"
        RENDER_STATE["progress"] = 0.0
        RENDER_STATE["message"] = "Initializing alignment engine..."
        RENDER_STATE["error"] = None
        RENDER_STATE["video_ready"] = False
        RENDER_STATE["started_at"] = time.time()

    try:
        audio_path = VOICE_DIR / "narration.mp3"
        script_path = SCRIPTS_DIR / "story.txt"
        visuals_path = VISUALS_DIR / "story_visuals.zip"
        output_path = OUTPUT_DIR / "final_story.mp4"

        # 1. Speech Cue Alignment
        with RENDER_LOCK:
            RENDER_STATE["progress"] = 10.0
            RENDER_STATE["message"] = "Analyzing voice audio and script timing..."

        aligner = SpeechCueAlignEngine()
        alignment = aligner.align_speech_with_script(audio_path, script_path)
        aligner.export_alignment(alignment, PROCESSED_DIR / "alignment.txt")

        # 2. Scene Duration Director
        with RENDER_LOCK:
            RENDER_STATE["progress"] = 25.0
            RENDER_STATE["message"] = "Directing scene durations and visual asset mapping..."

        director = SceneDurationDirector()
        timeline = director.build_timeline(alignment, visuals_path, fps=24)
        director.export_timeline(timeline, PROCESSED_DIR / "timeline.json")

        # 3. Visual Choreography & Exporter
        if not ensure_pillow() or not ensure_ffmpeg():
            raise RuntimeError("Required dependencies (Pillow or FFmpeg) are missing.")

        from exporter import VideoExporter

        def on_render_progress(percent: float, status_msg: str):
            with RENDER_LOCK:
                scaled_pct = 25.0 + (percent * 0.74)
                RENDER_STATE["progress"] = round(scaled_pct, 1)
                RENDER_STATE["message"] = status_msg
                RENDER_STATE["elapsed_sec"] = round(time.time() - RENDER_STATE["started_at"], 1)

        exporter = VideoExporter(fps=24)
        exporter.export_video(
            timeline=timeline,
            audio_path=audio_path,
            output_path=output_path,
            progress_callback=on_render_progress
        )

        with RENDER_LOCK:
            RENDER_STATE["status"] = "done"
            RENDER_STATE["progress"] = 100.0
            RENDER_STATE["message"] = "Render completed successfully!"
            RENDER_STATE["video_ready"] = True
            RENDER_STATE["elapsed_sec"] = round(time.time() - RENDER_STATE["started_at"], 1)

    except Exception as e:
        with RENDER_LOCK:
            RENDER_STATE["status"] = "error"
            RENDER_STATE["error"] = str(e)
            RENDER_STATE["message"] = f"Render failed: {e}"


class StorymakerRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler serving Web UI and storymaker APIs."""

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        clean_path = path.strip().lower()
        if clean_path in ("", "/", "/index.html", "/index.htm", "/ar.html", "/ar.htm", "/index", "/ar", "/web/index.html", "/web/ar.html"):
            self.serve_file(WEB_DIR / "index.html", "text/html")
        elif path == "/api/status":
            self.send_json(get_assets_status())
        elif path == "/api/scenes":
            self.send_json({"scenes": get_story_scenes()})
        elif path == "/api/render-status":
            with RENDER_LOCK:
                self.send_json(dict(RENDER_STATE))
        elif path == "/media/thumbnail":
            params = parse_qs(parsed.query)
            scene_num = params.get("scene", ["1"])[0]
            thumb_path = VISUALS_DIR / "raw_frames" / f"scene_{scene_num}.png"
            if thumb_path.exists():
                self.serve_file(thumb_path, "image/png")
            else:
                self.send_error(404, "Thumbnail not found")
        elif path == "/media/audio":
            audio_file = VOICE_DIR / "narration.mp3"
            if audio_file.exists():
                self.serve_file(audio_file, "audio/mpeg")
            else:
                self.send_error(404, "Audio file not found")
        elif path == "/media/video":
            video_file = OUTPUT_DIR / "final_story.mp4"
            if video_file.exists():
                self.serve_video_range(video_file)
            else:
                self.send_error(404, "Rendered video not found")
        else:
            # Fallback to static files in web/
            candidate = (WEB_DIR / path.lstrip("/")).resolve()
            if candidate.exists() and candidate.is_file() and str(candidate).startswith(str(WEB_DIR)):
                content_type, _ = mimetypes.guess_type(str(candidate))
                self.serve_file(candidate, content_type or "application/octet-stream")
            else:
                self.send_error(404, "File not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/render":
            global RENDER_STATE
            with RENDER_LOCK:
                if RENDER_STATE["status"] == "running":
                    self.send_json({"ok": False, "message": "A render is already in progress."}, status=409)
                    return
            thread = threading.Thread(target=run_pipeline_thread, daemon=True)
            thread.start()
            self.send_json({"ok": True, "message": "Render job started."})

        elif path == "/api/generate-assets":
            try:
                gen_script = REPO_ROOT / "scripts" / "generate_sample_assets.py"
                import importlib.util
                spec = importlib.util.spec_from_file_location("gen_assets", gen_script)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    mod.generate_all_sample_assets()
                self.send_json({"ok": True, "message": "Sample assets refreshed."})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)
        else:
            self.send_error(404, "Endpoint not found")

    def send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, file_path: Path, content_type: str):
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def serve_video_range(self, file_path: Path):
        """Supports HTTP 206 Partial Content for streaming/scrubbing in HTML5 video."""
        file_size = file_path.stat().st_size
        range_header = self.headers.get("Range")

        if not range_header:
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.copyfile(f, self.wfile)
            return

        # Parse range header: e.g. "bytes=0-1024"
        try:
            bytes_range = range_header.strip().split("=")[1]
            start_str, end_str = bytes_range.split("-")
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
            if end >= file_size:
                end = file_size - 1
            length = end - start + 1

            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.end_headers()

            with open(file_path, "rb") as f:
                f.seek(start)
                bytes_to_send = length
                chunk_size = 64 * 1024
                while bytes_to_send > 0:
                    read_len = min(bytes_to_send, chunk_size)
                    chunk = f.read(read_len)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    bytes_to_send -= len(chunk)
        except Exception:
            pass


def start_server(host: str = "0.0.0.0", port: int = 8000, open_browser: bool = False, max_retries: int = 10):
    HTTPServer.allow_reuse_address = True
    httpd = None
    active_port = port

    for p in range(port, port + max_retries):
        try:
            httpd = HTTPServer((host, p), StorymakerRequestHandler)
            active_port = p
            break
        except OSError as e:
            if e.errno in (98, 48) or "already in use" in str(e).lower():
                print(f"⚠️ Port {p} is currently in use. Trying port {p + 1}...")
                continue
            raise

    if httpd is None:
        raise RuntimeError(f"Could not bind server to any port from {port} to {port + max_retries - 1}")

    cache_buster = int(time.time())
    url = f"http://localhost:{active_port}"
    direct_url = f"http://localhost:{active_port}/?v={cache_buster}"

    print("==================================================")
    print(f"🎬 FB-2minutes Storymaker Web UI Server Running")
    print(f"👉 Direct URL (No Cache): {direct_url}")
    print(f"👉 Standard URL:          {url}")
    print(f"👉 Local Network:         http://{host}:{active_port}")
    print("==================================================")

    if open_browser:
        def _open():
            time.sleep(0.3)
            try:
                from termux_ui import open_url_in_browser
                open_url_in_browser(direct_url)
            except Exception:
                pass
        threading.Thread(target=_open, daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Web server...")
        httpd.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FB 2minutes Storymaker Web UI Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--open", action="store_true", help="Automatically open browser")
    args = parser.parse_args()
    start_server(args.host, args.port, open_browser=args.open)
