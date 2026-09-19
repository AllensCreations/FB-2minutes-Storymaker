# FB-2minutes Storymaker

An automated storytelling engine that generates viral storybook-style vertical videos (9:16) by synchronizing voice-over narration, scripts, and visual assets with **"Picture-Book Motion"** aesthetics and **Dynamic Timed Subtitle Paging**.

Supports three execution modes:
1. **Cloud Automation Engine**: Google Flow AI &rarr; Vercel Serverless API Gateway &rarr; GitHub Actions (FFmpeg 1080&times;1920) &rarr; Make.com Auto-Publishing.
2. **Creative Studio Web UI (`index.html`)**: Interactive zero-dependency in-browser studio with real-time waveform, draggable cut markers, live 9:16 canvas preview, and 1-click WebM/MP4 export.
3. **Local CLI & Android Termux Terminal UI (`main.py`)**: Native terminal interface for local Linux, macOS, and Android phones running Termux.

---

## 🎬 System Overview & Architecture

```
┌────────────────────────────────────────────────────────┐
│ 1. CONTENT IDEATION & ASSETS (Google Flow AI)          │
│    • Input: Story Topic / Script JSON                  │
│    • Output: Structured Scene JSON + Images + Voiceover │
└───────────────────────┬────────────────────────────────┘
                        │ HTTP POST /api/trigger
                        ▼
┌────────────────────────────────────────────────────────┐
│ 2. VERCEL SERVERLESS GATEWAY & CREATIVE STUDIO         │
│    • api/trigger.js (Node.js API Gateway):             │
│      Validates x-api-key & triggers GitHub Actions     │
│    • app.py / index.html (Universal Web Studio):       │
│      Interactive preview, waveform scrubbing & cuts    │
└───────────────────────┬────────────────────────────────┘
                        │ GitHub API (workflow_dispatch)
                        ▼
┌────────────────────────────────────────────────────────┐
│ 3. HIGH-SPEED RENDER ENGINE (GitHub Actions / Termux)  │
│    • Speech-Cue Align Engine (speech_align.py):        │
│      Duration analysis & silence gap detection (-35dB) │
│    • Scene Duration Director (duration_director.py):   │
│      Timeline synchronization (Scene[N] -> Img[N])     │
│    • Visual Choreography Core (choreography_core.py):  │
│      - 9:16 Full-bleed edge-to-edge cover framing      │
│      - Continuous Ken Burns push-in & drift            │
│      - Smooth 0.45s cinematic cross-dissolve           │
│      - Dynamic Timed Sub-Caption Paging (TikTok style) │
│    • Final Master Video Exporter (video_exporter.py):  │
│      Direct frame-piping to FFmpeg H.264 (1080x1920)   │
└───────────────────────┬────────────────────────────────┘
                        │ Webhook Callback
                        ▼
┌────────────────────────────────────────────────────────┐
│ 4. AUTOMATED DISTRIBUTION (Make.com)                   │
│    • Receives final video URL & metadata               │
│    • Auto-publishes to Facebook Reels, TikTok & Shorts │
└────────────────────────────────────────────────────────┘
```

---

## 💬 High Word Counts: Auto-Split & Auto-Captioning

When a story scene has a high word count (e.g., 30–60 words across 10–18 seconds), rendering all text at once crowds the vertical canvas and causes truncation. FB-2minutes Storymaker resolves this via two complementary mechanisms:

### 1. Dynamic Timed Sub-Caption Paging (TikTok / Reels Style)
- **Visual Continuity:** The scene's background artwork stays on screen with uninterrupted Ken Burns camera motion.
- **Progressive Chunking:** Long narration text is automatically split into bite-sized phrases (5–7 words each).
- **Proportional Time Slicing:** As the scene advances in time, only the phrase currently spoken is drawn on screen in crisp white font with a dark drop shadow and outline.
- **Zero Overflow:** Subtitles never exceed 1–2 lines, ensuring 100% readability on mobile devices without any cutoffs (`...`).

```text
[Scene 2: 12.0s Duration | 30 Words Total]
├── 0.0s – 4.0s : "Deep in the whispering enchanted woods,"
├── 4.0s – 8.0s : "Elsa uncovered a glowing golden key"
└── 8.0s – 12.0s: "hidden beneath the roots of the oak."
```

