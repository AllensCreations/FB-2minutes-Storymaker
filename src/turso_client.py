"""
Turso (libSQL Edge SQLite) HTTP Client for FB 2minutes Storymaker
Provides zero-dependency HTTP v2 pipeline access to Turso databases.
Replaces Google Apps Script with sub-10ms edge database queries.
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


def normalize_turso_url(db_url: str) -> str:
    """Normalize libSQL/turso URL to standard https:// endpoint."""
    url = (db_url or "").strip().rstrip("/")
    if url.startswith("libsql://"):
        url = "https://" + url[len("libsql://"):]
    elif not url.startswith("http://") and not url.startswith("https://") and url:
        url = "https://" + url
    return url


def execute_turso_pipeline(
    db_url: str,
    auth_token: str,
    statements: List[Tuple[str, Optional[List[Any]]]]
) -> Dict[str, Any]:
    """Execute raw SQL statements via Turso HTTP v2 pipeline."""
    base_url = normalize_turso_url(db_url)
    if not base_url:
        raise ValueError("Turso database URL is required.")

    pipeline_url = f"{base_url}/v2/pipeline"
    requests_payload = []

    for sql, args in statements:
        stmt_obj: Dict[str, Any] = {"sql": sql}
        if args:
            typed_args = []
            for a in args:
                if a is None:
                    typed_args.append({"type": "null"})
                elif isinstance(a, bool):
                    typed_args.append({"type": "integer", "value": "1" if a else "0"})
                elif isinstance(a, int):
                    typed_args.append({"type": "integer", "value": str(a)})
                elif isinstance(a, float):
                    typed_args.append({"type": "float", "value": a})
                else:
                    typed_args.append({"type": "text", "value": str(a)})
            stmt_obj["args"] = typed_args
        requests_payload.append({"type": "execute", "stmt": stmt_obj})

    requests_payload.append({"type": "close"})

    data = json.dumps({"requests": requests_payload}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token.strip()}"
    }

    req = urllib.request.Request(pipeline_url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(err_body)
            msg = parsed.get("message") or parsed.get("error") or err_body
        except Exception:
            msg = err_body or str(e)
        raise RuntimeError(f"Turso API HTTP {e.code}: {msg}")
    except Exception as e:
        raise RuntimeError(f"Turso connection error: {e}")


def init_turso_schema(db_url: str, auth_token: str) -> Dict[str, Any]:
    """Initialize stories table in Turso if not present and ensure social upload and dropbox_path columns exist."""
    schema_sql = (
        "CREATE TABLE IF NOT EXISTS stories ("
        "  filename TEXT PRIMARY KEY,"
        "  caption TEXT,"
        "  description TEXT,"
        "  dropbox_path TEXT,"
        "  status TEXT DEFAULT 'ready',"
        "  uploaded_to_fb_ig TEXT DEFAULT 'pending',"
        "  uploaded_to_youtube TEXT DEFAULT 'pending',"
        "  updated_at TEXT DEFAULT (datetime('now'))"
        ");"
    )
    col_dp_sql = "ALTER TABLE stories ADD COLUMN dropbox_path TEXT;"
    col_fb_sql = "ALTER TABLE stories ADD COLUMN uploaded_to_fb_ig TEXT DEFAULT 'pending';"
    col_yt_sql = "ALTER TABLE stories ADD COLUMN uploaded_to_youtube TEXT DEFAULT 'pending';"
    try:
        execute_turso_pipeline(db_url, auth_token, [(schema_sql, None)])
    except Exception:
        pass
    try:
        execute_turso_pipeline(db_url, auth_token, [(col_dp_sql, None)])
    except Exception:
        pass
    try:
        execute_turso_pipeline(db_url, auth_token, [(col_fb_sql, None)])
    except Exception:
        pass
    try:
        execute_turso_pipeline(db_url, auth_token, [(col_yt_sql, None)])
    except Exception:
        pass
    return {"ok": True}


def turso_test_connection(db_url: str, auth_token: str, seed_sample: bool = True) -> Dict[str, Any]:
    """Verify Turso credentials, ensure schema exists, and seed initial sample story if empty."""
    init_turso_schema(db_url, auth_token)
    res = execute_turso_pipeline(db_url, auth_token, [("SELECT COUNT(*) FROM stories;", None)])
    count = 0
    try:
        results = res.get("results", [])
        if results and results[0].get("type") == "ok":
            rows = results[0].get("response", {}).get("result", {}).get("rows", [])
            if rows and rows[0]:
                val = rows[0][0].get("value") if isinstance(rows[0][0], dict) else rows[0][0]
                count = int(val)
    except Exception:
        pass

    seeded = False
    if count == 0 and seed_sample:
        try:
            turso_log_story(
                db_url=db_url,
                auth_token=auth_token,
                filename="sample_story_001.mp4",
                caption="Stop waiting for tomorrow - take action now! #storymaker #motivation",
                description="Demo story item created automatically during Turso connection verification.",
                status="ready",
                uploaded_to_fb_ig="pending",
                uploaded_to_youtube="pending"
            )
            count = 1
            seeded = True
        except Exception:
            pass

    if seeded:
        msg = "Connected to Turso database successfully. Schema verified and sample story seeded (1 item ready)!"
    else:
        msg = f"Connected to Turso database successfully. Schema verified ({count} story items in database)."

    return {
        "ok": True,
        "message": msg,
        "count": count,
        "seeded": seeded,
        "details": res
    }


def turso_log_story(
    db_url: str,
    auth_token: str,
    filename: str,
    caption: str,
    description: str,
    status: str = "ready",
    uploaded_to_fb_ig: str = "pending",
    uploaded_to_youtube: str = "pending",
    dropbox_path: Optional[str] = None
) -> Dict[str, Any]:
    """Upsert story record into Turso stories table with social upload statuses and dropbox path."""
    init_turso_schema(db_url, auth_token)
    sql = (
        "INSERT INTO stories (filename, caption, description, dropbox_path, status, uploaded_to_fb_ig, uploaded_to_youtube, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now')) "
        "ON CONFLICT(filename) DO UPDATE SET "
        "caption=excluded.caption, "
        "description=excluded.description, "
        "dropbox_path=COALESCE(excluded.dropbox_path, stories.dropbox_path), "
        "status=excluded.status, "
        "uploaded_to_fb_ig=COALESCE(excluded.uploaded_to_fb_ig, stories.uploaded_to_fb_ig), "
        "uploaded_to_youtube=COALESCE(excluded.uploaded_to_youtube, stories.uploaded_to_youtube), "
        "updated_at=datetime('now');"
    )
    return execute_turso_pipeline(
        db_url,
        auth_token,
        [(sql, [filename, caption, description, dropbox_path, status, uploaded_to_fb_ig, uploaded_to_youtube])]
    )


def turso_check_duplicate(db_url: str, auth_token: str, filename: str) -> bool:
    """Check if story filename already exists in Turso."""
    try:
        sql = "SELECT filename FROM stories WHERE filename = ? LIMIT 1;"
        res = execute_turso_pipeline(db_url, auth_token, [(sql, [filename])])
        results = res.get("results", [])
        if results and results[0].get("type") == "ok":
            response = results[0].get("response", {})
            result = response.get("result", {})
            rows = result.get("rows", [])
            return len(rows) > 0
    except Exception:
        pass
    return False


def turso_delete_story(db_url: str, auth_token: str, filename: str) -> Dict[str, Any]:
    """Delete story record from Turso."""
    sql = "DELETE FROM stories WHERE filename = ?;"
    return execute_turso_pipeline(db_url, auth_token, [(sql, [filename])])


def turso_update_status(
    db_url: str,
    auth_token: str,
    filename: str,
    status: Optional[str] = None,
    uploaded_to_fb_ig: Optional[str] = None,
    uploaded_to_youtube: Optional[str] = None,
    dropbox_path: Optional[str] = None
) -> Dict[str, Any]:
    """Update story publication, dropbox path and platform upload statuses in Turso."""
    init_turso_schema(db_url, auth_token)
    sets = ["updated_at = datetime('now')"]
    args: List[Any] = []
    if status is not None:
        sets.append("status = ?")
        args.append(status)
    if uploaded_to_fb_ig is not None:
        sets.append("uploaded_to_fb_ig = ?")
        args.append(uploaded_to_fb_ig)
    if uploaded_to_youtube is not None:
        sets.append("uploaded_to_youtube = ?")
        args.append(uploaded_to_youtube)
    if dropbox_path is not None:
        sets.append("dropbox_path = ?")
        args.append(dropbox_path)
    args.append(filename)
    sql = f"UPDATE stories SET {', '.join(sets)} WHERE filename = ?;"
    return execute_turso_pipeline(db_url, auth_token, [(sql, args)])


def turso_list_stories(db_url: str, auth_token: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve recent stories from Turso."""
    init_turso_schema(db_url, auth_token)
    sql = (
        "SELECT filename, caption, description, dropbox_path, status, uploaded_to_fb_ig, uploaded_to_youtube, updated_at "
        "FROM stories ORDER BY updated_at DESC LIMIT ?;"
    )
    res = execute_turso_pipeline(db_url, auth_token, [(sql, [limit])])
    results = res.get("results", [])
    stories = []
    if results and results[0].get("type") == "ok":
        response = results[0].get("response", {})
        result = response.get("result", {})
        cols = [c.get("name") for c in result.get("cols", [])]
        rows = result.get("rows", [])
        for row in rows:
            entry = {}
            for idx, col in enumerate(cols):
                val = row[idx].get("value") if isinstance(row[idx], dict) else row[idx]
                entry[col] = val
            stories.append(entry)
    return stories
