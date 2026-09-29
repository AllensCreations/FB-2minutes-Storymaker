"""
Local Server Video Archive Manager.
Manages offline video publishing, local media storage, and JSON manifest.
"""

import json
import os
import re
import socket
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO_ROOT / "assets" / "output"
MANIFEST_PATH = OUTPUT_DIR / "archive_manifest.json"


def get_local_ip() -> str:
    """Detect primary LAN IP address for local network access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class ArchiveManager:
    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir
        self.manifest_path = self.output_dir / "archive_manifest.json"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_manifest(self) -> List[Dict[str, Any]]:
        if not self.manifest_path.exists():
            return []
        try:
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _write_manifest(self, items: List[Dict[str, Any]]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

    def list_archive(self) -> List[Dict[str, Any]]:
        """List all archived videos, auto-syncing with files on disk."""
        items = self._read_manifest()
        known_files = {item["filename"]: item for item in items if "filename" in item}

        # Scan disk for any mp4 files in output_dir
        disk_files = list(self.output_dir.glob("*.mp4"))
        changed = False

        for fpath in disk_files:
            fn = fpath.name
            if fn not in known_files:
                stat = fpath.stat()
                clean_title = fn.replace(".mp4", "").replace("-", " ").replace("_", " ").title()
                record = {
                    "rowIndex": len(items) + 1,
                    "filename": fn,
                    "title": clean_title,
                    "caption": f"Story video: {clean_title}",
                    "description": "#story #shorts #animation",
                    "file_size": stat.st_size,
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
                    "video_url": f"/media/archive/{fn}",
                    "uploaded": "NO",
                    "youtube": "NO"
                }
                items.append(record)
                known_files[fn] = record
                changed = True

        # Sort newest first
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        # Re-assign 1-based rowIndex
        for i, item in enumerate(items):
            item["rowIndex"] = i + 1

        if changed:
            self._write_manifest(items)

        return items

    def save_video(
        self,
        video_bytes: bytes,
        filename: str,
        title: Optional[str] = None,
        caption: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save MP4 video file to output directory and log to local manifest."""
        clean_fn = filename.strip()
        if not clean_fn.lower().endswith(".mp4"):
            clean_fn += ".mp4"

        target_path = self.output_dir / clean_fn
        target_path.write_bytes(video_bytes)

        stat = target_path.stat()
        clean_title = title or clean_fn.replace(".mp4", "").replace("-", " ").replace("_", " ").title()
        clean_cap = caption or clean_title
        clean_desc = description or "#story #shorts"

        items = self._read_manifest()
        # Check if already exists in manifest
        existing = next((it for it in items if it.get("filename") == clean_fn), None)

        if existing:
            existing["title"] = clean_title
            existing["caption"] = clean_cap
            existing["description"] = clean_desc
            existing["file_size"] = stat.st_size
            existing["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            existing["video_url"] = f"/media/archive/{clean_fn}"
            record = existing
        else:
            record = {
                "rowIndex": len(items) + 1,
                "filename": clean_fn,
                "title": clean_title,
                "caption": clean_cap,
                "description": clean_desc,
                "file_size": stat.st_size,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "video_url": f"/media/archive/{clean_fn}",
                "uploaded": "NO",
                "youtube": "NO"
            }
            items.insert(0, record)

        # Re-index
        for i, it in enumerate(items):
            it["rowIndex"] = i + 1

        self._write_manifest(items)
        return record

    def mark_status(self, row_index: int, platform: str, status: str = "YES") -> bool:
        """Mark Facebook or YouTube status for a given record."""
        items = self._read_manifest()
        target = next((it for it in items if it.get("rowIndex") == int(row_index)), None)
        if not target:
            return False

        if platform.lower() in ("fb", "facebook", "uploaded"):
            target["uploaded"] = status
        elif platform.lower() in ("yt", "youtube"):
            target["youtube"] = status
        else:
            return False

        self._write_manifest(items)
        return True
