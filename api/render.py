"""
Vercel Serverless Function: API Gateway for Google Flow -> GitHub Actions
Endpoint: POST /api/render
Accepts video metadata from Google Flow, validates API security token,
triggers GitHub Actions workflow, and returns a detailed 202 Accepted status.
"""

import json
import os
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, x-api-key")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        response_data = {
            "service": "FB-2minutes Storymaker Vercel API Gateway",
            "version": "2.0",
            "status": "online",
            "endpoints": {
                "trigger": "POST /api/trigger",
                "render": "POST /api/render"
            },
            "description": "Queues 9:16 TikTok/Shorts video generation and notifies Make.com webhook upon completion",
            "authentication": {
                "header": "x-api-key: <YOUR_SECRET_KEY> or Authorization: Bearer <YOUR_SECRET_KEY>",
                "env_var": "API_SECRET_KEY (Configure in Vercel project environment variables)"
            },
            "expected_payload": {
                "title": "The Secret of the Whispering Woods",
                "description": "Episode 1: The journey begins #story #tiktok",
                "upload_date": "2026-09-20T18:00:00Z",
                "audio_url": "https://example.com/narration.mp3",
                "images": [
                    "https://example.com/scene_1.png",
                    "https://example.com/scene_2.png"
                ],
                "script": "Scene 1: Introduction...\n(Next image)\nScene 2: The Cave...",
                "make_webhook_url": "https://hook.eu1.make.com/your-webhook-id"
            }
        }
        self.wfile.write(json.dumps(response_data, indent=2).encode("utf-8"))

    def do_POST(self):
        # 1. Verify Secret Token / API Key
        required_secret = os.environ.get("API_SECRET_KEY") or os.environ.get("API_KEY", "")
        if required_secret:
            auth_header = self.headers.get("Authorization", "")
            api_key_header = self.headers.get("x-api-key", "")
            provided_token = api_key_header
            if not provided_token and auth_header.startswith("Bearer "):
                provided_token = auth_header[7:].strip()

            if not provided_token or provided_token != required_secret:
                self.send_response(401)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                err_resp = {
                    "ok": False,
                    "error": "Unauthorized: Invalid or missing API key. Provide matching 'x-api-key' or 'Authorization: Bearer <token>' header."
                }
                self.wfile.write(json.dumps(err_resp).encode("utf-8"))
                return

        # 2. Parse JSON body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # 3. GitHub configuration from Environment Variables
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

        title = payload.get("title", "StoryShorts Video")
        description = payload.get("description", "")
        scheduled_time = payload.get("scheduled_time") or payload.get("upload_time") or payload.get("upload_date") or ""
        audio_url = payload.get("audio_url") or payload.get("audio", "")
        audio_base64 = payload.get("audio_base64", "")
        visuals_url = payload.get("visuals_url") or payload.get("visuals_zip_url") or (payload.get("images")[0] if isinstance(payload.get("images"), list) and payload.get("images") else "")
        visuals_base64 = payload.get("visuals_base64", "")
        script_text = payload.get("script_text") or payload.get("script", "")
        make_webhook_url = payload.get("make_webhook_url") or payload.get("webhook_url", "")

        # Calculate scene count
        scene_count = 1
        if script_text:
            if "(Next image)" in script_text:
                scene_count = len([s for s in script_text.split("(Next image)") if s.strip()])
            else:
                try:
                    parsed = json.loads(script_text)
                    if isinstance(parsed, list):
                        scene_count = len(parsed)
                except Exception:
                    scene_count = len([l for l in script_text.splitlines() if l.strip()]) or 1
        elif isinstance(payload.get("images"), list) and payload.get("images"):
            scene_count = len(payload.get("images"))

        # 4. Prepare repository_dispatch payload
        dispatch_url = f"https://api.github.com/repos/{github_repo}/dispatches"
        dispatch_body = {
            "event_type": "generate-video",
            "client_payload": {
                "title": title,
                "description": description,
                "scheduled_time": scheduled_time,
                "visuals_url": visuals_url,
                "visuals_base64": visuals_base64,
                "audio_url": audio_url,
                "audio_base64": audio_base64,
                "script_text": script_text,
                "make_webhook_url": make_webhook_url
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
                _ = resp.getcode()

            job_id = f"job_{int(time.time() * 1000)}"
            actions_url = f"https://github.{github_repo}/actions" if "github." in github_repo else f"https://github.com/{github_repo}/actions"

            self.send_response(202)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            success_resp = {
                "ok": True,
                "status": "queued",
                "job_id": job_id,
                "title": title,
                "scenes_detected": scene_count,
                "scheduled_for": scheduled_time or "immediate",
                "audio_source": "remote_url" if audio_url else ("base64" if audio_base64 else "demo_fallback"),
                "visuals_source": "remote_url" if visuals_url else ("base64" if visuals_base64 else "demo_fallback"),
                "make_webhook_configured": bool(make_webhook_url),
                "actions_url": actions_url,
                "repository": github_repo,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "message": "Story video generation successfully queued in GitHub Actions. Make.com will receive the published video once rendering completes."
            }
            self.wfile.write(json.dumps(success_resp, indent=2).encode("utf-8"))

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
