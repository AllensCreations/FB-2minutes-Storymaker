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
    """Initialize minimal stories table in Turso if not present."""
    schema_sql = (
        "CREATE TABLE IF NOT EXISTS stories ("
        "  filename TEXT PRIMARY KEY,"
        "  caption TEXT,"
        "  description TEXT,"
        "  status TEXT DEFAULT 'ready',"
        "  updated_at TEXT DEFAULT (datetime('now'))"
        ");"
    )
    return execute_turso_pipeline(db_url, auth_token, [(schema_sql, None)])


def turso_test_connection(db_url: str, auth_token: str) -> Dict[str, Any]:
    """Verify Turso credentials and ensure schema exists."""
    init_turso_schema(db_url, auth_token)
    res = execute_turso_pipeline(db_url, auth_token, [("SELECT COUNT(*) FROM stories;", None)])
    return {
        "ok": True,
        "message": "Connected to Turso database successfully. Schema verified.",
        "details": res
    }


def turso_log_story(
    db_url: str,
    auth_token: str,
    filename: str,
    caption: str,
    description: str,
    status: str = "ready"
) -> Dict[str, Any]:
    """Upsert story record into Turso stories table."""
    init_turso_schema(db_url, auth_token)
    sql = (
        "INSERT INTO stories (filename, caption, description, status, updated_at) "
        "VALUES (?, ?, ?, ?, datetime('now')) "
        "ON CONFLICT(filename) DO UPDATE SET "
        "caption=excluded.caption, "
        "description=excluded.description, "
        "status=excluded.status, "
        "updated_at=datetime('now');"
    )
    return execute_turso_pipeline(db_url, auth_token, [(sql, [filename, caption, description, status])])


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


def turso_update_status(db_url: str, auth_token: str, filename: str, status: str) -> Dict[str, Any]:
    """Update story publication status in Turso."""
    sql = "UPDATE stories SET status = ?, updated_at = datetime('now') WHERE filename = ?;"
    return execute_turso_pipeline(db_url, auth_token, [(sql, [status, filename])])


def turso_list_stories(db_url: str, auth_token: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve recent stories from Turso."""
    init_turso_schema(db_url, auth_token)
    sql = "SELECT filename, caption, description, status, updated_at FROM stories ORDER BY updated_at DESC LIMIT ?;"
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