### 2. Scene Subdivision Guidelines for Google Flow AI
For optimal viewer retention in short-form videos (TikTok, Shorts, Reels):
- **Ideal Scene Pacing:** 10–18 words per scene (~3.5 to 5.5 seconds of voiceover).
- **Image Prompts:** Generate 1 fresh vertical 9:16 image per scene beat to keep visual energy high.

---

## 📐 Smart Aspect Ratio Detection (1:1 → 4:5 Auto-Adaptation)

The engine automatically inspects the aspect ratio of incoming image assets and adapts the target video canvas:

| Input Image Ratio | Target Video Ratio | Output Dimensions | Best For |
| :--- | :--- | :--- | :--- |
| **1:1 Square** (e.g. $1080 \times 1080$, $1024 \times 1024$) | **4:5 Vertical** | **$1080 \times 1350$** | Facebook & Instagram Feed, Stories, Portrait Carousels. Reduces horizontal crop to just 20% (instead of 44%), preserving nearly the full square artwork! |
| **9:16 Vertical** (e.g. $1080 \times 1920$, $720 \times 1280$) | **9:16 Full Vertical** | **$1080 \times 1920$** | TikTok, YouTube Shorts, Facebook Reels. Edge-to-edge full-bleed vertical display. |

- **In the Web Studio (`index.html`):** The preview canvas immediately shifts to a 4:5 frame with a `4:5 Auto` badge, and exports `story_4x5.mp4` directly in-browser.
- **In Python CLI & CI (`duration_director.py`):** The pipeline auto-sets `timeline.width = 1080` and `timeline.height = 1350`, instructing FFmpeg to render at $1080 \times 1350$.
- **Explicit Override:** You can always force custom dimensions (e.g. `width=1080, height=1920`) in code or CLI arguments if needed.

---

## 🚀 Quickstart: One-Line Installation

Install and configure the local pipeline in a single command on **Android (Termux)**, **Ubuntu/Debian**, **macOS**, or generic Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/AllensCreations/FB-2minutes-Storymaker/main/install.sh | bash
```

### Launch Modes:

```bash
# 📱 Interactive Terminal Studio (Optimized for Android Termux)
fb-storymaker --tui
# or simply:
fb-storymaker

# 🌐 Launch the Creative Studio Web UI (open http://localhost:8000)
fb-storymaker --web

# 🎬 Render the 9:16 master story video directly in batch mode
fb-storymaker --render
```

---

## 🌐 Creative Studio Web UI (`index.html`)

A completely self-contained in-browser Creative Studio requiring **zero external server setup**:
- **Ingestion Deck:** Upload or drag-and-drop `script.txt`, `narration.mp3`, and `story_visuals.zip` (or load bundled interactive demo).
- **Audio Waveform & Pause Snapping:** Real-time visual audio waveform with -35dB silence detection and interactive draggable cut markers.
- **Scene Choreography Matrix:** Configure entrances (Spring-Pop, Dissolve, Zoom) and continuous motions (Push-in, Diagonal Drift, Horizontal Pan) per scene.
- **Live 9:16 Canvas & Subtitle Pager:** Instant 30 FPS playback preview with live subtitle chunking and progress indicator.
- **One-Click Export:** Client-side recording that exports master 1080&times;1920 video directly in your browser.

To launch locally:
```bash
make web
# or
python3 -m http.server 8000
```
Visit **[http://localhost:8000](http://localhost:8000)**.

---

## ☁️ Vercel Serverless Architecture

The repository is pre-configured for automated, zero-config deployment on Vercel:

| Component | File | Runtime | Purpose |
| :--- | :--- | :--- | :--- |
| **Serverless Entrypoint** | [`app.py`](file:///root/FB-2minutes-Storymaker/app.py) / [`index.py`](file:///root/FB-2minutes-Storymaker/index.py) | Python 3.9+ (`BaseHTTPRequestHandler` + WSGI) | Serves the Creative Studio Web UI (`index.html`) with dual Lambda dispatch and embedded gzip fallback. |
| **API Gateway** | [`api/trigger.js`](file:///root/FB-2minutes-Storymaker/api/trigger.js) | Node.js Serverless (ESM) | Ingests story JSON, validates `x-api-key`, and triggers GitHub Actions workflows. |
| **Build Configuration** | [`pyproject.toml`](file:///root/FB-2minutes-Storymaker/pyproject.toml) & [`uv.lock`](file:///root/FB-2minutes-Storymaker/uv.lock) | PEP 621 Standard | Satisfies Vercel's `uv` package resolver with zero build errors. |
| **Routing & Rewrites** | [`vercel.json`](file:///root/FB-2minutes-Storymaker/vercel.json) | Vercel Platform | Maps `/api/render` &rarr; `/api/trigger` with global CORS headers. |

---

## 🤖 Google Flow AI Automation & Make.com Integration

### 1. Master System Prompt for Google Flow AI
*(Copy and paste this into Google Flow's **System Instructions** or **Agent Persona** box)*:

```text
You are an Elite Social Media Story & Video Producer specialized in viral TikTok, YouTube Shorts, and Facebook Reels.

