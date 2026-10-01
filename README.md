# FB-2minutes Storymaker

[![Version](https://img.shields.io/badge/version-1.0.21-blue.svg)](https://github.com/AllensCreations/FBStoryMaker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-unittest-blue.svg)](tests/)

An automated storytelling engine that turns your narration, scripts, and artwork into vertical videos (9:16 and 4:5), with timed captions, audio alignment, and optional cloud publishing.

---

## ⚡ One-Line Quick Install & Auto-Updater

Install or update the application on **Linux**, **macOS**, or **Android Termux**:

```bash
curl -fsSL https://raw.githubusercontent.com/AllensCreations/FBStoryMaker/main/install.sh | bash
```

After installation, `fbsm` opens the interactive terminal dashboard. Terminal launches check the current Git branch's configured upstream, fast-forward and restart when an update is available, and stop with an error if an update cannot be verified or safely applied. A network connection is required.
Use **Up/Down** (or **J/K**) to select a menu action and press **Enter**. Choose **Open Web Studio** to render and publish through the browser workflow.

```bash
fbsm
# Open the interactive terminal dashboard

fb-storymaker --version
# Check the application version

bash install.sh --version
# Check the installer version
```

From the dashboard, choose **Edit .env settings** to open `.env` in `$VISUAL`, `$EDITOR`, `nano`, or `vi`.

---

## 🎬 System Overview & Architecture

```
┌────────────────────────────────────────────────────────┐
│ 1. CONTENT IDEATION & ASSETS (Google Studio / Gemini)  │
│    • Input: Story Topic / Script JSON                  │
│    • Output: Structured Scene JSON + Images + Voiceover │
└───────────────────────┬────────────────────────────────┘
                        │ POST /api/upload_item (ZIP + JSON)
                        ▼
┌────────────────────────────────────────────────────────┐
│ 2. CREATIVE STUDIO & PACKAGES QUEUE (Web UI)           │
│    • 📦 Story Packages: Live catalog, status, archive  │
│    • 🎬 Studio: Real-time waveform, timeline markers,  │
│      ambient backdrop glow, canvas preview & TTS       │
│    • 📅 Schedule: Social release queue & publish sync  │
│    • ⚙️ Settings Modal: Tabbed APIs, Cloud Publisher,   │
│      Google Sheets manifest & Workflow Guide           │
└───────────────────────┬────────────────────────────────┘
                        │ POST /api/items/<id>/auto-publish
                        ▼
┌────────────────────────────────────────────────────────┐
│ 3. HIGH-PRECISION ALIGNMENT & RENDER ENGINE            │
│    • Gemini Multimodal Audio Alignment:                │
│      Analyzes raw audio + text for scene cuts          │
│    • Smart Silence Snapping (FFmpeg silencedetect):   │
│      Snaps cuts to breath pauses within 300ms window   │
│    • Visual Choreography Core (100% Visual Parity):    │
│      - Ambient backdrop blur + top/bottom vignette     │
│      - Centered width-fitted drop shadow               │
│      - Dynamic Timed Sub-Caption Paging (TikTok style) │
│      - 6px bottom progress bar                         │
│    • Final Master Video Exporter:                      │
│      Direct frame-piping to FFmpeg H.264 MP4           │
└───────────────────────┬────────────────────────────────┘
                        │ Headless Cloud Delivery
                        ▼
┌────────────────────────────────────────────────────────┐
│ 4. CLOUD PUBLISHER & DUPLICATE PREVENTION              │
│    • Multi-tier duplicate check (Local + Sheet + DBX)  │
│    • Overwrite warning modal with user confirmation    │
│    • Direct headless Dropbox MP4 upload                │
│    • Google Sheets manifest logging & SSE updates      │
└────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 1. Studio & Publishing Queue
- **📦 Story Packages**: Manage incoming story packages, track real-time rendering progress via Server-Sent Events (SSE), filter by pending/published status, and load stories into the studio with one click.
- **🎬 Studio**: Creative canvas with 30 FPS playback, interactive audio waveform, manual draggable cut markers, fast cadence alignment, multimodal AI auto-alignment, and **web-based video rendering**. Click **Auto-Publish** to render and automatically queue for publishing.
- **⏳ Publish Queue**: The completed browser render enters the queue; background work handles Dropbox upload and Turso sync without rendering it again. Studio clears only after the server accepts the job. Follow progress here, and reopen failed stories to retry.
- **📅 Schedule**: Publishing overview with campaign search, platform filters, and interactive Facebook/YouTube status controls.
- **⚙️ Settings Modal**: Consolidated credentials modal supporting Gemini API keys, Gemini model selection (`gemini-2.5-flash`, `gemini-1.5-pro`, `gemini-3.8-flash`), Dropbox cloud credentials, and Google Sheets manifest URLs.

### 2. Single Unified Web Render Workflow
- **Web-Only Video Rendering**: All rendering happens in the browser via the Studio's **Auto-Publish** feature; the terminal menu remains available for launching the Studio and setup tools.
- **In-Browser Canvas Render**: Video is rendered directly in the browser using MediaRecorder + canvas capture at 30 FPS.
- **Automatic Queue on Completion**: Once the video is ready, it automatically enqueues for publishing (Dropbox + Sheets logging).
- **Real-Time Progress**: The Publish Queue tab shows upload and database-sync progress with SSE updates after browser rendering completes.

### 3. Auto-Jump & Instant Canvas Preview on "Open & Render"
- Clicking **"🎬 Open & Render"** (or **"🎙️ Open & Add Voiceover"**) on any story package card automatically switches the view to Studio and scrolls to the top of the interface.
- Loads scene images in parallel via non-blocking asynchronous fetching.
- Instantly displays the first scene illustration inside the Canvas Preview with full ambient backdrop glow and drop-shadow, even before audio upload.
- If voiceover audio is packaged, audio decoding, speech-cut snapping, and waveform rendering complete automatically.

### 4. Minimalist Studio UI
- **Single Primary Action**: Combined redundant export, server render, and cloud publish buttons into a single primary action button: `🚀 Auto-Publish to Dropbox & Sheets`.
- **Direct Local Download**: High-definition local MP4 download link is provided directly within the post-render completion toast notification without cluttering the canvas controls.
- **Unified Timeline Alignment**: Consolidated timeline build and alignment tools into a single `✨ Auto-Align Timeline` button with smart multimodal AI analysis and offline cadence fallback.
- **Streamlined Inputs**: Clean script input header displaying live scene counts with support for both structured JSON and plain-text `(Next image)` line markers.

### 5. Puck Voiceover & 1.1x Tempo Narration
- **Default Voice**: Google Gemini TTS defaults to `Puck (Youthful & Lively)` for energetic, engaging storytelling.
- **1.1x Speech Pacing**: Voiceover tracks are filtered at 1.1x speed using lossless audio tempo scaling (`atempo=1.1`), ensuring crisp narration that maintains voice pitch while eliminating drag.

### 6. Reactive Item Metadata & Social Publish Locking
- **Real-Time Auto-Save**: Story title, social caption, and hashtags auto-sync in the background with 300ms debouncing.
- **Social Publish Safety Lock**: Once a story is verified live on Facebook or YouTube (`fb_published` or `yt_published`), metadata editing is locked with an explicit unlock prompt to protect against desynchronization.

### 7. Triple-Layer Duplicate Prevention
- Protects against accidental overwrites by checking:
  1. Local story catalog (`published_complete` tag).
  2. Google Sheets manifest record.
  3. Dropbox destination folder.
- If a matching filename is detected, an interactive confirmation modal requests explicit overwrite authorization.

### 8. 100% Visual Parity (FFmpeg & Browser Canvas)
- **Ambient Backdrop Glow**: Gaussian-blurred, brightness-adjusted background sampled from the scene artwork.
- **Vignette Gradient**: Soft vertical gradient overlay (darkening top and bottom edges for readability).
- **Centered Width-Fitted Artwork with Drop Shadow**: 24px soft drop shadow behind the illustration.
- **Dynamic Floating White Captions**: High-contrast white subtitles with dark outlines and drop shadow, timed to phrases.
- **6px Progress Bar**: Sleek progress bar tracking video duration.

---

## 📐 Smart Aspect Ratio Detection (1:1 → 4:5 Auto-Adaptation)

The engine automatically inspects the dimensions of visual assets and adapts the target canvas ratio:

| Input Image Ratio | Target Video Ratio | Output Dimensions | Best For |
| :--- | :--- | :--- | :--- |
| **1:1 Square** (e.g. $1080 \times 1080$) | **4:5 Vertical** | **$1080 \times 1350$** | Facebook & Instagram Feed, Stories, Portrait Carousels. Preserves 80% more vertical frame space without horizontal cropping. |
| **9:16 Vertical** (e.g. $1080 \times 1920$) | **9:16 Full Vertical** | **$1080 \times 1920$** | TikTok, YouTube Shorts, Facebook Reels. Edge-to-edge full-bleed vertical display. |

---

## 🚀 Quickstart & Setup

### 1. Installation

Run the one-line installer:
```bash
curl -fsSL https://raw.githubusercontent.com/AllensCreations/FBStoryMaker/main/install.sh | bash
```

Or clone and set up locally:
```bash
git clone https://github.com/AllensCreations/FBStoryMaker.git
cd FBStoryMaker
bash setup_local.sh
```

`setup_local.sh` installs dependencies but does not create demo stories. Start with your own narration, script, and visual assets.

To increment the patch version by `0.0.1` on each local commit, enable the included Git hook:
```bash
git config core.hooksPath .githooks
```

### 2. Environment Configuration

Copy the example environment file and add your credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
DROPBOX_APP_KEY=your_dropbox_app_key
DROPBOX_APP_SECRET=your_dropbox_app_secret
DROPBOX_REFRESH_TOKEN=your_dropbox_refresh_token
GOOGLE_SHEET_URL=https://script.google.com/macros/s/.../exec
PORT=8000
```
*(You can also configure all keys directly in the Web UI via the ⚙️ Settings modal).*

### 3. Launching the Application

Video rendering happens via the web-based Studio. The `fbsm` terminal menu is retained for navigation and setup, but does not render videos itself.

```bash
# Open the arrow-key terminal menu
fbsm

# Launch the Web Studio directly
python3 main.py --web

# Or with optional flags
python3 main.py --web --port 3000 --open    # Custom port + auto-open browser

# Launch the menu explicitly from a terminal
python3 main.py --tui
```

**Render Workflow:**
1. Load or create a story package in the Studio
2. Click **Auto-Publish** to start web-based rendering
3. Video renders in the browser, then automatically queues for publishing
4. Monitor progress in the Publish Queue tab; Studio clears after server accepts

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/items` | List all story packages in the queue. |
| `GET` | `/api/items/<id>` | Retrieve full details, scene cuts, and artwork for a package. |
| `POST` | `/api/upload_item` | Ingest new story package (`-F "file=@story_pack.zip"`). Supports `-F "replace=true"` to update existing package. |
| `POST` | `/api/items/<id>/update` | **Update & replace** an existing package in-place by ID. |
| `POST` | `/api/update_item` | **Update & replace** a package matching by ID or title. |
| `POST` | `/api/items/<id>/metadata` | Update title, caption, description, or target filename. |
| `POST` | `/api/items/<id>/ai-align` | Run multimodal audio alignment & smart silence snapping. |
| `POST` | `/api/items/<id>/auto-publish` | Render video, check duplicates, upload to Dropbox, and log to Google Sheets. |
| `POST` | `/api/gemini-tts` | Synthesize speech using Gemini TTS, auto-align scene cuts, and attach audio. |
| `GET` | `/api/events` | Server-Sent Events (SSE) stream for real-time progress and notifications. |
| `GET` / `POST` | `/api/settings` | Retrieve or save configuration settings to `.env`. |

---

## 📦 Automated Ingestion & Local Update via cURL

Integrate local image generators, LLM scriptwriters, or automated pipelines directly via `curl`:

### 1. Ingest a New Story Package
```bash
curl -X POST http://localhost:8000/api/upload_item \
  -F "file=@story_pack.zip"
```

### 2. Update and Replace an Existing Package (by Item ID)
```bash
curl -X POST http://localhost:8000/api/items/<ITEM_ID>/update \
  -F "file=@updated_story_pack.zip"
```

### 3. Update via Python CLI Helper
```bash
# Upload a new package
python3 scripts/send_story.py path/to/images/ --script path/to/story.json

# Update existing package in-place
python3 scripts/send_story.py path/to/images/ --script path/to/story.json --update
```

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

---

## 📚 Guides & Automation Documentation

- [Turso + Make.com Integration Guide](docs/TURSO_MAKE_GUIDE.md): Configure the database and publishing workflow.
- [Google AI Studio Workflow Guide](docs/GOOGLE_STUDIO_GUIDE.md): Prepare and send story packages from Google AI Studio.
- [Automation & Webhook Pipeline Guide](docs/AUTOMATION_GUIDE.md): Connect Google Flow, GitHub Actions, and Make.com.

---

## 📁 Repository Structure

```
FBStoryMaker/
├── index.html                  # Creative Studio Web UI (Main client application)
├── AR.html                     # Mirrored client UI
├── app.py                      # Universal Python HTTP server & API gateway
├── main.py                     # Main CLI and pipeline orchestrator
├── install.sh                  # Installer and launcher setup
├── setup_local.sh              # Local environment configuration script
├── VERSION                     # Release version indicator
├── .env.example                # Example environment variables template
├── .githooks/                  # Optional version-bump commit hook
├── src/
│   ├── align_engine/           # Speech-Cue Align Engine (script parsing & pause detection)
│   ├── duration_director/      # Scene Duration Director (asset & timeline mapping)
│   ├── choreography_core/      # Visual Choreographer (Ken Burns, dissolves, sub-captions, vignettes)
│   ├── exporter/               # Video Exporter (FFmpeg frame-pipe & audio muxing)
│   ├── gemini_service.py       # Gemini TTS, multimodal audio alignment & silence snapping
│   ├── items_manager.py        # Story packages management & persistence
│   ├── archive_manager.py      # Publication history and duplicate verification
│   └── termux_ui.py            # Interactive Terminal Dashboard for Termux
├── web/
│   ├── index.html              # Mirrored Creative Studio UI
│   └── server.py               # Local Python HTTP API server implementation
├── scripts/
│   ├── google_studio_bridge.py # Automated bridge script
│   └── send_story.py           # Python CLI script to send story packages to server
├── assets/                     # User story packages, visuals, scripts, and output videos
├── tests/                      # Automated test suite
├── Makefile                    # Make targets (setup, run, web, test, clean)
└── requirements.txt            # Runtime dependencies
```

---

## 📄 License
MIT License. Created by [AllensCreations](https://github.com/AllensCreations).