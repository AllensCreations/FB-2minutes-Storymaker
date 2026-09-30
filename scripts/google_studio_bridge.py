#!/usr/bin/env python3
"""
Google AI Studio Bridge Script for FB-2minutes Storymaker
---------------------------------------------------------
Takes story output from Google AI Studio / Gemini, ensures visual assets
and story metadata are bundled into a ZIP package, and dispatches the ZIP
to the FB-2minutes Storymaker API endpoint (/api/upload_item).

Usage:
    # 1. Package existing story.json with image directory:
    python3 scripts/google_studio_bridge.py --json story.json --images-dir ./my_images --upload http://localhost:8000/api/upload_item

    # 2. Create zip locally without uploading:
    python3 scripts/google_studio_bridge.py --json story.json --images-dir ./my_images --output story_pack.zip
"""

import argparse
import io
import json
import os
import sys
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from items_manager import natural_sort_key

try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False



def create_storybook_image(scene_num: int, total_scenes: int, title: str, text: str, width: int = 1080, height: int = 1920) -> Image.Image:
    """Generate a clean visual storybook canvas when real AI images are not yet downloaded."""
    img = Image.new("RGB", (width, height), color=(15, 20, 30))
    draw = ImageDraw.Draw(img)

    # Dynamic gradient effect
    for y in range(height):
        r = int(18 + (35 - 18) * (y / height))
        g = int(22 + (45 - 22) * (y / height))
        b = int(38 + (70 - 38) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Center decorative frame
    margin = 50
    draw.rectangle(
        [margin, margin, width - margin, height - margin],
        outline=(60, 80, 110),
        width=3
    )

    # Inner illustration area
    box_top = 200
    box_bottom = height - 500
    box_margin = 80
    draw.rectangle(
        [box_margin, box_top, width - box_margin, box_bottom],
        fill=(25, 33, 50),
        outline=(80, 110, 160),
        width=2
    )

    # Draw scene icon & number
    draw.text((width // 2, box_top + 100), f"SCENE {scene_num:02d} / {total_scenes:02d}", fill=(245, 180, 50), anchor="mm")
    draw.text((width // 2, box_top + 220), "📖", fill=(200, 220, 255), anchor="mm")
    draw.text((width // 2, box_top + 340), title, fill=(220, 230, 245), anchor="mm")

    # Word wrapped prompt description in image box
    words = text.split()
    lines = []
    cur = []
    for w in words:
        cur.append(w)
        if len(" ".join(cur)) > 32:
            lines.append(" ".join(cur))
            cur = []
    if cur:
        lines.append(" ".join(cur))

    y_text = box_bottom + 80
    for line in lines[:4]:
        draw.text((width // 2, y_text), line, fill=(255, 255, 255), anchor="mm")
        y_text += 50

    return img


def package_story(story_data: Dict[str, Any], images_dir: Path = None) -> bytes:
    """Bundle story images + story.json into an in-memory ZIP archive."""
    buf = io.BytesIO()
    scenes = story_data.get("scenes", [])
    title = story_data.get("title", "Story")

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Add story.json
        zf.writestr("story.json", json.dumps(story_data, indent=2))

        # 2. Add script.txt with (Next image) breaks for universal compatibility
        script_parts = []
        for s in scenes:
            script_parts.append(f"Scene {s.get('scene', 1)}: {s.get('text', '')}")
        zf.writestr("script.txt", "\n(Next image)\n".join(script_parts))

        # 3. Add images
        for i, s in enumerate(scenes):
            scene_num = s.get("scene", i + 1)
            filename = f"{scene_num:02d}.png"

            img_bytes = None
            if images_dir and images_dir.is_dir():
                # Direct image name if specified in scene metadata
                if "image" in s and (images_dir / s["image"]).exists():
                    img_bytes = (images_dir / s["image"]).read_bytes()
                else:
                    cand = list(images_dir.glob(f"*{scene_num}*"))
                    if cand:
                        img_bytes = cand[0].read_bytes()

            if not img_bytes:
                # Generate fallback/preview storybook canvas
                if HAS_PIL:
                    pil_img = create_storybook_image(
                        scene_num=scene_num,
                        total_scenes=len(scenes),
                        title=title,
                        text=s.get("text", "")
                    )
                    img_buf = io.BytesIO()
                    pil_img.save(img_buf, format="PNG")
                    img_bytes = img_buf.getvalue()
                else:
                    img_bytes = b"EMPTY_IMAGE"

            zf.writestr(filename, img_bytes)

    return buf.getvalue()


def upload_zip(zip_bytes: bytes, upload_url: str, filename: str = "story_pack.zip") -> Dict[str, Any]:
    """Upload ZIP file to Storymaker API endpoint via multipart/form-data."""
    boundary = f"----WebKitFormBoundary{int(time.time()*1000)}"
    crlf = b"\r\n"

    body = io.BytesIO()
    body.write(f"--{boundary}".encode() + crlf)
    body.write(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode() + crlf)
    body.write(b"Content-Type: application/zip" + crlf + crlf)
    body.write(zip_bytes)
    body.write(crlf)
    body.write(f"--{boundary}--".encode() + crlf)

    payload = body.getvalue()

    req = urllib.request.Request(
        upload_url,
        data=payload,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(payload))
        },
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        resp_data = resp.read().decode("utf-8")
        try:
            return json.loads(resp_data)
        except Exception:
            return {"status": resp.status, "body": resp_data}



def main():
    parser = argparse.ArgumentParser(description="Google AI Studio / Image Generation to FB-2minutes Storymaker Bridge")
    parser.add_argument("--json", type=str, help="Path to story JSON file from Google Studio")
    parser.add_argument("--images-dir", type=str, help="Directory containing pre-generated scene images (No JSON required)")
    parser.add_argument("--title", type=str, help="Story title (optional)")
    parser.add_argument("--script", type=str, help="Optional text script file or string with (Next image) splits")
    parser.add_argument("--description", type=str, help="Optional story description / hashtags")
    parser.add_argument("--output", type=str, help="Save generated ZIP to local file")
    parser.add_argument("--upload", type=str, help="API upload URL (e.g. http://localhost:8000/api/upload_item)")

    args = parser.parse_args()

    story_data = None
    images_dir = Path(args.images_dir) if args.images_dir else None

    if args.json:
        with open(args.json, "r", encoding="utf-8") as f:
            story_data = json.load(f)
    elif images_dir and images_dir.is_dir():
        # Auto-create story structure from images directory without requiring JSON
        exts = {".png", ".jpg", ".jpeg", ".webp"}
        image_files = sorted([p for p in images_dir.iterdir() if p.suffix.lower() in exts], key=lambda x: natural_sort_key(x.name))
        if not image_files:
            print(f"Error: No image files found in '{args.images_dir}'")
            sys.exit(1)

        title = args.title or images_dir.name.replace("_", " ").replace("-", " ").title()
        
        # Load script if provided
        script_text = ""
        if args.script:
            if os.path.exists(args.script):
                script_text = Path(args.script).read_text(encoding="utf-8")
            else:
                script_text = args.script

        script_chunks = []
        if script_text:
            if "(Next image)" in script_text:
                script_chunks = [c.strip() for c in script_text.split("(Next image)") if c.strip()]
            else:
                script_chunks = [c.strip() for c in script_text.splitlines() if c.strip()]

        scenes = []
        for idx, img_p in enumerate(image_files):
            text = script_chunks[idx] if idx < len(script_chunks) else f"Scene {idx + 1}"
            scenes.append({
                "scene": idx + 1,
                "text": text,
                "image": img_p.name
            })

        story_data = {
            "title": title,
            "description": args.description or f"Generated story with {len(scenes)} visual scenes.",
            "scenes": scenes
        }
    else:
        print("Error: Specify --json <story.json> or --images-dir <dir>.")
        sys.exit(1)

    if args.title and story_data:
        story_data["title"] = args.title

    print(f"📦 Packaging story: '{story_data.get('title')}' ({len(story_data.get('scenes', []))} scenes)...")
    zip_bytes = package_story(story_data, images_dir)
    print(f"✅ Created ZIP archive ({len(zip_bytes)} bytes)")

    if args.output:
        out_path = Path(args.output)
        out_path.write_bytes(zip_bytes)
        print(f"💾 Saved ZIP to: {out_path.resolve()}")

    if args.upload:
        print(f"🚀 Dispatching ZIP to Storymaker API: {args.upload} ...")
        try:
            res = upload_zip(zip_bytes, args.upload, filename=f"{story_data.get('title', 'story_pack')}.zip")
            print(f"🎉 Successfully uploaded! API Response:\n{json.dumps(res, indent=2)}")
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
