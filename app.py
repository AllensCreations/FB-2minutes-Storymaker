"""
Vercel Serverless Entrypoint for FB 2minutes Storymaker
Serves the Creative Studio Web UI (index.html) and static assets safely
without requiring any external binary or backend dependencies on Vercel.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"


def handler(environ=None, start_response=None):
    """WSGI entrypoint for Vercel deployment: serves index.html and static assets."""
    if callable(start_response):
        path_info = environ.get("PATH_INFO", "/") if environ else "/"
        clean_path = path_info.lstrip("/")

        target = None
        content_type = "text/html; charset=utf-8"

        if not clean_path or clean_path in ("index.html", "index"):
            target = INDEX_FILE
        elif clean_path in ("AR.html", "web/index.html", "web/AR.html"):
            target = BASE_DIR / clean_path
        elif (BASE_DIR / clean_path).is_file():
            cand = BASE_DIR / clean_path
            if not cand.name.endswith(".py"):
                target = cand
                if cand.suffix in (".png", ".jpg", ".jpeg", ".webp"):
                    content_type = f"image/{cand.suffix.replace('.', '')}"
                elif cand.suffix == ".mp3":
                    content_type = "audio/mpeg"
                elif cand.suffix == ".css":
                    content_type = "text/css; charset=utf-8"
                elif cand.suffix == ".js":
                    content_type = "application/javascript; charset=utf-8"

        if target and target.exists():
            try:
                content = target.read_bytes()
                start_response("200 OK", [
                    ("Content-Type", content_type),
                    ("Content-Length", str(len(content))),
                    ("Access-Control-Allow-Origin", "*")
                ])
                return [content]
            except Exception:
                pass

        # Fallback to index.html if found
        if INDEX_FILE.exists():
            content = INDEX_FILE.read_bytes()
            start_response("200 OK", [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Content-Length", str(len(content))),
                ("Access-Control-Allow-Origin", "*")
            ])
            return [content]

        start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"FB 2minutes Storymaker is Online"]

    return {"status": "ok", "service": "FB 2minutes Storymaker"}


app = handler
application = handler
