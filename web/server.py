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
import queue
import re
import sys
import threading
import time
from http import HTTPStatus
from http.server import HTTPServer, ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import urllib.error
import urllib.parse
import urllib.request

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from align_engine import SpeechCueAlignEngine, AlignmentResult, SpeechSegment
from duration_director import SceneDurationDirector
from deps_helper import ensure_pillow, ensure_ffmpeg
from items_manager import default_manager, parse_multipart_request, natural_sort_key
from archive_manager import ArchiveManager, get_local_ip
from port_helper import find_random_available_port, save_active_port

WEB_DIR = Path(__file__).resolve().parent
ASSETS_DIR = REPO_ROOT / "assets"
SCRIPTS_DIR = ASSETS_DIR / "scripts"
VOICE_DIR = ASSETS_DIR / "voice-over"
VISUALS_DIR = ASSETS_DIR / "visuals"
OUTPUT_DIR = ASSETS_DIR / "output"
PROCESSED_DIR = ASSETS_DIR / "processed"

default_archive = ArchiveManager(OUTPUT_DIR)


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


def get_project_assets_info():
    """Returns full metadata and content for preloading local Termux assets into Web Studio."""
    has_voice = any(VOICE_DIR.glob("*.mp3")) or any(VOICE_DIR.glob("*.wav"))
    has_script = any(SCRIPTS_DIR.glob("*.txt"))
    zip_path = VISUALS_DIR / "story_visuals.zip"
    has_visuals = zip_path.exists() or any((VISUALS_DIR / "raw_frames").glob("*.png"))

    script_file = SCRIPTS_DIR / "story.txt"
    script_text = ""
    script_lines = []
    if script_file.exists():
        try:
            with open(script_file, "r", encoding="utf-8") as f:
                script_text = f.read()
        except Exception:
            pass

    scenes = get_story_scenes()
    if scenes:
        script_lines = [s["text"] for s in scenes]
    elif script_text:
        script_lines = [l.strip() for l in script_text.splitlines() if l.strip() and not l.strip().startswith("#")]

    return {
        "has_assets": has_voice and has_script and has_visuals,
        "audio_url": "/media/audio" if has_voice else None,
        "script_url": "/media/script" if has_script else None,
        "script_text": "\n".join(script_lines) if script_lines else script_text,
        "script_raw": script_text,
        "visuals_url": "/media/visuals" if zip_path.exists() else None,
        "scene_count": len(scenes) if scenes else len(script_lines),
        "scenes": scenes
    }


def run_pipeline_thread(show_captions: bool = True, caption_style: str = "gold"):
    """Background thread function that executes the full rendering pipeline."""
    global RENDER_STATE
    with RENDER_LOCK:
        RENDER_STATE["status"] = "running"
        RENDER_STATE["progress"] = 0.0
        RENDER_STATE["message"] = "Initializing alignment engine..."
        RENDER_STATE["error"] = None
        RENDER_STATE["video_ready"] = False
        RENDER_STATE["started_at"] = time.time()
        RENDER_STATE["show_captions"] = show_captions
        RENDER_STATE["caption_style"] = caption_style

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
            progress_callback=on_render_progress,
            show_captions=show_captions,
            caption_style=caption_style
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


ITEM_RENDER_STATES = {}
ITEM_RENDER_LOCK = threading.Lock()


def render_story_item_thread(item_id: str, show_captions: bool = True, caption_style: str = "gold"):
    """Background worker that renders an item from the Items Queue using FFmpeg."""
    global ITEM_RENDER_STATES
    item = default_manager.get_item(item_id)
    if not item:
        with ITEM_RENDER_LOCK:
            ITEM_RENDER_STATES[item_id] = {
                "status": "error",
                "error": f"Story item {item_id} not found."
            }
        return

    item_folder = (default_manager.items_dir / item_id).resolve()

    # 1. Resolve Audio Path
    audio_path = None
    if item.get("audio_file"):
        cand = item_folder / item["audio_file"]
        if cand.exists() and cand.is_file():
            audio_path = cand

    if not audio_path:
        for ext in (".wav", ".mp3", ".m4a", ".aac", ".ogg"):
            found = list(item_folder.glob(f"*{ext}"))
            if found:
                audio_path = found[0]
                break

    if not audio_path:
        with ITEM_RENDER_LOCK:
            ITEM_RENDER_STATES[item_id] = {
                "status": "error",
                "error": "No voiceover audio found in story package. Generate or upload speech first."
            }
        return

    # 2. Resolve Visuals
    visuals_path = item_folder / "story_pack.zip"
    if not visuals_path.exists():
        visuals_path = item_folder

    # 3. Resolve Script
    script_path = item_folder / "script.txt"
    if not script_path.exists():
        script_text = item.get("script_text") or item.get("title") or "Story scene"
        script_path.write_text(script_text, encoding="utf-8")

    # Output filename based on item title
    raw_title = item.get("title") or item_id
    clean_slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', raw_title.lower()).strip('-')
    if not clean_slug:
        clean_slug = f"story_{item_id}"
    out_filename = f"{clean_slug}.mp4"
    output_path = OUTPUT_DIR / out_filename

    with ITEM_RENDER_LOCK:
        ITEM_RENDER_STATES[item_id] = {
            "status": "running",
            "progress": 5.0,
            "message": "Initializing speech alignment...",
            "started_at": time.time(),
            "output_filename": out_filename
        }

    default_manager.broadcast_event("render_progress", {
        "item_id": item_id,
        "progress": 5.0,
        "status": "running",
        "message": "Starting alignment..."
    })

    try:
        aligner = SpeechCueAlignEngine()
        audio_dur = aligner.get_audio_duration(audio_path)

        # Check for pre-saved scene_cuts
        scene_cuts = item.get("scene_cuts")
        story_json_path = item_folder / "story.json"
        if not scene_cuts and story_json_path.exists():
            try:
                s_json = json.loads(story_json_path.read_text(encoding="utf-8"))
                scene_cuts = s_json.get("scene_cuts")
            except Exception:
                pass

        if scene_cuts and len(scene_cuts) > 0:
            cuts = sorted([float(c) for c in scene_cuts if 0 < float(c) < audio_dur])
            time_points = [0.0] + cuts + [audio_dur]
            scenes_data = item.get("scenes") or []
            segments = []
            scene_map = {}
            for i in range(len(time_points) - 1):
                st = time_points[i]
                et = time_points[i + 1]
                txt = scenes_data[i].get("text", f"Scene {i+1}") if i < len(scenes_data) else f"Scene {i+1}"
                seg = SpeechSegment(start_time=st, end_time=et, text=txt, scene_title=f"Scene {i+1}")
                segments.append(seg)
                scene_map[i] = seg
            alignment = AlignmentResult(segments=segments, scene_mapping=scene_map, total_duration=audio_dur)
        else:
            alignment = aligner.align_speech_with_script(audio_path, script_path)

        with ITEM_RENDER_LOCK:
            ITEM_RENDER_STATES[item_id]["progress"] = 25.0
            ITEM_RENDER_STATES[item_id]["message"] = "Directing scene durations & frame mapping..."

        director = SceneDurationDirector()
        timeline = director.build_timeline(alignment, visuals_path, fps=24)

        if not ensure_pillow() or not ensure_ffmpeg():
            raise RuntimeError("Required dependencies (Pillow or FFmpeg) are missing.")

        from exporter import VideoExporter

        def on_item_render_progress(percent: float, status_msg: str):
            scaled_pct = 25.0 + (percent * 0.74)
            with ITEM_RENDER_LOCK:
                ITEM_RENDER_STATES[item_id]["progress"] = round(scaled_pct, 1)
                ITEM_RENDER_STATES[item_id]["message"] = status_msg
            default_manager.broadcast_event("render_progress", {
                "item_id": item_id,
                "progress": round(scaled_pct, 1),
                "status": "running",
                "message": status_msg
            })

        exporter = VideoExporter(fps=24)
        exporter.export_video(
            timeline=timeline,
            audio_path=audio_path,
            output_path=output_path,
            progress_callback=on_item_render_progress,
            show_captions=show_captions,
            caption_style=caption_style
        )

        # Log into local archive manifest!
        stat = output_path.stat()
        default_archive.save_video(
            video_bytes=output_path.read_bytes(),
            filename=out_filename,
            title=item.get("title") or out_filename.replace(".mp4", ""),
            caption=item.get("caption") or item.get("title") or "Story Video",
            description=item.get("description") or "#story #shorts"
        )

        with ITEM_RENDER_LOCK:
            ITEM_RENDER_STATES[item_id]["status"] = "done"
            ITEM_RENDER_STATES[item_id]["progress"] = 100.0
            ITEM_RENDER_STATES[item_id]["message"] = "Render completed successfully!"
            ITEM_RENDER_STATES[item_id]["video_url"] = f"/media/archive/{out_filename}"

        default_manager.broadcast_event("render_completed", {
            "item_id": item_id,
            "filename": out_filename,
            "video_url": f"/media/archive/{out_filename}"
        })

    except Exception as e:
        with ITEM_RENDER_LOCK:
            ITEM_RENDER_STATES[item_id]["status"] = "error"
            ITEM_RENDER_STATES[item_id]["error"] = str(e)
            ITEM_RENDER_STATES[item_id]["message"] = f"Render failed: {e}"
        default_manager.broadcast_event("render_error", {
            "item_id": item_id,
            "error": str(e)
        })


