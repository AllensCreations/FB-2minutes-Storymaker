"""
Vercel Serverless Function: API Gateway for Google Flow -> GitHub Actions
Endpoint: POST /api/render
Accepts video metadata from Google Flow, triggers GitHub Actions workflow,
and returns an immediate 202 Accepted status.
"""

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response_data = {
            "service": "StoryShorts Studio API Gateway",
            "version": "2.0",
            "endpoint": "POST /api/render",
            "description": "Queues 9:16 TikTok video generation and notifies Make.com webhook upon completion",
            "expected_payload": {
                "title": "My Story Title",
                "description": "Video description with #hashtags",
                "scheduled_time": "2026-09-18T18:00:00Z",
                "visuals_url": "https://example.com/story_visuals.zip",
                "audio_url": "https://example.com/narration.mp3",
                "script_text": "Scene 1...\n(Next image)\nScene 2...",
                "make_webhook_url": "https://hook.make.com/your-webhook-id"
            }
        }
        self.wfile.write(json.dumps(response_data, indent=2).encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # GitHub configuration from Environment Variables
        github_token = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN", "")
        github_repo = os.environ.get("GITHUB_REPOSITORY", "AllensCreations/FB-2minutes-Storymaker")

        if not github_token:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            err_resp = {
                "ok": False,
                "error": "GITHUB_TOKEN (or GH_PAT) environment variable is not configured in Vercel settings."
            }
            self.wfile.write(json.dumps(err_resp).encode("utf-8"))
            return

        # Prepare repository_dispatch payload
        dispatch_url = f"https://api.github.com/repos/{github_repo}/dispatches"
        dispatch_body = {
            "event_type": "generate-video",
            "client_payload": {
                "title": payload.get("title", "StoryShorts Video"),
                "description": payload.get("description", ""),
                "scheduled_time": payload.get("scheduled_time") or payload.get("upload_time", ""),
                "visuals_url": payload.get("visuals_url") or payload.get("visuals_zip_url", ""),
                "visuals_base64": payload.get("visuals_base64", ""),
                "audio_url": payload.get("audio_url", ""),
                "audio_base64": payload.get("audio_base64", ""),
                "script_text": payload.get("script_text", ""),
                "make_webhook_url": payload.get("make_webhook_url", "")
            }
        }

        req = urllib.request.Request(
            dispatch_url,
            data=json.dumps(dispatch_body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "StoryShorts-Vercel-Gateway",
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as resp:
                status_code = resp.getcode()

            self.send_response(202)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            success_resp = {
                "ok": True,
                "status": "queued",
                "message": "Video rendering workflow successfully dispatched to GitHub Actions runner.",
                "repository": github_repo,
                "title": payload.get("title"),
                "scheduled_time": payload.get("scheduled_time") or payload.get("upload_time")
            }
            self.wfile.write(json.dumps(success_resp).encode("utf-8"))

        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            resp = {
                "ok": False,
                "error": f"GitHub API rejected dispatch: {e.reason}",
                "details": err_body
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            resp = {"ok": False, "error": str(e)}
            self.wfile.write(json.dumps(resp).encode("utf-8"))
