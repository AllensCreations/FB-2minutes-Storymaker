#!/usr/bin/env python3
"""
send_story.py - Direct Image-to-API Story Dispatcher
---------------------------------------------------
Use this when you already generate images but do NOT have a JSON file.
Takes a folder of images (or image file paths), automatically creates
the story package and scene splits, and sends it directly to the Storymaker API.

Usage as CLI:
    python3 scripts/send_story.py --images-dir ./my_images --title "Lighthouse Mystery"
    python3 scripts/send_story.py --snippet  # Print 15-line copy-paste Python snippet for your code

Usage in Python code:
    from scripts.send_story import send_images_to_api

    send_images_to_api(
        images="./my_images",  # or list of file paths ['01.png', '02.png']
        title="My Generated Story",
        api_url="http://localhost:8000/api/upload_item"
    )
"""

import argparse
import io
import json
import os
import re
import sys
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import List, Union, Optional, Dict, Any


def natural_sort_key(s: str):
    """Sort strings containing numbers naturally (e.g. 1.png, 2.png, 10.png)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", str(s))]


def package_images_to_zip(
    images: Union[str, Path, List[Union[str, Path]]],
    title: str = "AI Generated Story",
    script_text: Optional[str] = None,
    description: Optional[str] = None
) -> bytes:
    """
    Bundle image files into an in-memory ZIP archive with auto-generated
    story.json and script.txt (Scene 1, Scene 2...) without needing a pre-made JSON.
    """
    image_paths: List[Path] = []
    
    if isinstance(images, (str, Path)):
        p = Path(images)
        if p.is_dir():
            valid_exts = {".png", ".jpg", ".jpeg", ".webp"}
            image_paths = [f for f in p.iterdir() if f.suffix.lower() in valid_exts]
            image_paths.sort(key=lambda x: natural_sort_key(x.name))
        elif p.is_file():
            image_paths = [p]
        else:
            raise FileNotFoundError(f"Path not found: {images}")
    elif isinstance(images, list):
        image_paths = [Path(img) for img in images if Path(img).is_file()]
        image_paths.sort(key=lambda x: natural_sort_key(x.name))
    else:
        raise ValueError("images must be a directory path, file path, or list of file paths.")

    if not image_paths:
        raise ValueError("No valid image files found to package.")

    # Split script if provided
    script_chunks = []
    if script_text:
        if "(Next image)" in script_text:
            script_chunks = [c.strip() for c in script_text.split("(Next image)") if c.strip()]
        else:
            script_chunks = [c.strip() for c in script_text.splitlines() if c.strip()]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        scenes = []
        script_parts = []

        for idx, img_path in enumerate(image_paths):
            dest_name = f"{idx + 1:02d}{img_path.suffix.lower()}"
            zf.write(img_path, arcname=dest_name)

            text = script_chunks[idx] if idx < len(script_chunks) else f"Scene {idx + 1}"
            scenes.append({
                "scene": idx + 1,
                "text": text,
                "image": dest_name
            })
            script_parts.append(f"Scene {idx + 1}: {text}")

        story_json = {
            "title": title,
            "description": description or f"Auto-generated story package with {len(scenes)} scenes.",
            "scenes": scenes
        }
        zf.writestr("story.json", json.dumps(story_json, indent=2))
        full_script = script_text if script_text else "\n(Next image)\n".join(script_parts)
        zf.writestr("script.txt", full_script)

    return buf.getvalue()


def send_images_to_api(
    images: Union[str, Path, List[Union[str, Path]]],
    title: str = "AI Generated Story",
    script_text: Optional[str] = None,
    description: Optional[str] = None,
    api_url: str = "http://localhost:8000/api/upload_item",
    timeout: int = 30,
    replace: bool = False,
    item_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function: Package images and POST them to Storymaker API.
    Zero third-party dependencies required.
    """
    zip_bytes = package_images_to_zip(
        images=images,
        title=title,
        script_text=script_text,
        description=description
    )

    boundary = f"----WebKitFormBoundary{int(time.time()*1000)}"
    crlf = b"\r\n"

    body = io.BytesIO()
    if replace:
        body.write(f"--{boundary}".encode() + crlf)
        body.write(b'Content-Disposition: form-data; name="replace"' + crlf + crlf + b"true" + crlf)
    if item_id:
        body.write(f"--{boundary}".encode() + crlf)
        body.write(f'Content-Disposition: form-data; name="item_id"'.encode() + crlf + crlf + str(item_id).encode() + crlf)
    if title:
        body.write(f"--{boundary}".encode() + crlf)
        body.write(f'Content-Disposition: form-data; name="title"'.encode() + crlf + crlf + str(title).encode() + crlf)

    body.write(f"--{boundary}".encode() + crlf)
    body.write(f'Content-Disposition: form-data; name="file"; filename="{title}.zip"'.encode() + crlf)
    body.write(b"Content-Type: application/zip" + crlf + crlf)
    body.write(zip_bytes)
    body.write(crlf)
    body.write(f"--{boundary}--".encode() + crlf)

    payload = body.getvalue()

    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(payload))
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp_data = resp.read().decode("utf-8")
        try:
            return json.loads(resp_data)
        except Exception:
            return {"status": resp.status, "body": resp_data}