def get_dropbox_access_token(app_key: str, app_secret: str, refresh_token: str) -> str:
    """Exchange Dropbox OAuth refresh token for a short-lived access token."""
    url = "https://api.dropbox.com/oauth2/token"
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": app_key,
        "client_secret": app_secret
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=25) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["access_token"]


def upload_file_to_dropbox(access_token: str, file_path: Path, dropbox_path: str) -> Dict[str, Any]:
    """Uploads an MP4 video file to Dropbox at dropbox_path."""
    url = "https://content.dropboxapi.com/2/files/upload"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Dropbox-API-Arg": json.dumps({
            "path": dropbox_path,
            "mode": "overwrite",
            "autorename": False,
            "mute": False,
            "strict_conflict": False
        }),
        "Content-Type": "application/octet-stream"
    }
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    req = urllib.request.Request(url, data=file_bytes, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode("utf-8"))


def log_to_google_sheet(gas_url: str, filename: str, caption: str, description: str) -> Dict[str, Any]:
    """Posts story publication row to Google Sheets via Google Apps Script Web App."""
    url = f"{gas_url}?action=add&filename={urllib.parse.quote(filename)}&caption={urllib.parse.quote(caption)}&description={urllib.parse.quote(description)}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode("utf-8"))


def check_sheet_duplicate(gas_url: str, filename: str, title: str) -> bool:
    """Queries Google Sheets manifest to check if filename or story title already exists."""
    try:
        url = f"{gas_url}?action=get"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            rows = data.get("data", [])
            fn_clean = filename.lower().replace(".mp4", "")
            title_clean = title.lower()
            for r in rows:
                r_fn = str(r.get("filename", "")).lower().replace(".mp4", "")
                r_cap = str(r.get("caption", "")).lower()
                if fn_clean and (fn_clean == r_fn or fn_clean in r_fn or r_fn in fn_clean):
                    return True
                if title_clean and (title_clean in r_cap or r_cap in title_clean):
                    return True
    except Exception:
        pass
    return False


