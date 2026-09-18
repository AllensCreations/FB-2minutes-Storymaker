#!/usr/bin/env python3
"""
CI Render & Publish Helper for GitHub Actions & Make.com Automation
Handles asset ingestion (ZIP/Base64/URLs), executes the Storymaker pipeline,
uploads the resulting MP4 as a GitHub Release asset, and notifies Make.com webhook.
"""

import base64
import json
import os
import sys
import urllib.request
import urllib.parse
import zipfile
from pathlib import Path

# Add project root and src to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from main import run_pipeline

ASSETS_DIR = REPO_ROOT / "assets"
SCRIPTS_DIR = ASSETS_DIR / "scripts"
VOICE_DIR = ASSETS_DIR / "voice-over"
VISUALS_DIR = ASSETS_DIR / "visuals"
OUTPUT_DIR = ASSETS_DIR / "output"


def download_file(url: str, dest_path: Path):
    """Downloads a file from a remote URL to dest_path."""
    print(f"[CI Ingestion] Downloading asset from: {url}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "FB-2minutes-Storymaker-CI/1.0"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())
    print(f"[CI Ingestion] Saved to: {dest_path} ({dest_path.stat().st_size} bytes)")


def save_base64_file(data_b64: str, dest_path: Path):
    """Decodes a base64 string to dest_path."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if "," in data_b64:
        data_b64 = data_b64.split(",", 1)[1]
    raw_bytes = base64.b64decode(data_b64)
    with open(dest_path, "wb") as f:
        f.write(raw_bytes)
    print(f"[CI Ingestion] Decoded base64 asset to: {dest_path} ({len(raw_bytes)} bytes)")


def create_github_release_and_upload(
    token: str,
    repository: str,
    run_id: str,
    file_path: Path,
    title: str
) -> str:
    """
    Creates a GitHub Release and uploads the final video as an asset.
    Returns the direct public browser_download_url.
    """
    tag = f"v-run-{run_id}"
    api_base = f"https://api.github.com/repos/{repository}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "FB-2minutes-Storymaker-CI"
    }

    # 1. Create Release
    release_payload = {
        "tag_name": tag,
        "name": f"Video: {title[:50]} (Run #{run_id})",
        "body": f"Automated video generation release for Google Flow / Make.com pipeline.\nTitle: {title}",
        "draft": False,
        "prerelease": False
    }

    print(f"[GitHub Release] Creating release with tag: {tag}")
    req = urllib.request.Request(
        f"{api_base}/releases",
        data=json.dumps(release_payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        release_data = json.loads(resp.read().decode("utf-8"))

    upload_url_template = release_data["upload_url"]
    upload_url = upload_url_template.split("{")[0] + f"?name={file_path.name}"

    # 2. Upload Video Binary
    file_size = file_path.stat().st_size
    print(f"[GitHub Release] Uploading {file_path.name} ({file_size / (1024*1024):.2f} MB)...")
    with open(file_path, "rb") as f:
        video_bytes = f.read()

    upload_req = urllib.request.Request(
        upload_url,
        data=video_bytes,
        headers={
            **headers,
            "Content-Type": "video/mp4",
            "Content-Length": str(file_size)
        },
        method="POST"
    )

    with urllib.request.urlopen(upload_req) as resp:
        asset_data = json.loads(resp.read().decode("utf-8"))

    download_url = asset_data.get("browser_download_url")
    print(f"[GitHub Release] Direct download URL: {download_url}")
    return download_url


def notify_make_webhook(
    webhook_url: str,
    video_url: str,
    title: str,
    description: str,
    scheduled_time: str
):
    """
    Sends the minimal payload to Make.com incoming webhook.
    Payload: { video_url, title, description, scheduled_time }
    """
    payload = {
        "video_url": video_url,
        "title": title,
        "description": description,
        "scheduled_time": scheduled_time
    }

    print(f"[Make.com Webhook] Pinging webhook: {webhook_url}")
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "FB-2minutes-Storymaker-CI"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.getcode()
            print(f"[Make.com Webhook] Delivered successfully (HTTP {status})")
    except Exception as e:
        print(f"[Make.com Webhook] Warning: Failed to send to webhook: {e}")


def main():
    payload_json = os.environ.get("PAYLOAD_JSON", "").strip()
    data = {}
    if payload_json:
        try:
            data = json.loads(payload_json)
        except Exception as e:
            print(f"[CI Error] Failed to parse PAYLOAD_JSON: {e}")

    # Read config fields
    title = data.get("title") or os.environ.get("TITLE", "StoryShorts Video")
    description = data.get("description") or os.environ.get("DESCRIPTION", "")
    scheduled_time = data.get("scheduled_time") or data.get("upload_time") or os.environ.get("SCHEDULED_TIME", "")
    script_text = data.get("script_text") or os.environ.get("SCRIPT_TEXT", "")
    visuals_url = data.get("visuals_url") or data.get("visuals_zip_url") or os.environ.get("VISUALS_URL", "")
    visuals_base64 = data.get("visuals_base64") or os.environ.get("VISUALS_BASE64", "")
    audio_url = data.get("audio_url") or os.environ.get("AUDIO_URL", "")
    audio_base64 = data.get("audio_base64") or os.environ.get("AUDIO_BASE64", "")
    make_webhook_url = data.get("make_webhook_url") or os.environ.get("MAKE_WEBHOOK_URL", "")

    # GitHub Context
    github_token = os.environ.get("GITHUB_TOKEN", "")
    github_repo = os.environ.get("GITHUB_REPOSITORY", "")
    github_run_id = os.environ.get("GITHUB_RUN_ID", "local")

    print("=" * 65)
    print("🎬 StoryShorts CI Automation: Ingest -> Render -> Publish")
    print(f"Title:          {title}")
    print(f"Scheduled Time: {scheduled_time}")
    print(f"Repository:     {github_repo}")
    print(f"Run ID:         {github_run_id}")
    print("=" * 65)

    # 0. Check for scenes or direct images from Google Flow
    scenes = data.get("scenes") or []
    images = data.get("images") or []

    if isinstance(scenes, list) and len(scenes) > 0:
        print(f"[CI Ingestion] Detected {len(scenes)} scene(s) from Google Flow payload.")
        raw_frames_dir = VISUALS_DIR / "raw_frames"
        raw_frames_dir.mkdir(parents=True, exist_ok=True)
        visuals_zip = VISUALS_DIR / "story_visuals.zip"

        script_blocks = []
        for idx, sc in enumerate(scenes, 1):
            s_num = sc.get("scene", idx)
            s_text = sc.get("text") or sc.get("narration") or sc.get("script") or ""
            img_url = sc.get("image_url") or sc.get("url") or ""
            img_b64 = sc.get("image_base64") or sc.get("base64") or ""

            if s_text:
                script_blocks.append(f"Scene {s_num}: {s_text.strip()}")

            dest_img = raw_frames_dir / f"scene_{s_num}.png"
            if img_url:
                download_file(img_url, dest_img)
            elif img_b64:
                save_base64_file(img_b64, dest_img)

        if script_blocks and not script_text:
            script_text = "\n(Next image)\n".join(script_blocks)

        with zipfile.ZipFile(visuals_zip, "w") as zf:
            for sc in scenes:
                s_num = sc.get("scene", 1)
                img_path = raw_frames_dir / f"scene_{s_num}.png"
                if img_path.exists():
                    zf.write(img_path, arcname=f"scene_{s_num}.png")
        print(f"[CI Ingestion] Successfully packaged {visuals_zip} from Google Flow scenes.")

    elif isinstance(images, list) and len(images) > 0:
        print(f"[CI Ingestion] Detected {len(images)} direct image URL(s).")
        raw_frames_dir = VISUALS_DIR / "raw_frames"
        raw_frames_dir.mkdir(parents=True, exist_ok=True)
        visuals_zip = VISUALS_DIR / "story_visuals.zip"

        for idx, img_item in enumerate(images, 1):
            dest_img = raw_frames_dir / f"scene_{idx}.png"
            if isinstance(img_item, str) and (img_item.startswith("http://") or img_item.startswith("https://")):
                download_file(img_item, dest_img)
            elif isinstance(img_item, str) and img_item:
                save_base64_file(img_item, dest_img)

        with zipfile.ZipFile(visuals_zip, "w") as zf:
            for idx in range(1, len(images) + 1):
                img_path = raw_frames_dir / f"scene_{idx}.png"
                if img_path.exists():
                    zf.write(img_path, arcname=f"scene_{idx}.png")
        print(f"[CI Ingestion] Successfully packaged {visuals_zip} from images array.")

    # 1. Ingest Script
    if script_text:
        SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        script_file = SCRIPTS_DIR / "story.txt"
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script_text)
        print(f"[CI Ingestion] Wrote script to: {script_file}")

    # 2. Ingest Visuals (if not already packaged from scenes/images)
    visuals_zip = VISUALS_DIR / "story_visuals.zip"
    if not visuals_zip.exists() or (not scenes and not images):
        if visuals_url:
            download_file(visuals_url, visuals_zip)
        elif visuals_base64:
            save_base64_file(visuals_base64, visuals_zip)

    # 3. Ingest Audio
    audio_file = VOICE_DIR / "narration.mp3"
    if audio_url:
        download_file(audio_url, audio_file)
    elif audio_base64:
        save_base64_file(audio_base64, audio_file)

    # 4. Render Video
    print("\n[Step 1/3] Executing Storymaker Video Generation Pipeline...")
    output_mp4 = OUTPUT_DIR / "final_story.mp4"
    run_pipeline(fps=24, show_captions=True)

    if not output_mp4.exists():
        print(f"[CI Error] Expected output file not found: {output_mp4}")
        sys.exit(1)

    print(f"\n[Step 2/3] Master video successfully rendered ({output_mp4.stat().st_size} bytes)")

    # 5. Create GitHub Release & Upload
    video_download_url = ""
    if github_token and github_repo:
        print("\n[Step 3/3] Uploading MP4 to GitHub Release Asset...")
        try:
            video_download_url = create_github_release_and_upload(
                token=github_token,
                repository=github_repo,
                run_id=github_run_id,
                file_path=output_mp4,
                title=title
            )
        except Exception as e:
            print(f"[GitHub Release Error] Failed to create release: {e}")

    # Fallback to repository raw link if release upload was skipped or failed
    if not video_download_url:
        tag = f"v-run-{github_run_id}"
        video_download_url = f"https://github.com/{github_repo}/releases/download/{tag}/{output_mp4.name}"

    # 6. Notify Make.com Webhook
    if make_webhook_url:
        notify_make_webhook(
            webhook_url=make_webhook_url,
            video_url=video_download_url,
            title=title,
            description=description,
            scheduled_time=scheduled_time
        )
    else:
        print("[Make.com Webhook] No webhook URL provided. Payload not sent.")

    print("\n" + "=" * 65)
    print("🎉 Pipeline Completed Successfully!")
    print(f"Video Direct URL: {video_download_url}")
    print("=" * 65)


if __name__ == "__main__":
    main()