SNIPPET_CODE = '''# --- Zero-Dependency Sending Function for your Image Generator ---
import io, json, re, time, zipfile, urllib.request
from pathlib import Path

def send_to_storymaker(image_folder, title="AI Story", api_url="http://localhost:8000/api/upload_item"):
    """Call this right after your images finish generating!"""
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    imgs = sorted([f for f in Path(image_folder).iterdir() if f.suffix.lower() in exts],
                  key=lambda x: [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\\d+)', x.name)])
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        scenes = []
        for i, img in enumerate(imgs):
            name = f"{i+1:02d}{img.suffix}"
            zf.write(img, arcname=name)
            scenes.append({"scene": i + 1, "text": f"Scene {i + 1}", "image": name})
        zf.writestr("story.json", json.dumps({"title": title, "scenes": scenes}, indent=2))
        zf.writestr("script.txt", "\\n(Next image)\\n".join([f"Scene {s['scene']}: Scene {s['scene']}" for s in scenes]))
    
    zip_bytes = buf.getvalue()
    b = f"----WebKitFormBoundary{int(time.time()*1000)}"
    body = (f"--{b}\\r\\nContent-Disposition: form-data; name=\\"file\\"; filename=\\"{title}.zip\\"\\r\\nContent-Type: application/zip\\r\\n\\r\\n".encode() 
            + zip_bytes + f"\\r\\n--{b}--\\r\\n".encode())
    
    req = urllib.request.Request(api_url, data=body, headers={"Content-Type": f"multipart/form-data; boundary={b}"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

# Example call:
# send_to_storymaker("./generated_frames", title="My Lighthouse Story")
'''


def main():
    parser = argparse.ArgumentParser(description="Direct Image-to-API Story Dispatcher (No JSON needed)")
    parser.add_argument("--images-dir", type=str, help="Directory containing your generated scene images")
    parser.add_argument("--title", type=str, default="AI Generated Story", help="Story title")
    parser.add_argument("--script", type=str, help="Optional text script or file with (Next image) splits")
    parser.add_argument("--upload", type=str, default=None, help="API URL (defaults to auto-discovering active port from .active_port)")
    parser.add_argument("--update", "--replace", dest="replace", action="store_true", help="Update and replace existing package matched by title or ID")
    parser.add_argument("--item-id", type=str, help="Specific story package ID to update/replace")
    parser.add_argument("--output", type=str, help="Save generated ZIP package locally")
    parser.add_argument("--snippet", action="store_true", help="Print copy-paste Python snippet for your image generator")

    args = parser.parse_args()

    if args.snippet:
        print(SNIPPET_CODE)
        return

    if not args.images_dir:
        print("Error: Please provide --images-dir <path> or use --snippet to see code.")
        parser.print_help()
        sys.exit(1)

    print(f"📦 Packaging images from: {args.images_dir} (Title: '{args.title}')...")
    zip_bytes = package_images_to_zip(
        images=args.images_dir,
        title=args.title,
        script_text=args.script
    )
    print(f"✅ Created story package archive ({len(zip_bytes)} bytes)")

    if args.output:
        Path(args.output).write_bytes(zip_bytes)
        print(f"💾 Saved to: {args.output}")

    # Determine destination API URL (auto-discover active port if not specified)
    dest_url = args.upload
    if not dest_url:
        active_port_file = Path(__file__).resolve().parent.parent / ".active_port"
        active_port = 8000
        if active_port_file.is_file():
            try:
                active_port = int(active_port_file.read_text(encoding="utf-8").strip())
            except Exception:
                pass
        dest_url = f"http://localhost:{active_port}/api/upload_item"

    action_name = "Updating" if args.replace or args.item_id else "Sending"
    print(f"🚀 {action_name} to Storymaker API: {dest_url} ...")
    try:
        res = send_images_to_api(
            images=args.images_dir,
            title=args.title,
            script_text=args.script,
            api_url=dest_url,
            replace=args.replace,
            item_id=args.item_id
        )
        print(f"🎉 Success! Item ID: {res.get('item', {}).get('id')} - Status: {res.get('message')}")
        print(f"View in Items Queue: {dest_url.replace('/api/upload_item', '').replace('/api/update_item', '')}")
    except Exception as e:
        print(f"❌ Failed to dispatch to API: {e}")
        sys.exit(1)



if __name__ == "__main__":
    main()