def check_dropbox_duplicate(access_token: str, dropbox_path: str) -> bool:
    """Checks if a video file already exists on Dropbox."""
    try:
        url = "https://api.dropboxapi.com/2/files/get_metadata"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = json.dumps({"path": dropbox_path}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            meta = json.loads(resp.read().decode("utf-8"))
            if meta and meta.get(".tag") == "file":
                return True
    except Exception:
        pass
    return False


def delete_file_from_dropbox(access_token: str, dropbox_path: str) -> Dict[str, Any]:
    """Permanently deletes a file from Dropbox."""
    try:
        url = "https://api.dropboxapi.com/2/files/delete_v2"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = json.dumps({"path": dropbox_path}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"ok": True, "res": json.loads(resp.read().decode("utf-8"))}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def delete_from_google_sheet(gas_url: str, filename: str) -> Dict[str, Any]:
    """Deletes a row from Google Sheets by filename via Google Apps Script."""
    try:
        url = f"{gas_url}?action=delete&filename={urllib.parse.quote(filename)}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"ok": False, "error": str(e)}


def update_google_sheet_status(gas_url: str, filename: str, platform: str, value: str) -> Dict[str, Any]:
    """Updates Facebook or YouTube publication status (YES/NO) in Google Sheets."""
    try:
        url = f"{gas_url}?action=update&filename={urllib.parse.quote(filename)}&platform={urllib.parse.quote(platform)}&value={urllib.parse.quote(value)}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"ok": False, "error": str(e)}


def auto_publish_story_item_thread(
    item_id: str,
    db_cfg: Dict[str, str],
    gas_url: str,
    show_captions: bool = True,
    caption_style: str = "gold"
):
    """
    End-to-end background publishing pipeline:
    1. Render video via upgraded FFmpeg VideoExporter
    2. Upload MP4 directly to Dropbox
    3. Log row to Google Sheets manifest
    4. Mark item as published_complete
    """
    item = default_manager.get_item(item_id)
    if not item:
        return

    item_folder = (default_manager.items_dir / item_id).resolve()
    raw_title = item.get("title") or item_id
    clean_slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', raw_title.lower()).strip('-')
    if not clean_slug:
        clean_slug = f"story_{item_id}"
    out_filename = f"{clean_slug}.mp4"
    output_path = OUTPUT_DIR / out_filename

    # Step 1: Render video
    with ITEM_RENDER_LOCK:
        ITEM_RENDER_STATES[item_id] = {
            "status": "running",
            "progress": 5.0,
            "message": "Starting video render...",
            "started_at": time.time(),
            "output_filename": out_filename
        }

    default_manager.broadcast_event("render_progress", {
        "item_id": item_id,
        "progress": 5.0,
        "status": "running",
        "message": "Starting video render..."
    })

    try:
        audio_file = item.get("audio_file") or "narration.wav"
        audio_path = item_folder / audio_file
        if not audio_path.exists():
            for ext in [".wav", ".mp3", ".m4a", ".aac"]:
                cand = list(item_folder.glob(f"*{ext}"))
                if cand:
                    audio_path = cand[0]
                    break

        if not audio_path.exists():
            raise FileNotFoundError("Voiceover audio track missing from story package.")

        aligner = SpeechCueAlignEngine()
        audio_dur = aligner.get_audio_duration(audio_path)

        scene_cuts = item.get("scene_cuts")
        story_json_path = item_folder / "story.json"
        if not scene_cuts and story_json_path.exists():
            try:
                s_json = json.loads(story_json_path.read_text(encoding="utf-8"))
                scene_cuts = s_json.get("scene_cuts")
            except Exception:
                pass

        if scene_cuts and len(scene_cuts) > 0:
            cuts = sorted([float(c) for c in scene_cuts if 0 < float(c) < audio_dur])
            time_points = [0.0] + cuts + [audio_dur]
            scenes_data = item.get("scenes") or []
            segments = []
            scene_map = {}
            for i in range(len(time_points) - 1):
                st = time_points[i]
                et = time_points[i + 1]
                txt = scenes_data[i].get("text", f"Scene {i+1}") if i < len(scenes_data) else f"Scene {i+1}"
                seg = SpeechSegment(start_time=st, end_time=et, text=txt, scene_title=f"Scene {i+1}")
                segments.append(seg)
                scene_map[i] = seg
            alignment = AlignmentResult(segments=segments, scene_mapping=scene_map, total_duration=audio_dur)
        else:
            script_path = item_folder / "script.txt"
            alignment = aligner.align_speech_with_script(audio_path, script_path)

        director = SceneDurationDirector()
        timeline = director.build_timeline(alignment, item_folder, fps=24)

        from exporter import VideoExporter
        def on_progress(percent: float, status_msg: str):
            scaled_pct = 5.0 + (percent * 0.70)  # Render is 5% -> 75%
            with ITEM_RENDER_LOCK:
                ITEM_RENDER_STATES[item_id]["progress"] = round(scaled_pct, 1)
                ITEM_RENDER_STATES[item_id]["message"] = status_msg
            default_manager.broadcast_event("render_progress", {
                "item_id": item_id,
                "progress": round(scaled_pct, 1),
                "status": "running",
                "message": status_msg
            })

        exporter = VideoExporter(fps=24)
        exporter.export_video(
            timeline=timeline,
            audio_path=audio_path,
            output_path=output_path,
            progress_callback=on_progress,
            show_captions=show_captions,
            caption_style=caption_style
        )

        # Step 2: Upload to Dropbox
        db_path = f"/Storymaker_Exports/{out_filename}"
        token = db_cfg.get("token")
        if not token and db_cfg.get("app_key") and db_cfg.get("app_secret") and db_cfg.get("refresh_token"):
            with ITEM_RENDER_LOCK:
                ITEM_RENDER_STATES[item_id]["progress"] = 78.0
                ITEM_RENDER_STATES[item_id]["message"] = "Refreshing Dropbox access token..."
            default_manager.broadcast_event("render_progress", {
                "item_id": item_id,
                "progress": 78.0,
                "status": "running",
                "message": "Refreshing Dropbox token..."
            })
            token = get_dropbox_access_token(db_cfg["app_key"], db_cfg["app_secret"], db_cfg["refresh_token"])

        if token:
            with ITEM_RENDER_LOCK:
                ITEM_RENDER_STATES[item_id]["progress"] = 82.0
                ITEM_RENDER_STATES[item_id]["message"] = f"Uploading '{out_filename}' to Dropbox..."
            default_manager.broadcast_event("render_progress", {
                "item_id": item_id,
                "progress": 82.0,
                "status": "running",
                "message": f"Uploading '{out_filename}' to Dropbox..."
            })
            upload_file_to_dropbox(token, output_path, db_path)

        # Step 3: Log to Google Sheets
        if gas_url:
            with ITEM_RENDER_LOCK:
                ITEM_RENDER_STATES[item_id]["progress"] = 94.0
                ITEM_RENDER_STATES[item_id]["message"] = "Logging row to Google Sheets manifest..."
            default_manager.broadcast_event("render_progress", {
                "item_id": item_id,
                "progress": 94.0,
                "status": "running",
                "message": "Logging to Google Sheets..."
            })
            caption = item.get("caption") or item.get("title") or "Story Video"
            description = item.get("description") or "#story #shorts"
            log_to_google_sheet(gas_url, out_filename, caption, description)

        # Step 4: Mark publish complete in catalog
        default_manager.mark_publish_complete(item_id, True)

        with ITEM_RENDER_LOCK:
            ITEM_RENDER_STATES[item_id]["status"] = "done"
            ITEM_RENDER_STATES[item_id]["progress"] = 100.0
            ITEM_RENDER_STATES[item_id]["message"] = f"✓ Successfully published {out_filename} to Dropbox & Google Sheets!"

        default_manager.broadcast_event("publish_completed", {
            "item_id": item_id,
            "filename": out_filename,
            "dropbox_path": db_path,
            "message": f"✓ Published {out_filename} to Dropbox & Google Sheets!"
        })

    except Exception as e:
        with ITEM_RENDER_LOCK:
            ITEM_RENDER_STATES[item_id]["status"] = "error"
            ITEM_RENDER_STATES[item_id]["error"] = str(e)
            ITEM_RENDER_STATES[item_id]["message"] = f"Publish failed: {e}"
        default_manager.broadcast_event("render_error", {
            "item_id": item_id,
            "error": str(e)
        })


class StorymakerRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler serving Web UI and storymaker APIs."""

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        clean_path = path.strip().lower()
        if clean_path in ("", "/", "/index.html", "/index.htm", "/ar.html", "/ar.htm", "/index", "/ar", "/web/index.html", "/web/ar.html"):
            index_path = REPO_ROOT / "index.html" if (REPO_ROOT / "index.html").is_file() else WEB_DIR / "index.html"
            self.serve_file(index_path, "text/html")
        elif path == "/api/status":
            self.send_json(get_assets_status())
        elif path == "/api/project-assets":
            self.send_json(get_project_assets_info())
        elif path == "/api/scenes":
            self.send_json({"scenes": get_story_scenes()})
        elif path == "/api/render-status":
            with RENDER_LOCK:
                self.send_json(dict(RENDER_STATE))
        elif path == "/api/settings":
            import gemini_service
            cfg = gemini_service.read_env_settings()
            self.send_json({
                "ok": True,
                "gemini_api_key": cfg.get("gemini_api_key", ""),
                "gemini_model": cfg.get("gemini_model", "gemini-2.5-flash"),
                "offline_mode": cfg.get("offline_mode", False),
                "db_app_key": cfg.get("db_app_key", ""),
                "db_app_secret": cfg.get("db_app_secret", ""),
                "db_refresh_token": cfg.get("db_refresh_token", ""),
                "db_folder": cfg.get("db_folder", "/Think with Tobi"),
                "gas_url": cfg.get("gas_url", "")
            })
        elif path == "/api/archive":
            self.send_json({
                "ok": True,
                "data": default_archive.list_archive(),
                "local_ip": get_local_ip(),
                "port": self.server.server_port
            })
        elif path.startswith("/media/archive/"):
            target_fn = path.replace("/media/archive/", "").strip("/")
            target_file = OUTPUT_DIR / target_fn
            if target_file.exists() and target_file.is_file():
                self.serve_video_range(target_file)
            else:
                self.send_error(404, "Archived video not found")
        elif path == "/api/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            q = default_manager.subscribe_events()
            initial_msg = f"event: connected\ndata: {json.dumps({'status': 'connected', 'items_count': len(default_manager.list_items())})}\n\n"
            try:
                self.wfile.write(initial_msg.encode("utf-8"))
                self.wfile.flush()
                while True:
                    try:
                        msg = q.get(timeout=15.0)
                        self.wfile.write(msg.encode("utf-8"))
                        self.wfile.flush()
                    except queue.Empty:
                        self.wfile.write(b": ping\n\n")
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, Exception):
                pass
            finally:
                default_manager.unsubscribe_events(q)
            return

        elif path.startswith("/api/items"):
            parts = [p for p in path.split("/") if p]
            # /api/items
            if len(parts) == 2:
                self.send_json(default_manager.list_items())
            # /api/items/<item_id>
            elif len(parts) == 3:
                item = default_manager.get_item(parts[2])
                if item:
                    self.send_json(item)
                else:
                    self.send_error(404, "Item not found")
            # /api/items/<item_id>/image/<img_name>
            elif len(parts) >= 5 and parts[3] == "image":
                item_id = parts[2]
                img_name = "/".join(parts[4:])
                img_path = default_manager.get_item_file_path(item_id, img_name)
                if img_path and img_path.exists():
                    ctype, _ = mimetypes.guess_type(str(img_path))
                    self.serve_file(img_path, ctype or "image/png")
                else:
                    self.send_error(404, "Image not found")
            # /api/items/<item_id>/audio
            elif len(parts) >= 4 and parts[3] == "audio":
                item_id = parts[2]
                item = default_manager.get_item(item_id)
                audio_file = item.get("audio_file") if item else None
                if audio_file:
                    audio_path = default_manager.get_item_file_path(item_id, audio_file)
                    if audio_path and audio_path.exists():
                        ctype, _ = mimetypes.guess_type(str(audio_path))
                        self.serve_file(audio_path, ctype or "audio/mpeg")
                        return
                self.send_error(404, "Audio file not found in story item")
            # /api/items/<item_id>/zip
            elif len(parts) == 4 and parts[3] == "zip":
                item_id = parts[2]
                zip_path = default_manager.get_item_file_path(item_id, "story_pack.zip")
                if zip_path and zip_path.exists():
                    self.serve_file(zip_path, "application/zip")
                else:
                    self.send_error(404, "Zip archive not found")
            # /api/items/<item_id>/render-status
            elif len(parts) >= 4 and parts[3] == "render-status":
                item_id = parts[2]
                with ITEM_RENDER_LOCK:
                    status_info = ITEM_RENDER_STATES.get(item_id, {"status": "idle", "progress": 0.0})
                self.send_json(status_info)
            else:
                self.send_error(404, "Resource not found")
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
            if not audio_file.exists():
                audio_file = VOICE_DIR / "narration.wav"
            if audio_file.exists():
                content_type = "audio/mpeg" if audio_file.suffix == ".mp3" else "audio/wav"
                self.serve_file(audio_file, content_type)
            else:
                self.send_error(404, "Audio file not found")
        elif path == "/media/script":
            script_file = SCRIPTS_DIR / "story.txt"
            if script_file.exists():
                self.serve_file(script_file, "text/plain; charset=utf-8")
            else:
                self.send_error(404, "Script file not found")
        elif path == "/media/visuals":
            zip_file = VISUALS_DIR / "story_visuals.zip"
            if zip_file.exists():
                self.serve_file(zip_file, "application/zip")
            else:
                self.send_error(404, "Visuals zip not found")
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
            content_length = int(self.headers.get("Content-Length", 0))
            show_captions = True
            caption_style = "gold"
            if content_length > 0:
                try:
                    payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                    if "show_captions" in payload:
                        show_captions = bool(payload["show_captions"])
                    if "caption_style" in payload:
                        caption_style = str(payload["caption_style"]).strip().lower()
                except Exception:
                    pass

            with RENDER_LOCK:
                if RENDER_STATE["status"] == "running":
                    self.send_json({"ok": False, "message": "A render is already in progress."}, status=409)
                    return
            thread = threading.Thread(target=run_pipeline_thread, args=(show_captions, caption_style), daemon=True)
            thread.start()
            self.send_json({"ok": True, "message": f"Render job started (captions: {'ON' if show_captions else 'OFF'}, style: {caption_style})."})

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

        elif path == "/api/save-script":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body)
                script_text = payload.get("script_text", "").strip()
                if script_text:
                    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
                    with open(SCRIPTS_DIR / "story.txt", "w", encoding="utf-8") as f:
                        f.write(script_text)
                    self.send_json({"ok": True, "message": "Script saved to assets/scripts/story.txt"})
                else:
                    self.send_json({"ok": False, "message": "No script text provided"}, status=400)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path == "/api/save-timeline":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body)
                timeline_data = payload.get("timeline")
                if timeline_data:
                    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
                    with open(PROCESSED_DIR / "timeline.json", "w", encoding="utf-8") as f:
                        json.dump(timeline_data, f, indent=2)
                    self.send_json({"ok": True, "message": "Timeline saved to assets/processed/timeline.json"})
                else:
                    self.send_json({"ok": False, "message": "No timeline data provided"}, status=400)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)
        elif path == "/api/align-speech":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                payload = {}
                if content_length > 0:
                    payload = json.loads(self.rfile.read(content_length).decode("utf-8"))

                # 1. Resolve Audio Path
                audio_path = None
                item_id = payload.get("item_id")
                if item_id:
                    item = default_manager.get_item(item_id)
                    if item and item.get("audio_file"):
                        audio_path = default_manager.get_item_file_path(item_id, item["audio_file"])
                
                if not audio_path or not audio_path.exists():
                    audio_path = VOICE_DIR / "speech.mp3"
                    if not audio_path.exists():
                        mp3_list = list(VOICE_DIR.glob("*.mp3")) + list(VOICE_DIR.glob("*.wav"))
                        if mp3_list:
                            audio_path = mp3_list[0]

                # 2. Resolve Script Text
                script_text = payload.get("script_text") or payload.get("script") or payload.get("json")
                if not script_text and item_id:
                    item = default_manager.get_item(item_id)
                    if item:
                        script_text = item.get("script_text")
                if not script_text:
                    story_file = SCRIPTS_DIR / "story.txt"
                    if story_file.exists():
                        script_text = story_file.read_text(encoding="utf-8")

                if not audio_path or not audio_path.exists():
                    self.send_json({"ok": False, "error": "No audio file available for alignment."}, status=400)
                    return
                if not script_text:
                    self.send_json({"ok": False, "error": "No script text or scenes available for alignment."}, status=400)
                    return

                engine = SpeechCueAlignEngine()
                parsed_scenes = engine.parse_script_content(script_text)
                if not parsed_scenes:
                    self.send_json({"ok": False, "error": "Could not parse any scenes from script text."}, status=400)
                    return

                total_duration = engine.get_audio_duration(audio_path)
                scene_word_counts = [max(1, len(text.split())) for _, text in parsed_scenes]
                total_words = sum(scene_word_counts)

                segments = []
                cuts = [0.0]
                current_time = 0.0

                for i, ((title, text), wc) in enumerate(zip(parsed_scenes, scene_word_counts)):
                    if i == len(parsed_scenes) - 1:
                        end_time = total_duration
                    else:
                        proportion = wc / total_words
                        duration = max(1.8, proportion * total_duration)
                        end_time = min(total_duration, current_time + duration)
                    
                    seg = {
                        "scene": i + 1,
                        "title": title,
                        "text": text,
                        "start": round(current_time, 2),
                        "end": round(end_time, 2),
                        "duration": round(end_time - current_time, 2)
                    }
                    segments.append(seg)
                    cuts.append(round(end_time, 2))
                    current_time = end_time

                self.send_json({
                    "ok": True,
                    "total_duration": round(total_duration, 2),
                    "scene_count": len(segments),
                    "scene_cuts": cuts,
                    "segments": segments
                })
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)
        elif path == "/api/upload_item":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                content_type = self.headers.get("Content-Type", "")

                zip_bytes = None
                filename = "story_pack.zip"
                title = None
                description = None
                script_text = None
                json_text = None
                replace_flag = False
                target_item_id = None

                if "multipart/form-data" in content_type:
                    fields, files = parse_multipart_request(self.headers, body)
                    title = fields.get("title")
                    description = fields.get("description")
                    script_text = fields.get("script") or fields.get("script_text")
                    json_text = fields.get("json") or fields.get("json_code") or fields.get("story_json")
                    replace_flag = fields.get("replace", "").lower() in ["true", "1", "yes"]
                    force_flag = fields.get("force", "").lower() in ["true", "1", "yes"]
                    target_item_id = fields.get("item_id") or fields.get("id") or fields.get("replace_id")

                    file_list = files.get("_list", [])
                    # Check if a zip file was provided
                    zip_candidates = [f for f in file_list if f["filename"].lower().endswith(".zip")]
                    if zip_candidates:
                        zip_bytes = zip_candidates[0]["bytes"]
                        filename = zip_candidates[0]["filename"]
                    else:
                        # Check if raw image files were provided
                        image_exts = {".png", ".jpg", ".jpeg", ".webp"}
                        img_candidates = [f for f in file_list if Path(f["filename"]).suffix.lower() in image_exts]
                        if img_candidates:
                            # Natural sort
                            img_candidates.sort(key=lambda x: natural_sort_key(x["filename"]))
                            # Duplicate check for images
                            if not replace_flag and not force_flag and not target_item_id and title:
                                existing_img_item = default_manager.find_item_by_title_or_id(title)
                                if existing_img_item:
                                    self.send_json({
                                        "ok": False,
                                        "is_duplicate": True,
                                        "item_id": existing_img_item["id"],
                                        "title": existing_img_item.get("title", title),
                                        "message": f"Duplicate detected: A story package titled '{existing_img_item.get('title', title)}' already exists. Overwrite and replace?"
                                    }, status=409)
                                    return

                            item_meta = default_manager.save_images_item(
                                images=[(f["filename"], f["bytes"]) for f in img_candidates],
                                title=title,
                                script_text=script_text or json_text,
                                description=description
                            )
                            self.send_json({
                                "ok": True,
                                "message": f"Successfully received {len(img_candidates)} images and created story package.",
                                "item": item_meta
                            })
                            return

                        file_info = files.get("file")
                        if file_info:
                            zip_bytes = file_info.get("bytes")
                            filename = file_info.get("filename") or filename

                elif "application/zip" in content_type or "application/octet-stream" in content_type:
                    zip_bytes = body
                    replace_flag = False
                    force_flag = False

                if not zip_bytes:
                    self.send_json({"ok": False, "error": "No ZIP file or image assets found in upload request."}, status=400)
                    return

                # Check if replace was requested and match existing item
                matched_item = None
                if replace_flag or target_item_id:
                    if target_item_id:
                        matched_item = default_manager.get_item(target_item_id)
                    elif title:
                        matched_item = default_manager.find_item_by_title_or_id(title)
                elif not force_flag:
                    # Duplicate check for ZIP upload: verify by title or zip stem
                    candidate_title = title or Path(filename).stem.replace("_", " ").replace("-", " ").strip()
                    if candidate_title and candidate_title.lower() != "story pack":
                        matched_item_dup = default_manager.find_item_by_title_or_id(candidate_title)
                        if matched_item_dup:
                            self.send_json({
                                "ok": False,
                                "is_duplicate": True,
                                "item_id": matched_item_dup["id"],
                                "title": matched_item_dup.get("title", candidate_title),
                                "filename": filename,
                                "message": f"Duplicate detected: A story package titled '{matched_item_dup.get('title', candidate_title)}' already exists in your Story Packages queue. Overwrite and replace it?"
                            }, status=409)
                            return

                if matched_item:
                    item_meta = default_manager.update_item(
                        item_id=matched_item["id"],
                        zip_bytes=zip_bytes,
                        filename=filename,
                        title=title,
                        description=description,
                        script_text=script_text,
                        json_text=json_text
                    )
                    self.send_json({
                        "ok": True,
                        "updated": True,
                        "replaced_id": matched_item["id"],
                        "message": f"Story package '{item_meta['title']}' ({matched_item['id']}) updated and replaced successfully.",
                        "item": item_meta
                    })
                    return

                item_meta = default_manager.save_zip_item(
                    zip_bytes,
                    filename=filename,
                    title=title,
                    description=description,
                    script_text=script_text,
                    json_text=json_text
                )
                self.send_json({
                    "ok": True,
                    "message": "Story package uploaded and unpacked successfully.",
                    "item": item_meta
                })
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path.startswith("/api/items/") and path.endswith("/update"):
            try:
                item_id = path.replace("/api/items/", "").replace("/update", "").strip("/")
                item = default_manager.get_item(item_id)
                if not item:
                    self.send_json({"ok": False, "error": f"Story package {item_id} not found to update"}, status=404)
                    return

                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                content_type = self.headers.get("Content-Type", "")

                zip_bytes = None
                filename = "story_pack.zip"
                title = None
                description = None
                script_text = None
                json_text = None

                if "multipart/form-data" in content_type:
                    fields, files = parse_multipart_request(self.headers, body)
                    title = fields.get("title")
                    description = fields.get("description")
                    script_text = fields.get("script") or fields.get("script_text")
                    json_text = fields.get("json") or fields.get("json_code") or fields.get("story_json")

                    file_list = files.get("_list", [])
                    zip_candidates = [f for f in file_list if f["filename"].lower().endswith(".zip")]
                    if zip_candidates:
                        zip_bytes = zip_candidates[0]["bytes"]
                        filename = zip_candidates[0]["filename"]
                    else:
                        file_info = files.get("file")
                        if file_info:
                            zip_bytes = file_info.get("bytes")
                            filename = file_info.get("filename") or filename

                elif "application/zip" in content_type or "application/octet-stream" in content_type:
                    zip_bytes = body

                if not zip_bytes:
                    self.send_json({"ok": False, "error": "No ZIP file found in update request. Use -F \"file=@story_pack.zip\""}, status=400)
                    return

                item_meta = default_manager.update_item(
                    item_id=item_id,
                    zip_bytes=zip_bytes,
                    filename=filename,
                    title=title,
                    description=description,
                    script_text=script_text,
                    json_text=json_text
                )

                self.send_json({
                    "ok": True,
                    "updated": True,
                    "message": f"Story package '{item_meta['title']}' ({item_id}) updated and replaced successfully.",
                    "item": item_meta
                })
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path == "/api/update_item":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                content_type = self.headers.get("Content-Type", "")

                zip_bytes = None
                filename = "story_pack.zip"
                title = None
                description = None
                script_text = None
                json_text = None
                target_item_id = None

                if "multipart/form-data" in content_type:
                    fields, files = parse_multipart_request(self.headers, body)
                    target_item_id = fields.get("item_id") or fields.get("id") or fields.get("replace_id")
                    title = fields.get("title") or fields.get("name")
                    description = fields.get("description")
                    script_text = fields.get("script") or fields.get("script_text")
                    json_text = fields.get("json") or fields.get("json_code") or fields.get("story_json")

                    file_list = files.get("_list", [])
                    zip_candidates = [f for f in file_list if f["filename"].lower().endswith(".zip")]
                    if zip_candidates:
                        zip_bytes = zip_candidates[0]["bytes"]
                        filename = zip_candidates[0]["filename"]
                    else:
                        file_info = files.get("file")
                        if file_info:
                            zip_bytes = file_info.get("bytes")
                            filename = file_info.get("filename") or filename

                elif "application/zip" in content_type or "application/octet-stream" in content_type:
                    zip_bytes = body

                if not zip_bytes:
                    self.send_json({"ok": False, "error": "No ZIP file found in update request. Use -F \"file=@story_pack.zip\""}, status=400)
                    return

                matched_item = None
                if target_item_id:
                    matched_item = default_manager.get_item(target_item_id)
                elif title:
                    matched_item = default_manager.find_item_by_title_or_id(title)

                # If still not matched, inspect ZIP for story.json title or filename stem
                if not matched_item:
                    try:
                        import zipfile, io
                        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
                            for name in zf.namelist():
                                if name.endswith(".json") and not name.endswith("index.json"):
                                    data = json.loads(zf.read(name).decode("utf-8"))
                                    t = data.get("Title") or data.get("title")
                                    if t:
                                        matched_item = default_manager.find_item_by_title_or_id(t)
                                        if matched_item:
                                            break
                    except Exception:
                        pass

                if not matched_item and filename:
                    stem = Path(filename).stem
                    if stem and stem != "story_pack":
                        matched_item = default_manager.find_item_by_title_or_id(stem)

                if matched_item:
                    item_id = matched_item["id"]
                    item_meta = default_manager.update_item(
                        item_id=item_id,
                        zip_bytes=zip_bytes,
                        filename=filename,
                        title=title,
                        description=description,
                        script_text=script_text,
                        json_text=json_text
                    )
                    self.send_json({
                        "ok": True,
                        "updated": True,
                        "replaced_id": item_id,
                        "message": f"Story package '{item_meta['title']}' ({item_id}) updated and replaced successfully.",
                        "item": item_meta
                    })
                else:
                    # Save as new item if no match found
                    item_meta = default_manager.save_zip_item(
                        zip_bytes,
                        filename=filename,
                        title=title,
                        description=description,
                        script_text=script_text,
                        json_text=json_text
                    )
                    self.send_json({
                        "ok": True,
                        "updated": False,
                        "message": f"No existing package matched; created new package '{item_meta['title']}'.",
                        "item": item_meta
                    })
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path.startswith("/api/items/") and path.endswith("/delete"):
            try:
                item_id = path.replace("/api/items/", "").replace("/delete", "").strip("/")
                success = default_manager.delete_item(item_id)
                if success:
                    self.send_json({"ok": True, "message": f"Item {item_id} deleted."})
                else:
                    self.send_json({"ok": False, "error": "Item not found"}, status=404)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path.startswith("/api/items/") and path.endswith("/save-audio"):
            try:
                item_id = path.replace("/api/items/", "").replace("/save-audio", "").strip("/")
                content_type = self.headers.get("Content-Type", "")
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)

                audio_bytes = b""
                filename = "voiceover.wav"

                if "multipart/form-data" in content_type:
                    fields, files = parse_multipart_request(self.headers, body)
                    file_info = files.get("file") or files.get("audio")
                    if not file_info:
                        self.send_json({"ok": False, "error": "No audio file provided in upload"}, status=400)
                        return
                    audio_bytes = file_info["bytes"]
                    filename = file_info.get("filename") or "voiceover.wav"
                elif "application/json" in content_type:
                    payload = json.loads(body.decode("utf-8"))
                    if "audio_base64" in payload:
                        import base64
                        audio_bytes = base64.b64decode(payload["audio_base64"])
                        filename = payload.get("filename", "voiceover.wav")
                else:
                    audio_bytes = body

                updated = default_manager.save_item_audio(item_id, audio_bytes, filename)
                if updated:
                    self.send_json({"ok": True, "item": updated, "audio_url": updated.get("audio_url")})
                else:
                    self.send_json({"ok": False, "error": f"Story item {item_id} not found"}, status=404)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path.startswith("/api/items/") and path.endswith("/save-timeline"):
            try:
                item_id = path.replace("/api/items/", "").replace("/save-timeline", "").strip("/")
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body)
                cuts = payload.get("cuts", [])
                updated = default_manager.save_item_cuts(item_id, cuts)
                if updated:
                    self.send_json({"ok": True, "item": updated})
                else:
                    self.send_json({"ok": False, "error": f"Story item {item_id} not found"}, status=404)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path.startswith("/api/items/") and path.endswith("/publish-complete"):
            try:
                item_id = path.replace("/api/items/", "").replace("/publish-complete", "").strip("/")
                content_length = int(self.headers.get("Content-Length", 0))
                payload = {}
                if content_length > 0:
                    try:
                        payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                    except Exception:
                        pass
                complete = bool(payload.get("complete", True))
                updated = default_manager.mark_publish_complete(item_id, complete)
                if updated:
                    self.send_json({
                        "ok": True,
                        "item": updated,
                        "message": f"Story package {item_id} publish_complete set to {complete}."
                    })
                else:
                    self.send_json({"ok": False, "error": f"Story item {item_id} not found"}, status=404)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path.startswith("/api/items/") and path.endswith("/render"):
            try:
                item_id = path.replace("/api/items/", "").replace("/render", "").strip("/")
                show_captions = True
                caption_style = "gold"
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length > 0:
                    try:
                        payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                        if "show_captions" in payload:
                            show_captions = bool(payload["show_captions"])
                        if "caption_style" in payload:
                            caption_style = str(payload["caption_style"]).strip().lower()
                    except Exception:
                        pass

                with ITEM_RENDER_LOCK:
                    curr = ITEM_RENDER_STATES.get(item_id, {})
                    if curr.get("status") == "running":
                        self.send_json({"ok": False, "message": "Render job already in progress for this item."}, status=409)
                        return
                    ITEM_RENDER_STATES[item_id] = {"status": "starting", "progress": 0.0}

                t = threading.Thread(target=render_story_item_thread, args=(item_id, show_captions, caption_style), daemon=True)
                t.start()
                self.send_json({"ok": True, "message": f"Background FFmpeg render started for item {item_id} (captions: {'ON' if show_captions else 'OFF'}, style: {caption_style})."})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path.startswith("/api/items/") and path.endswith("/ai-align"):
            try:
                item_id = path.replace("/api/items/", "").replace("/ai-align", "").strip("/")
                item = default_manager.get_item(item_id)
                if not item:
                    self.send_json({"ok": False, "error": f"Item {item_id} not found"}, status=404)
                    return

                item_folder = (default_manager.items_dir / item_id).resolve()
                audio_file = item.get("audio_file") or "narration.wav"
                audio_path = item_folder / audio_file
                if not audio_path.exists():
                    for ext in [".wav", ".mp3", ".m4a", ".aac"]:
                        cand = list(item_folder.glob(f"*{ext}"))
                        if cand:
                            audio_path = cand[0]
                            break

                if not audio_path.exists():
                    self.send_json({"ok": False, "error": "No voiceover audio found for this story item. Please generate or upload speech first."}, status=400)
                    return

                content_length = int(self.headers.get("Content-Length", 0))
                payload = {}
                if content_length > 0:
                    payload = json.loads(self.rfile.read(content_length).decode("utf-8"))

                api_key = payload.get("gemini_api_key")
                model = payload.get("gemini_model")

                import gemini_service
                from align_engine import SpeechCueAlignEngine
                engine = SpeechCueAlignEngine()
                duration = engine.get_audio_duration(audio_path)

                # Get scenes
                scenes = item.get("scenes") or []
                if not scenes:
                    story_json = item_folder / "story.json"
                    if story_json.exists():
                        try:
                            sdata = json.loads(story_json.read_text(encoding="utf-8"))
                            raw_sc = sdata.get("script") or sdata.get("scenes") or []
                            scenes = raw_sc if isinstance(raw_sc, list) else []
                        except Exception:
                            pass

                if not scenes and item.get("script_text"):
                    parsed = engine.parse_script_content(item["script_text"])
                    scenes = [{"text": t, "title": s} for s, t in parsed]

                res = gemini_service.align_audio_with_gemini_multimodal(
                    audio_path_or_bytes=audio_path,
                    scenes=scenes,
                    audio_duration=duration,
                    api_key=api_key,
                    model=model
                )

                if res.get("ok") and res.get("cuts"):
                    default_manager.save_item_cuts(item_id, res["cuts"])

                status_code = 200 if res.get("ok") else 400
                self.send_json(res, status=status_code)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path.startswith("/api/items/") and path.endswith("/auto-publish"):
            try:
                item_id = path.replace("/api/items/", "").replace("/auto-publish", "").strip("/")
                item = default_manager.get_item(item_id)
                if not item:
                    self.send_json({"ok": False, "error": f"Item {item_id} not found"}, status=404)
                    return

                item_folder = (default_manager.items_dir / item_id).resolve()
                audio_file = item.get("audio_file") or "narration.wav"
                audio_path = item_folder / audio_file
                if not audio_path.exists():
                    for ext in [".wav", ".mp3", ".m4a", ".aac"]:
                        cand = list(item_folder.glob(f"*{ext}"))
                        if cand:
                            audio_path = cand[0]
                            break

                if not audio_path.exists():
                    self.send_json({
                        "ok": False,
                        "code": "VOICEOVER_REQUIRED",
                        "error": "Voiceover audio is required before auto-publishing. Please record, upload, or generate voiceover audio first."
                    }, status=400)
                    return

                content_length = int(self.headers.get("Content-Length", 0))
                payload = {}
                if content_length > 0:
                    payload = json.loads(self.rfile.read(content_length).decode("utf-8"))

                force = bool(payload.get("force", False))
                gas_url = payload.get("gas_url", "").strip()
                db_app_key = payload.get("db_app_key", "").strip()
                db_app_secret = payload.get("db_app_secret", "").strip()
                db_refresh_token = payload.get("db_refresh_token", "").strip()
                db_token = payload.get("db_token", "").strip()
                show_captions = bool(payload.get("show_captions", True))
                caption_style = str(payload.get("caption_style", "gold")).strip().lower()

                raw_title = item.get("title") or item_id
                clean_slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', raw_title.lower()).strip('-')
                out_filename = f"{clean_slug}.mp4"

                # Duplicate checks if not forced
                if not force:
                    # 1. Local publish_complete tag
                    if item.get("published_complete"):
                        self.send_json({
                            "ok": False,
                            "is_duplicate": True,
                            "filename": out_filename,
                            "message": f"Story package '{raw_title}' is already marked as PUBLISH COMPLETE. Overwrite and re-publish?"
                        }, status=409)
                        return

                    # 2. Google Sheets duplicate check
                    if gas_url and check_sheet_duplicate(gas_url, out_filename, raw_title):
                        self.send_json({
                            "ok": False,
                            "is_duplicate": True,
                            "filename": out_filename,
                            "message": f"Story video '{out_filename}' already exists in your Google Sheets manifest. Overwrite and re-publish?"
                        }, status=409)
                        return

                    # 3. Dropbox duplicate check
                    if (db_token or (db_app_key and db_app_secret and db_refresh_token)):
                        try:
                            chk_token = db_token or get_dropbox_access_token(db_app_key, db_app_secret, db_refresh_token)
                            if check_dropbox_duplicate(chk_token, f"/Storymaker_Exports/{out_filename}"):
                                self.send_json({
                                    "ok": False,
                                    "is_duplicate": True,
                                    "filename": out_filename,
                                    "message": f"Video '{out_filename}' already exists on Dropbox (/Storymaker_Exports/). Overwrite and re-publish?"
                                }, status=409)
                                return
                        except Exception:
                            pass

                # Start auto-publish thread
                db_cfg = {
                    "token": db_token,
                    "app_key": db_app_key,
                    "app_secret": db_app_secret,
                    "refresh_token": db_refresh_token
                }
                t = threading.Thread(
                    target=auto_publish_story_item_thread,
                    args=(item_id, db_cfg, gas_url, show_captions, caption_style),
                    daemon=True
                )
                t.start()
                self.send_json({
                    "ok": True,
                    "message": f"Auto-publishing '{out_filename}' started in background.",
                    "filename": out_filename
                })
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path == "/api/settings":
            try:
                import gemini_service
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body)
                api_key = payload.get("gemini_api_key")
                model = payload.get("gemini_model")
                offline_mode = payload.get("offline_mode")
                db_app_key = payload.get("db_app_key")
                db_app_secret = payload.get("db_app_secret")
                db_refresh_token = payload.get("db_refresh_token")
                db_folder = payload.get("db_folder")
                gas_url = payload.get("gas_url")
                saved = gemini_service.write_env_settings(
                    api_key=api_key,
                    model=model,
                    offline_mode=offline_mode,
                    db_app_key=db_app_key,
                    db_app_secret=db_app_secret,
                    db_refresh_token=db_refresh_token,
                    db_folder=db_folder,
                    gas_url=gas_url
                )
                self.send_json({
                    "ok": True,
                    "message": "Settings saved to local .env successfully!",
                    "settings": saved
                })
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path == "/api/test-gemini":
            try:
                import gemini_service
                content_length = int(self.headers.get("Content-Length", 0))
                payload = {}
                if content_length > 0:
                    body = self.rfile.read(content_length).decode("utf-8")
                    payload = json.loads(body)
                api_key = payload.get("gemini_api_key")
                model = payload.get("gemini_model")
                res = gemini_service.test_gemini_connection(api_key=api_key, model=model)
                status_code = 200 if res.get("ok") else 400
                self.send_json(res, status=status_code)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path == "/api/gemini-align":
            try:
                import gemini_service
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body)
                transcription = payload.get("transcription", "")
                script_text = payload.get("script_text", "")
                audio_duration = float(payload.get("audio_duration", 0.0))
                scene_count = int(payload.get("scene_count", 0))
                model = payload.get("gemini_model")

                res = gemini_service.reconcile_and_align_speech(
                    transcription=transcription,
                    script_text=script_text,
                    audio_duration=audio_duration,
                    scene_count=scene_count,
                    model=model
                )
                status_code = 200 if res.get("ok") else 400
                self.send_json(res, status=status_code)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path == "/api/gemini-tts":
            try:
                import gemini_service
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body)
                script_text = payload.get("script_text", "")
                voice_name = payload.get("voice_name", "Puck")
                speed = float(payload.get("speed", 1.1))
                model = payload.get("gemini_model")
                api_key = payload.get("gemini_api_key")
                item_id = payload.get("item_id")

                res = gemini_service.generate_gemini_tts(
                    script_text=script_text,
                    voice_name=voice_name,
                    api_key=api_key,
                    model=model,
                    speed=speed
                )

                # Persist TTS audio to story package if item_id was specified
                if item_id and res.get("ok") and res.get("audio_base64"):
                    try:
                        import base64
                        audio_raw = base64.b64decode(res["audio_base64"])
                        updated_item = default_manager.save_item_audio(item_id, audio_raw, "voiceover.wav")
                        if updated_item:
                            res["item_id"] = item_id
                            res["item_audio_saved"] = True
                            res["item_audio_url"] = updated_item.get("audio_url")

                            # Automatically compute and save AI alignment cuts
                            from align_engine import SpeechCueAlignEngine
                            audio_path = default_manager.items_dir / item_id / "voiceover.wav"
                            duration = SpeechCueAlignEngine().get_audio_duration(audio_path)
                            scenes = updated_item.get("scenes") or []
                            if scenes and duration > 0:
                                align_res = gemini_service.align_audio_with_gemini_multimodal(
                                    audio_path_or_bytes=audio_path,
                                    scenes=scenes,
                                    audio_duration=duration,
                                    api_key=api_key,
                                    model=model
                                )
                                if align_res.get("ok") and align_res.get("cuts"):
                                    default_manager.save_item_cuts(item_id, align_res["cuts"])
                                    res["aligned_cuts"] = align_res["cuts"]
                    except Exception as ex:
                        pass

                status_code = 200 if res.get("ok") else 400
                self.send_json(res, status=status_code)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif re.match(r"^/api/items/([^/]+)/metadata$", path):
            try:
                m = re.match(r"^/api/items/([^/]+)/metadata$", path)
                item_id = m.group(1)
                content_length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length > 0 else {}
                res = default_manager.update_metadata(
                    item_id=item_id,
                    title=payload.get("title"),
                    caption=payload.get("caption"),
                    description=payload.get("description"),
                    fb_published=payload.get("fb_published"),
                    yt_published=payload.get("yt_published"),
                    published_complete=payload.get("published_complete"),
                    unlock=payload.get("unlock", False)
                )
                if res and "error" in res:
                    self.send_json(res, status=423)
                elif res:
                    self.send_json({"ok": True, "item": res})
                else:
                    self.send_json({"ok": False, "error": "Item not found."}, status=404)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path == "/api/schedule/delete":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length > 0 else {}
                filename = payload.get("filename", "").strip()
                gas_url = payload.get("gas_url") or os.getenv("GOOGLE_SHEET_URL", "").strip()

                if not filename:
                    self.send_json({"ok": False, "error": "Filename is required to delete schedule item."}, status=400)
                    return

                sheet_res = None
                if gas_url:
                    sheet_res = delete_from_google_sheet(gas_url, filename)

                # Delete from Dropbox
                dropbox_res = None
                app_key = payload.get("db_app_key") or os.getenv("DROPBOX_APP_KEY", "")
                app_secret = payload.get("db_app_secret") or os.getenv("DROPBOX_APP_SECRET", "")
                refresh_token = payload.get("db_refresh_token") or os.getenv("DROPBOX_REFRESH_TOKEN", "")
                folder = payload.get("db_folder") or os.getenv("DROPBOX_FOLDER", "/Think with Tobi").rstrip("/")

                if app_key and app_secret and refresh_token:
                    try:
                        token = get_dropbox_access_token(app_key, app_secret, refresh_token)
                        db_path = f"{folder}/{filename}"
                        dropbox_res = delete_file_from_dropbox(token, db_path)
                    except Exception as dex:
                        dropbox_res = {"ok": False, "error": str(dex)}

                self.send_json({
                    "ok": True,
                    "filename": filename,
                    "sheet_res": sheet_res,
                    "dropbox_res": dropbox_res,
                    "message": f"Successfully deleted '{filename}' from Google Sheets and Dropbox."
                })
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path == "/api/schedule/update_status":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(content_length).decode("utf-8")) if content_length > 0 else {}
                filename = payload.get("filename", "").strip()
                platform = payload.get("platform", "").strip().lower() # 'fb' or 'yt'
                value = payload.get("value", "").strip().upper() # 'YES' or 'NO'
                gas_url = payload.get("gas_url") or os.getenv("GOOGLE_SHEET_URL", "").strip()

                if not filename or not platform:
                    self.send_json({"ok": False, "error": "Filename and platform ('fb' or 'yt') are required."}, status=400)
                    return

                sheet_res = None
                if gas_url:
                    sheet_res = update_google_sheet_status(gas_url, filename, platform, value)

                # Also sync back to any matching local item in ItemsManager
                matched_item = None
                clean_target = filename.lower().replace(".mp4", "")
                for it in default_manager.list_items():
                    slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', (it.get("title") or it.get("id") or "").lower()).strip('-')
                    if slug == clean_target or it.get("id") == clean_target or (it.get("title") and it.get("title").lower() == clean_target):
                        is_yes = (value == "YES")
                        if platform == "fb":
                            matched_item = default_manager.update_metadata(it["id"], fb_published=is_yes)
                        elif platform == "yt":
                            matched_item = default_manager.update_metadata(it["id"], yt_published=is_yes)
                        break

                self.send_json({
                    "ok": True,
                    "filename": filename,
                    "platform": platform,
                    "value": value,
                    "sheet_res": sheet_res,
                    "matched_item": matched_item
                })
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path == "/api/gemini-ai-align":
            try:
                import gemini_service
                content_length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
                audio_base64 = payload.get("audio_base64")
                scenes = payload.get("scenes", [])
                duration = float(payload.get("audio_duration", 0.0))
                api_key = payload.get("gemini_api_key")
                model = payload.get("gemini_model")

                audio_bytes = b""
                if audio_base64:
                    import base64
                    audio_bytes = base64.b64decode(audio_base64)

                res = gemini_service.align_audio_with_gemini_multimodal(
                    audio_path_or_bytes=audio_bytes,
                    scenes=scenes,
                    audio_duration=duration,
                    api_key=api_key,
                    model=model
                )
                self.send_json(res, status=200 if res.get("ok") else 400)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path == "/api/archive/save":
            try:
                content_type = self.headers.get("Content-Type", "")
                if "multipart/form-data" in content_type:
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    fields, files = parse_multipart_request(self.headers, body)
                    file_info = files.get("file") or files.get("video")
                    if not file_info:
                        self.send_json({"ok": False, "error": "No video file uploaded"}, status=400)
                        return
                    video_bytes = file_info["bytes"]
                    filename = fields.get("filename") or file_info.get("filename") or "story_video.mp4"
                    title = fields.get("title")
                    caption = fields.get("caption")
                    description = fields.get("description")
                else:
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length).decode("utf-8")
                    payload = json.loads(body)
                    import base64
                    video_b64 = payload.get("video_base64", "")
                    video_bytes = base64.b64decode(video_b64)
                    filename = payload.get("filename", "story_video.mp4")
                    title = payload.get("title")
                    caption = payload.get("caption")
                    description = payload.get("description")

                record = default_archive.save_video(
                    video_bytes=video_bytes,
                    filename=filename,
                    title=title,
                    caption=caption,
                    description=description
                )
                self.send_json({
                    "ok": True,
                    "message": f"Saved '{record['filename']}' to local archive!",
                    "item": record
                })
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        elif path == "/api/archive/mark":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(body)
                row_index = int(payload.get("rowIndex", 0))
                platform = payload.get("platform", "")
                status = payload.get("status", "YES")
                ok = default_archive.mark_status(row_index, platform, status)
                if ok:
                    try:
                        arch_items = default_archive.list_archive()
                        target_rec = next((r for r in arch_items if r.get("rowIndex") == row_index), None)
                        if target_rec:
                            fb_done = str(target_rec.get("uploaded", "")).strip().upper() == "YES"
                            yt_done = str(target_rec.get("youtube", "")).strip().upper() == "YES"
                            is_both_done = fb_done and yt_done
                            fn = target_rec.get("filename", "").lower().replace(".mp4", "")
                            for itm in default_manager.list_items():
                                itm_title = (itm.get("title") or "").lower()
                                itm_id = itm.get("id", "").lower()
                                if (itm_id in fn) or (itm_title and (itm_title in fn or fn in itm_title)):
                                    default_manager.mark_publish_complete(itm["id"], is_both_done)
                                    break
                    except Exception:
                        pass
                self.send_json({"ok": ok})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, status=500)

        else:
            self.send_error(404, "Endpoint not found")

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/items/"):
            item_id = path.replace("/api/items/", "").strip("/")
            success = default_manager.delete_item(item_id)
            if success:
                self.send_json({"ok": True, "message": f"Item {item_id} deleted."})
            else:
                self.send_json({"ok": False, "error": "Item not found"}, status=404)
        else:
            self.send_error(404, "Endpoint not found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS, POST, DELETE")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if self.command != "HEAD":
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
            if self.command != "HEAD":
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


def start_server(host: str = "0.0.0.0", port=None, open_browser: bool = False, max_retries: int = 15):
    ThreadingHTTPServer.allow_reuse_address = True
    httpd = None
    active_port = None

    if port is not None:
        try:
            target_port = int(port)
            if target_port > 0:
                httpd = ThreadingHTTPServer((host, target_port), StorymakerRequestHandler)
                active_port = target_port
        except ValueError:
            pass
        except OSError as e:
            if e.errno in (98, 48) or "already in use" in str(e).lower():
                print(f"⚠️ Port {port} is currently in use. Selecting a random available port to prevent server overlap...")
            else:
                raise


    # If port was None, 0, or in use, randomly assign an available port
    if httpd is None:
        for _ in range(max_retries):
            p = find_random_available_port(host=host, min_port=5000, max_port=9999)
            try:
                httpd = ThreadingHTTPServer((host, p), StorymakerRequestHandler)
                active_port = p
                break
            except OSError:
                continue

    if httpd is None:
        raise RuntimeError("Could not bind server to any available port.")

    save_active_port(active_port)
    cache_buster = int(time.time())
    url = f"http://localhost:{active_port}"
    direct_url = f"http://localhost:{active_port}/?v={cache_buster}"

    print("==================================================")
    print("🎬 FB-2minutes Storymaker Web UI Server Running")
    print(f"🎲 Random Assigned Port:  {active_port}")
    print(f"👉 Direct URL (No Cache): {direct_url}")
    print(f"👉 Standard URL:          {url}")
    print(f"👉 Local Network:         http://{host}:{active_port}")
    print(f"👉 Saved port marker:     {REPO_ROOT / '.active_port'}")
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
    parser.add_argument("--port", type=int, default=None, help="Port number (default: randomly assigned)")
    parser.add_argument("--open", action="store_true", help="Automatically open browser")
    args = parser.parse_args()
    start_server(args.host, args.port, open_browser=args.open)

