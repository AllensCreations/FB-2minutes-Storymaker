"""
Items Queue Manager for FB-2minutes Storymaker
----------------------------------------------
Handles incoming story packages (ZIP archives) from Google AI Studio / APIs:
- Unpacks & indexes story packages in assets/items/<item_id>/
- Extracts script text / JSON and visual scene frames
- Manages metadata catalog (assets/items/index.json)
- Dispatches real-time Server-Sent Events (SSE) to connected web clients
"""

import io
import json
import os
import queue
import re
import shutil
import threading
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ITEMS_DIR = REPO_ROOT / "assets" / "items"


def natural_sort_key(s: str):
    """Sort strings containing numbers naturally (e.g. 1.png, 2.png, 10.png)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", str(s))]


def parse_multipart_request(headers: Any, body: bytes) -> Tuple[Dict[str, str], Dict[str, Any]]:
    """Zero-dependency multipart/form-data parser for file uploads."""
    content_type = headers.get("Content-Type", "")
    if "boundary=" not in content_type:
        return {}, {}
    
    boundary_str = content_type.split("boundary=")[1].split(";")[0].strip().strip('"\'')
    boundary = boundary_str.encode("utf-8")
    
    parts = body.split(b"--" + boundary)
    fields: Dict[str, str] = {}
    files: Dict[str, Any] = {}
    file_list: List[Dict[str, Any]] = []
    
    for part in parts:
        if not part or part == b"--\r\n" or part.startswith(b"--"):
            continue
        header_end = part.find(b"\r\n\r\n")
        if header_end == -1:
            continue
        header_bytes = part[:header_end]
        content = part[header_end + 4:]
        if content.endswith(b"\r\n"):
            content = content[:-2]
            
        header_text = header_bytes.decode("utf-8", errors="replace")
        if "filename=" in header_text:
            fname = header_text.split("filename=")[1].split(";")[0].split("\r\n")[0].strip('"\' ')
            file_entry = {"filename": fname, "bytes": content}
            file_list.append(file_entry)
            if "file" not in files:
                files["file"] = file_entry
            files[f"file_{len(file_list)-1}"] = file_entry
        elif "name=" in header_text:
            name = header_text.split("name=")[1].split(";")[0].split("\r\n")[0].strip('"\' ')
            fields[name] = content.decode("utf-8", errors="replace")
            
    files["_list"] = file_list
    return fields, files


class ItemsManager:
    """Thread-safe manager for story items queue with real-time SSE broadcasting."""

    def __init__(self, items_dir: Optional[Path] = None):
        self.items_dir = Path(items_dir) if items_dir else DEFAULT_ITEMS_DIR
        self.items_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.items_dir / "index.json"
        self._lock = threading.Lock()
        self._subscribers: List[queue.Queue] = []
        self._ensure_index()

    def _ensure_index(self):
        with self._lock:
            if not self.index_file.exists():
                self._write_index([])

    def _read_index(self) -> List[Dict[str, Any]]:
        if not self.index_file.exists():
            return []
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_index(self, items: List[Dict[str, Any]]):
        temp_file = self.items_dir / "index.json.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        temp_file.replace(self.index_file)

    def subscribe_events(self) -> queue.Queue:
        """Register an SSE subscriber queue."""
        q = queue.Queue(maxsize=50)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe_events(self, q: queue.Queue):
        """Unregister an SSE subscriber queue."""
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    def broadcast_event(self, event_type: str, data: Any):
        """Send an SSE event payload to all active subscriber queues."""
        msg = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        with self._lock:
            dead = []
            for q in self._subscribers:
                try:
                    q.put_nowait(msg)
                except queue.Full:
                    dead.append(q)
            for d in dead:
                self._subscribers.remove(d)

    def list_items(self) -> List[Dict[str, Any]]:
        """Return all stories in the items queue, newest first."""
        with self._lock:
            items = self._read_index()
            # Verify directories still exist on disk
            valid = []
            changed = False
            for item in items:
                item_folder = self.items_dir / item["id"]
                if item_folder.exists() and item_folder.is_dir():
                    valid.append(item)
                else:
                    changed = True
            if changed:
                self._write_index(valid)
            return valid

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full details of a specific story item."""
        with self._lock:
            for item in self._read_index():
                if item["id"] == item_id:
                    return item
        return None

    def get_item_file_path(self, item_id: str, filename: str) -> Optional[Path]:
        """Safely resolve an asset file inside an item folder."""
        item_folder = (self.items_dir / item_id).resolve()
        if not item_folder.exists():
            return None
        target = (item_folder / filename).resolve()
        if str(target).startswith(str(item_folder)) and target.exists() and target.is_file():
            return target
        return None

    def save_zip_item(
        self,
        zip_bytes: bytes,
        filename: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        script_text: Optional[str] = None,
        json_text: Optional[str] = None,
        existing_item_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Unpack a ZIP archive, extract script and images, index the item, and broadcast SSE.
        Auto-generates scene splits and script text if no story.json or script.txt is provided,
        or accepts explicit pasted json_text / script_text.
        If existing_item_id is provided, updates and replaces that package in-place.
        """
        is_update = bool(existing_item_id)
        if is_update:
            item_id = existing_item_id
        else:
            timestamp = int(time.time())
            item_id = f"item_{timestamp}_{os.urandom(3).hex()}"

        item_folder = self.items_dir / item_id

        # Preserve existing voiceover audio and cuts if updating and new zip doesn't have audio
        old_audio_name = None
        old_audio_bytes = None
        old_cuts = None
        if is_update and item_folder.exists():
            existing_meta = self.get_item(item_id)
            if existing_meta:
                old_cuts = existing_meta.get("scene_cuts")
            for ext in [".wav", ".mp3", ".m4a", ".aac", ".ogg"]:
                cands = list(item_folder.glob(f"*{ext}"))
                if cands:
                    old_audio_name = cands[0].name
                    old_audio_bytes = cands[0].read_bytes()
                    break
            # Remove previous content so old visual files are cleanly replaced
            for p in list(item_folder.glob("*")):
                if p.is_file():
                    p.unlink()
                elif p.is_dir():
                    shutil.rmtree(p)

        item_folder.mkdir(parents=True, exist_ok=True)

        # 1. Unpack ZIP safely (guard against zip-slip)
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
            for member in zf.infolist():
                # Ignore directories or path traversal
                target_path = (item_folder / member.filename).resolve()
                if not str(target_path).startswith(str(item_folder.resolve())):
                    continue
                if member.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src, open(target_path, "wb") as dst:
                        shutil.copyfileobj(src, dst)

        # Also save the original zip for convenience / backup
        (item_folder / "story_pack.zip").write_bytes(zip_bytes)

        # 2. Discover Images
        image_extensions = {".png", ".jpg", ".jpeg", ".webp"}
        image_files = []
        for p in item_folder.rglob("*"):
            if p.is_file() and p.suffix.lower() in image_extensions:
                rel = p.relative_to(item_folder)
                image_files.append(str(rel))

        image_files.sort(key=natural_sort_key)

        # 2b. Discover Audio
        audio_extensions = {".mp3", ".wav", ".m4a", ".aac", ".ogg"}
        audio_files = []
        for p in item_folder.rglob("*"):
            if p.is_file() and p.suffix.lower() in audio_extensions:
                rel = p.relative_to(item_folder)
                audio_files.append(str(rel))
        audio_files.sort(key=natural_sort_key)

        # Restore preserved voice-over if new ZIP did not include any audio
        if not audio_files and old_audio_bytes and old_audio_name:
            restored_path = item_folder / old_audio_name
            restored_path.write_bytes(old_audio_bytes)
            audio_files.append(old_audio_name)

        item_audio = audio_files[0] if audio_files else None

        # 3. Discover & Parse Script / story.json
        meta_title = title or (filename.replace(".zip", "") if filename else "Untitled Story")
        meta_desc = description or ""
        meta_caption = ""
        meta_aspect_ratio = ""
        parsed_script_text = script_text or ""
        scenes_data = []
        parsed_json = False

        # Helper to extract metadata and scenes from arbitrary dict
        def parse_story_dict(data_dict: Dict[str, Any]):
            nonlocal meta_title, meta_desc, meta_caption, meta_aspect_ratio, scenes_data, parsed_json
            if not isinstance(data_dict, dict):
                return
            meta_title = title or data_dict.get("Title") or data_dict.get("title", meta_title)
            meta_caption = data_dict.get("Caption") or data_dict.get("caption", meta_caption)
            meta_desc = description or data_dict.get("Description") or data_dict.get("description", meta_desc)
            raw_list = data_dict.get("script") or data_dict.get("scenes") or data_dict.get("story") or data_dict.get("Script") or data_dict.get("Scenes")
            if isinstance(raw_list, list):
                scenes_data = raw_list
                parsed_json = True
                # Check aspect ratio
                for item in raw_list:
                    if isinstance(item, dict) and (item.get("aspect_ratio") or item.get("aspectRatio")):
                        meta_aspect_ratio = item.get("aspect_ratio") or item.get("aspectRatio")
                        break

        # If explicit json_text was passed (e.g. from pasted JSON in UI)
        if json_text and json_text.strip():
            try:
                data = json.loads(json_text.strip())
                if isinstance(data, dict):
                    parse_story_dict(data)
                elif isinstance(data, list):
                    scenes_data = data
                    parsed_json = True
                (item_folder / "story.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception:
                # If not valid JSON, treat as raw script text
                if not parsed_script_text:
                    parsed_script_text = json_text.strip()

        # If not already parsed from passed json_text, check for story.json inside ZIP
        if not parsed_json:
            json_candidates = list(item_folder.glob("*.json"))
            json_candidates = [j for j in json_candidates if j.name != "index.json"]
            for jpath in json_candidates:
                try:
                    data = json.loads(jpath.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        parse_story_dict(data)
                        if parsed_json:
                            break
                    elif isinstance(data, list):
                        scenes_data = data
                        parsed_json = True
                        break
                except Exception:
                    pass

        # Check for script.txt or text files if not passed or parsed
        if not parsed_script_text:
            txt_candidates = list(item_folder.glob("*.txt"))
            for tpath in txt_candidates:
                try:
                    parsed_script_text = tpath.read_text(encoding="utf-8")
                    break
                except Exception:
                    pass

        script_text = parsed_script_text

        # If we have scenes_data but no script_text, build clean script_text without scene numbers
        if scenes_data and not script_text:
            parts = []
            for idx, s in enumerate(scenes_data):
                if isinstance(s, dict):
                    txt = s.get("narration") or s.get("text") or s.get("script") or s.get("caption") or ""
                else:
                    txt = str(s)
                clean_txt = re.sub(r"^(?:\[?\s*Scene\s*\d+\s*[\:\]\-\.]*\s*)", "", str(txt or ""), flags=re.IGNORECASE).strip()
                parts.append(clean_txt if clean_txt else str(txt))
            script_text = "\n(Next image)\n".join(parts)

        # If we have script_text but no scenes_data, parse scenes from text
        if script_text and not scenes_data:
            if "(Next image)" in script_text:
                chunks = script_text.split("(Next image)")
            elif "Scene " in script_text:
                chunks = re.split(r"\[?Scene\s*\d+[^\]\n]*\]?", script_text)
            else:
                chunks = [l for l in script_text.splitlines() if l.strip()]

            chunks = [c.strip() for c in chunks if c.strip()]
            for idx, c in enumerate(chunks):
                clean_c = re.sub(r"^(?:\[?\s*Scene\s*\d+\s*[\:\]\-\.]*\s*)", "", str(c or ""), flags=re.IGNORECASE).strip()
                scenes_data.append({
                    "text": clean_c if clean_c else str(c)
                })

        # If we have images but neither story.json nor script.txt was provided (image-only upload):
        if not scenes_data and not script_text and image_files:
            parts = []
            for idx, img_rel in enumerate(image_files):
                clean_name = Path(img_rel).stem.replace("_", " ").replace("-", " ").title()
                scene_label = f"Scene {idx + 1}"
                scenes_data.append({
                    "scene": idx + 1,
                    "text": scene_label,
                    "image": img_rel
                })
                parts.append(f"{scene_label}: {clean_name}")
            script_text = "\n(Next image)\n".join(parts)

        scene_count = max(len(image_files), len(scenes_data), 1)

        # First image is thumbnail
        thumbnail_img = image_files[0] if image_files else None

        item_meta = {
            "id": item_id,
            "title": meta_title,
            "caption": meta_caption,
            "description": meta_desc,
            "aspect_ratio": meta_aspect_ratio,
            "scene_count": scene_count,
            "thumbnail_url": f"/api/items/{item_id}/image/{thumbnail_img}" if thumbnail_img else None,
            "audio_status": "ready" if item_audio else "pending",
            "audio_file": item_audio,
            "audio_url": f"/api/items/{item_id}/audio" if item_audio else None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "images": image_files,
            "script_text": script_text,
            "scenes": scenes_data,
            "zip_url": f"/api/items/{item_id}/zip",
            "published_complete": False,
            "fb_published": False,
            "yt_published": False
        }

        with self._lock:
            items = self._read_index()
            found_idx = None
            if is_update:
                for idx, it in enumerate(items):
                    if it.get("id") == item_id:
                        found_idx = idx
                        break

            if found_idx is not None:
                if items[found_idx].get("created_at"):
                    item_meta["created_at"] = items[found_idx]["created_at"]
                if items[found_idx].get("published_complete") is not None:
                    item_meta["published_complete"] = items[found_idx]["published_complete"]
                if items[found_idx].get("fb_published") is not None:
                    item_meta["fb_published"] = items[found_idx]["fb_published"]
                if items[found_idx].get("yt_published") is not None:
                    item_meta["yt_published"] = items[found_idx]["yt_published"]
                if old_cuts and len(old_cuts) == len(scenes_data) + 1:
                    item_meta["scene_cuts"] = old_cuts
                item_meta["updated_at"] = datetime.now(timezone.utc).isoformat()
                items[found_idx] = item_meta
            else:
                items.insert(0, item_meta)
            self._write_index(items)

        # 4. Broadcast live notification via SSE
        event_type = "item_updated" if (is_update and found_idx is not None) else "item_added"
        self.broadcast_event(event_type, item_meta)

        return item_meta

    def update_item(
        self,
        item_id: str,
        zip_bytes: bytes,
        filename: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        script_text: Optional[str] = None,
        json_text: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update and replace an existing story package in-place."""
        existing = self.get_item(item_id)
        if not existing:
            return None
        return self.save_zip_item(
            zip_bytes=zip_bytes,
            filename=filename,
            title=title,
            description=description,
            script_text=script_text,
            json_text=json_text,
            existing_item_id=item_id
        )

    def find_item_by_title_or_id(self, query: str) -> Optional[Dict[str, Any]]:
        """Look up an existing story item by ID, exact title, or slugified title."""
        if not query:
            return None
        q = str(query).strip().lower()
        q_slug = re.sub(r"[^a-z0-9]+", "", q)
        with self._lock:
            for item in self._read_index():
                if item.get("id") == query or item.get("id", "").lower() == q:
                    return item
                title = (item.get("title") or "").strip().lower()
                if title == q:
                    return item
                title_slug = re.sub(r"[^a-z0-9]+", "", title)
                if q_slug and title_slug == q_slug:
                    return item
        return None

    def save_images_item(
        self,
        images: List[Tuple[str, bytes]],
        title: Optional[str] = None,
        script_text: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a story package directly from raw image bytes, auto-generating
        a ZIP package and scene timeline splits without requiring a pre-made JSON.
        """
        buf = io.BytesIO()
        pkg_title = title or "AI Generated Story"
        pkg_desc = description or f"Story package with {len(images)} images."

        # Natural sort images by filename
        sorted_images = sorted(images, key=lambda x: natural_sort_key(x[0]))

        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            scenes = []
            script_parts = []

            # If script_text provided, parse chunks
            script_chunks = []
            if script_text:
                if "(Next image)" in script_text:
                    script_chunks = [c.strip() for c in script_text.split("(Next image)") if c.strip()]
                else:
                    script_chunks = [c.strip() for c in script_text.splitlines() if c.strip()]

            for idx, (img_name, img_bytes) in enumerate(sorted_images):
                zf.writestr(img_name, img_bytes)
                text = script_chunks[idx] if idx < len(script_chunks) else f"Scene {idx + 1}"
                scenes.append({
                    "scene": idx + 1,
                    "text": text,
                    "image": img_name
                })
                script_parts.append(f"Scene {idx + 1}: {text}")

            story_meta = {
                "title": pkg_title,
                "description": pkg_desc,
                "scenes": scenes
            }
            zf.writestr("story.json", json.dumps(story_meta, indent=2))
            full_script = script_text if script_text else "\n(Next image)\n".join(script_parts)
            zf.writestr("script.txt", full_script)

        return self.save_zip_item(
            buf.getvalue(),
            filename=f"{pkg_title}.zip",
            title=pkg_title,
            description=pkg_desc
        )

    def save_item_audio(self, item_id: str, audio_bytes: bytes, filename: str = "voiceover.wav") -> Optional[Dict[str, Any]]:
        """Save synthesized or uploaded audio into an existing story item and update index."""
        with self._lock:
            items = self._read_index()
            target = next((it for it in items if it["id"] == item_id), None)
            if not target:
                return None

            item_folder = (self.items_dir / item_id).resolve()
            if not item_folder.exists() or not item_folder.is_dir():
                return None

            # Write audio file
            audio_path = item_folder / filename
            audio_path.write_bytes(audio_bytes)

            # Update item metadata in index
            target["audio_file"] = filename
            target["audio_url"] = f"/api/items/{item_id}/audio"
            target["audio_status"] = "ready"

            # Also update story.json if it exists inside the item folder
            story_json_path = item_folder / "story.json"
            if story_json_path.exists():
                try:
                    s_data = json.loads(story_json_path.read_text(encoding="utf-8"))
                    s_data["audio_file"] = filename
                    story_json_path.write_text(json.dumps(s_data, indent=2, ensure_ascii=False), encoding="utf-8")
                except Exception:
                    pass

            self._write_index(items)

        # Broadcast SSE update
        self.broadcast_event("item_updated", target)
        return target

    def save_item_cuts(self, item_id: str, scene_cuts: List[float]) -> Optional[Dict[str, Any]]:
        """Save aligned cut timestamps into story item."""
        with self._lock:
            items = self._read_index()
            target = next((it for it in items if it["id"] == item_id), None)
            if not target:
                return None

            item_folder = (self.items_dir / item_id).resolve()
            if not item_folder.exists() or not item_folder.is_dir():
                return None

            target["scene_cuts"] = scene_cuts

            story_json_path = item_folder / "story.json"
            if story_json_path.exists():
                try:
                    s_data = json.loads(story_json_path.read_text(encoding="utf-8"))
                    s_data["scene_cuts"] = scene_cuts
                    story_json_path.write_text(json.dumps(s_data, indent=2, ensure_ascii=False), encoding="utf-8")
                except Exception:
                    pass

            self._write_index(items)

        self.broadcast_event("item_updated", target)
        return target

    def mark_publish_complete(self, item_id: str, complete: bool = True) -> Optional[Dict[str, Any]]:
        """Mark an item as PUBLISH COMPLETE or revert."""
        with self._lock:
            items = self._read_index()
            target = next((it for it in items if it["id"] == item_id), None)
            if not target:
                return None

            target["published_complete"] = bool(complete)

            item_folder = (self.items_dir / item_id).resolve()
            if item_folder.exists() and item_folder.is_dir():
                story_json_path = item_folder / "story.json"
                if story_json_path.exists():
                    try:
                        s_data = json.loads(story_json_path.read_text(encoding="utf-8"))
                        s_data["published_complete"] = bool(complete)
                        story_json_path.write_text(json.dumps(s_data, indent=2, ensure_ascii=False), encoding="utf-8")
                    except Exception:
                        pass

            self._write_index(items)

        self.broadcast_event("item_updated", target)
        return target

    def update_metadata(
        self,
        item_id: str,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        description: Optional[str] = None,
        fb_published: Optional[bool] = None,
        yt_published: Optional[bool] = None,
        published_complete: Optional[bool] = None,
        unlock: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Update story title, caption, description and social published status with edit locking."""
        with self._lock:
            items = self._read_index()
            target = None
            for item in items:
                if item.get("id") == item_id:
                    # Enforce social edit lock rule:
                    # If fb_published or yt_published is true, lock editing of title/caption/description unless unlocking
                    is_social_locked = (item.get("fb_published") is True or item.get("yt_published") is True) and not unlock
                    if is_social_locked and (title is not None or caption is not None or description is not None):
                        return {
                            "error": "LOCKED: Story is already published on Facebook or YouTube and cannot be edited.",
                            "locked": True,
                            "item": item
                        }

                    if title is not None:
                        item["title"] = str(title).strip()
                    if caption is not None:
                        item["caption"] = str(caption).strip()
                    if description is not None:
                        item["description"] = str(description).strip()
                    if fb_published is not None:
                        item["fb_published"] = bool(fb_published)
                    if yt_published is not None:
                        item["yt_published"] = bool(yt_published)
                    if published_complete is not None:
                        item["published_complete"] = bool(published_complete)

                    item["updated_at"] = datetime.now(timezone.utc).isoformat()
                    target = dict(item)
                    break

            if target:
                self._write_index(items)

        if target and "error" not in target:
            # Sync to disk story.json if present
            try:
                story_json_path = self.items_dir / item_id / "story.json"
                data = {}
                if story_json_path.exists():
                    try:
                        data = json.loads(story_json_path.read_text(encoding="utf-8"))
                    except Exception:
                        data = {}
                if title is not None:
                    data["title"] = target.get("title", "")
                if caption is not None:
                    data["caption"] = target.get("caption", "")
                if description is not None:
                    data["description"] = target.get("description", "")
                if fb_published is not None:
                    data["fb_published"] = target.get("fb_published", False)
                if yt_published is not None:
                    data["yt_published"] = target.get("yt_published", False)
                if published_complete is not None:
                    data["published_complete"] = target.get("published_complete", False)
                story_json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception:
                pass

            self.broadcast_event("item_updated", target)
        return target

    def delete_item(self, item_id: str) -> bool:
        """Remove a story item and broadcast SSE deletion event."""
        with self._lock:
            items = self._read_index()
            found = False
            remaining = []
            for it in items:
                if it["id"] == item_id:
                    found = True
                else:
                    remaining.append(it)

            if not found:
                return False

            self._write_index(remaining)

            # Delete folder
            item_folder = self.items_dir / item_id
            if item_folder.exists() and item_folder.is_dir():
                shutil.rmtree(item_folder, ignore_errors=True)

        self.broadcast_event("item_deleted", {"id": item_id})
        return True


# Global default instance
default_manager = ItemsManager()