Your mission is to take story concepts or scene JSON inputs, generate vertical 9:16 scene images using your image tool, and dispatch the complete story package to the FB-2minutes Storymaker rendering pipeline.

---

### WORKFLOW EXECUTION:
1. INPUT PARSING:
   Receive the user's Scene JSON containing scene numbers, narration text, and visual image prompts.
   Pacing Rule: Keep each scene between 10 and 20 words for maximum visual engagement.

2. IMAGE GENERATION STEP:
   - For each scene, trigger your Image Generation tool using the `image_prompt`.
   - Ensure the image output format is vertical 9:16 aspect ratio.
   - Capture the generated image URL for each scene.

3. AUDIO INGESTION:
   - Ingest the voiceover narration audio URL or base64 data.

4. METADATA CREATION:
   - Title: High-CTR hook title (under 60 characters).
   - Description: 2-3 sentence engaging caption with 4-6 viral hashtags (#storytime #shorts #tiktok #viral #reels).
   - Upload Date: Target schedule time in ISO 8601 format (e.g. "2026-09-20T18:00:00Z").

5. PIPELINE DISPATCH CONTRACT:
   Send an HTTP POST request to the Vercel API Gateway:

   POST Endpoint: https://YOUR-VERCEL-APP.vercel.app/api/trigger
   Headers:
     Content-Type: application/json
     x-api-key: <YOUR_API_SECRET_KEY>

   Payload Structure (Direct Scene Array):
   {
     "title": "<Catchy Video Title>",
     "description": "<Engaging Description with hashtags>",
     "upload_date": "<ISO-8601 UTC Timestamp>",
     "audio_url": "<Public URL to uploaded voiceover audio>",
     "make_webhook_url": "<Make.com incoming webhook URL>",
     "scenes": [
       {
         "scene": 1,
         "text": "In a quiet village nestled between rolling hills, Elsa begins her day before sunrise.",
         "image_url": "https://storage.googleapis.com/.../scene_1.png"
       },
       {
         "scene": 2,
         "text": "She opens the wooden cupboard, but the magical yeast has mysteriously vanished.",
         "image_url": "https://storage.googleapis.com/.../scene_2.png"
       }
     ]
   }

   Expected Response (202 Accepted):
   {
     "ok": true,
     "status": "queued",
     "job_id": "job_1726645800000_3x8a9",
     "title": "...",
     "scenes_detected": 2,
     "actions_url": "https://github.com/...",
     "message": "Story video generation successfully queued in GitHub Actions..."
   }
```

---

### 2. Sample Input JSON Template for Google Flow

```json
[
  {
    "scene": 1,
    "text": "In a quiet village nestled between rolling hills, Elsa begins her day before sunrise.",
    "image_prompt": "Cinematic vertical 9:16 storybook illustration of a cozy village bakery at dawn, warm glowing lanterns, morning mist, watercolor digital painting"
  },
  {
    "scene": 2,
    "text": "She opens the wooden cupboard, but the magical yeast has mysteriously vanished.",
    "image_prompt": "Close-up cinematic 9:16 illustration of a young female baker looking shocked inside an open rustic wooden cupboard, glowing dust particles"
  },
  {
    "scene": 3,
    "text": "Armed with only her rolling pin and an ancient map, Elsa ventures into the Whispering Woods.",
    "image_prompt": "Cinematic vertical 9:16 illustration of a brave young baker stepping into an enchanted misty forest with glowing blue mushrooms, holding a lantern"
  },
  {
    "scene": 4,
    "text": "Deep within the hollow tree, the Forest Sprites were baking golden loaves of starlight bread.",
    "image_prompt": "Cinematic 9:16 storybook art of tiny glowing forest sprites baking glowing bread inside a giant magical hollow oak tree, fantasy aesthetic"
  }
]
```

---

### 3. Webhook Payload Delivered to Make.com

When GitHub Actions completes video rendering, it dispatches this payload to your `make_webhook_url`:

```json
{
  "video_url": "https://github.com/AllensCreations/FB-2minutes-Storymaker/releases/download/v-run-12345678/final_story.mp4",
  "title": "The Mystery of the Golden Forest",
  "description": "Elsa ventures into the Whispering Woods. #story #shorts #tiktok #viral",
  "scheduled_time": "2026-09-20T18:00:00Z"
}
```

---

## 📁 Repository Structure

```
FB-2minutes-Storymaker/
├── api/
│   └── trigger.js              # Vercel Node.js Serverless API Gateway
├── app.py                      # Universal Python Serverless entrypoint (BaseHTTPRequestHandler + WSGI)
├── index.py                    # Serverless entrypoint alias
├── index.html                  # Creative Studio Web UI (Browser client)
├── main.py                     # Main CLI and pipeline orchestrator
├── vercel.json                 # Vercel function routing, CORS & rewrites
├── pyproject.toml              # PEP 621 metadata & Vercel entrypoint declaration
├── uv.lock                     # Pre-locked dependency graph
├── src/
│   ├── align_engine/           # Speech-Cue Align Engine (script parsing & pause detection)
│   ├── duration_director/      # Scene Duration Director (asset & timeline mapping)
│   ├── choreography_core/      # Visual Choreographer (Ken Burns, dissolves, sub-captions)
│   ├── exporter/               # Video Exporter (FFmpeg frame-pipe & audio muxing)
│   └── termux_ui.py            # Interactive Terminal Dashboard for Termux
├── web/
│   ├── index.html              # Mirror of Creative Studio UI
│   └── server.py               # Local Python HTTP dev server
├── assets/
│   ├── voice-over/             # Narration audio (narration.mp3)
│   ├── scripts/                # Story text script (story.txt)
│   ├── visuals/                # Visual illustrations zip (story_visuals.zip)
│   └── output/                 # Rendered video (final_story.mp4)
├── tests/                      # Automated test suite (100% passing)
│   ├── test_align_engine.py
│   ├── test_api_gateway.py
│   ├── test_choreography_core.py
│   ├── test_duration_director.py
│   └── test_serverless_app.py
├── Makefile                    # Make targets (setup, run, web, test, clean)
└── requirements.txt            # Runtime dependencies (Pillow>=10.0.0)
```

---

## ⚙️ CLI Reference

```bash
# Run the pipeline with default assets
python3 main.py

# Launch Web UI on a specific port
python3 main.py --web --port 8080

# Specify custom output frame rate (default: 24 fps)
python3 main.py --run --fps 30

# Verify asset readiness
python3 main.py --check

# Regenerate bundled sample assets
python3 main.py --generate-assets
```

---

## 🛠️ Makefile Commands

| Command | Description |
| :--- | :--- |
| `make setup` | Run automated local setup (`setup_local.sh`) |
| `make run` | Execute the full pipeline and output `assets/output/final_story.mp4` |
| `make tui` | Open the interactive Termux Terminal UI |
| `make web` | Launch the local Web UI on `http://localhost:8000` |
| `make test` | Run the full test suite (`unittest`) |
| `make clean` | Clean up generated videos, caches, and temporary files |

---

## 🧪 Testing

Run the automated test suite covering all engines, the Vercel serverless entrypoints, and API dispatch:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

All 20 tests pass with zero external mock failures.

---

## 📄 License
MIT License. Created by AllensCreations.