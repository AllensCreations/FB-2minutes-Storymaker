# Storymaker JSON & ZIP Bridge Integration Guide

This guide explains how the **Story JSON** is created to match your generated images, how to package them into a ZIP archive, and how to send them to FB-2minutes Storymaker via the API Bridge or the Web UI.

---

## 1. 📄 How the Story JSON is Created (`story.json`)

Since you already have your image generation workflow, you only need a matching JSON script for the narration. The array elements correspond **1-to-1** with your generated image files in alphabetical order (`01.png`, `02.png`, etc.). **Do not include scene numbers** (e.g. `"Scene 1"`) in the text so your captions and social descriptions remain 100% clean.

### Recommended JSON Format (Clean Narration Strings)
```json
{
  "title": "The Whispering Lighthouse",
  "caption": "An ancient keeper discovers the light is warning the land, not the sea.",
  "description": "#storytime #mystery #shorts #viral",
  "scenes": [
    "High upon the jagged cliffs of Cape Raven, old Silas kept watch over the blackened sea.",
    "Every night for forty years, the brass gears turned the massive crystal lens like clockwork.",
```json
{
  "Title": "The 'Validation' Addiction",
  "Caption": "What if the applause you are chasing is actually keeping you a prisoner? 🎭 Living for the approval of others is a game you can never win. Here is how to break free from the trap of people-pleasing. #Psychology #Boundaries #SelfWorth #Thinkwithtobi",
  "Description": "Stop performing for an audience that doesn't care. Build a life for yourself. #Thinkwithtobi",
  "script": [
    {
      "scene_number": 0,
      "scene_type": "illustration",
      "visual_style_tag": "illustration",
      "aspect_ratio": "1:1",
      "narration": "What if the reason you are always exhausted is because you are spending all your energy performing for an audience that won't even remember your name tomorrow?",
      "prompt_description": "A low-angle shot of a main stickman figure dancing on a high stage under a glaring spotlight, while a second group of stickman figures in the audience are looking away, texting on their phones and paying no attention."
    },
    {
      "scene_number": 1,
      "scene_type": "infograph",
      "visual_style_tag": "infograph",
      "aspect_ratio": "1:1",
      "narration": "This is The Validation Trap, explained by Tobi.",
      "prompt_description": "A minimalist chart showing a main stickman figure trying to fill a bucket labeled 'Other People's Opinions' that has a giant hole in the bottom."
    }
  ]
}
```

### JSON Schema Rules:
- `Title` *(string)*: Story headline shown in the Queue and Studio. Slugified to `.mp4` filename for Publisher.
- `Caption` *(string, optional)*: Social media post caption/hook with hashtags.
- `Description` *(string, optional)*: Summary with hashtags (`#tags`) for social media export.
- `script` *(array of objects)*:
  - `scene_number`: 0-indexed scene integer.
  - `aspect_ratio`: e.g. `"1:1"` (triggers 4:5 auto-fit width layout with ambient glow) or `"9:16"`.
  - `narration`: Spoken voiceover narration for that visual frame (no "Scene X:" prefix).
  - `prompt_description`: Visual generation prompt description.

### ⚡ All-in-One Auto-Bridge Prompt Instruction:
Add this instruction snippet to the end of your existing generator prompt to produce the narration JSON, bundle the ZIP, and auto-dispatch to the API via curl:

```text
After generating all scene images:
1. Format story narration as strict JSON using this schema (NO scene numbers in narration text):
{
  "Title": "Story Title",
  "Caption": "Catchy social caption hook with hashtags",
  "Description": "Story description and hashtags",
  "script": [
    {
      "scene_number": 0,
      "scene_type": "illustration",
      "visual_style_tag": "illustration",
      "aspect_ratio": "1:1",
      "narration": "Narration text for scene 1 (clean narration without scene number prefixes)",
      "prompt_description": "Detailed visual scene prompt description..."
    }
  ]
}
2. Save JSON as story.json, image frames as 0.png, 1.png... (or 01.png, 02.png), and package them into story_pack.zip.
3. Automatically send the ZIP package to Storymaker via curl:
   curl -X POST http://localhost:8000/api/upload_item -F "file=@story_pack.zip"
```

---

## 2. 📦 ZIP Package Structure (`story_pack.zip`)

Bundle your scene images and optional `story.json` into a single ZIP archive:

```text
story_pack.zip
├── story.json       // Optional inside ZIP if pasted in Web UI modal
├── 01.png           // Scene 1 visual frame (9:16 vertical portrait)
├── 02.png           // Scene 2 visual frame
├── 03.png           // Scene 3 visual frame
└── ...              // Up to 20+ frames (.png, .jpg, .webp)
```

**Sorting Rule**: Images are sorted naturally (e.g. `01.png`, `02.png` or `1.png`, `2.png`, `10.png`), so frame numbers cleanly align with `scene: 1`, `scene: 2`, etc.

---

## 3. 🚀 Sending to Storymaker (Bridge & Upload Mechanics)

You can send your ZIP and JSON into the Storymaker Item Queue using any of these methods:

### Option A: Web UI "Upload ZIP + Paste JSON" Modal (Easiest)
1. Open the Web Studio (`http://localhost:8000`) and switch to the **Items Queue** tab.
2. Click **"✨ Upload ZIP + Paste JSON"**.
3. Select or drop your images ZIP archive.
4. Paste your JSON into the box (includes live syntax check and scene counter).
5. Click **"🚀 Add to Item Queue"**.

### Option B: Automated CLI Bridge Script
Zero pip dependencies required (pure standard Python library):

```bash
# If you have an images folder and story.json:
python3 scripts/google_studio_bridge.py --json story.json --images-dir ./my_images --upload http://localhost:8000/api/upload_item

# If you only have images and want auto-generated scene markers:
python3 scripts/send_story.py --images-dir ./my_images --title "My Story" --upload http://localhost:8000/api/upload_item
```

### Option C: Terminal curl
```bash
curl -X POST http://localhost:8000/api/upload_item -F "file=@story_pack.zip"
```

### Option D: Python Snippet inside your Generator Script
Drop this snippet at the end of your image generation script:

```python
from scripts.send_story import send_images_to_api

send_images_to_api(
    images="./my_images",
    title="My Story",
    json_path="story.json", # optional if already created
    api_url="http://localhost:8000/api/upload_item"
)
```
