# FB-2minutes Storymaker

An automated storytelling engine that generates storybook-style vertical videos (9:16) by synchronizing voice-over narration, scripts, and visual assets with **"Picture-Book Motion"** aesthetics.

Includes both a **command-line pipeline** and a **creative studio Web UI** (`index.html`) for in-browser creation, scene preview, and playback.

---

## 🎬 System Overview

FB-2minutes Storymaker implements the editorial behavior, narrative pacing, and visual style of storybook motion videos:

### Core Philosophy: "Picture-Book Motion"
- **The Canvas is a Page**: Warm editorial parchment background provides continuity while scene artwork cards enter and drift.
- **The Voice is the Conductor**: Visual transitions snap to speech pauses and narrative sentences rather than rigid BPM beats.
- **Movement Serves Focus**:
  - **Scene Entrances**: Gentle Spring Pop (scale 90% &rarr; 102% &rarr; 100% over 350ms) and Cross-Dissolve transitions.
  - **Subtle Life Micro-Drift**: Slow intentional push (3–4% zoom over the scene duration) and harmonic breathing oscillation.
- **Aspect Composition (9:16 Vertical Story)**: Centers artwork in the upper region with drop shadow and reserves the lower third for dark contrast typography cards with dynamic narrative captions.

```
[Raw Voice-Over (.mp3)]   [Scene Script (.txt)]   [Ordered Visuals (.zip)]
           │                       │                       │
           └──────────────┬────────┘                       │
                          ▼                                │
           ┌─────────────────────────────┐                 │
           │   Speech-Cue Align Engine   │                 │
           │  • Audio duration analysis  │                 │
           │  • Narrative pause snapping │                 │
           └──────────────┬──────────────┘                 │
                          ▼                                │
           ┌─────────────────────────────┐                 │
           │   Scene Duration Director   │◄────────────────┘
           │  • Maps Scene[N] -> Img[N]  │
           │  • Allocates timeline plan  │
           └──────────────┬──────────────┘
                          ▼
           ┌─────────────────────────────┐
           │   Visual Choreography Core  │
           │  • Spring-Pop & Paper Cut   │
           │  • Life micro-drift (zoom)  │
           │  • Lower-third captions     │
           └──────────────┬──────────────┘
                          ▼
           ┌─────────────────────────────┐
           │   Final Master Video        │
           │   Exporter (FFmpeg H.264)   │
           │   assets/output/            │
           │   final_story.mp4           │
           └─────────────────────────────┘
```

---

## 🚀 Quickstart: One-Line Installation

Install and configure everything in one command (no manual cloning required):

```bash
curl -fsSL https://raw.githubusercontent.com/AllensCreations/FB-2minutes-Storymaker/main/install.sh | bash
```

This single command automatically:
1. **Detects your system**: **Android (Termux)**, **Debian/Ubuntu**, **macOS**, or generic Linux
2. **Installs packages**: `python-pillow`, `ffmpeg`, `python3`, and `git`
3. **Clones or updates** the repository into `./FB-2minutes-Storymaker`
4. **Prepares demo assets**: Creates the sample story script, illustration cards, and narration audio
5. **Installs global launcher**: Adds the `fb-storymaker` command directly to your PATH

### Ready to Run:

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

### Alternative: Clone & Run via Makefile

If you prefer cloning manually:
```bash
git clone https://github.com/AllensCreations/FB-2minutes-Storymaker.git
cd FB-2minutes-Storymaker

# Automated local setup
make setup

# Run the Storymaker
make tui   # 📱 Interactive Terminal Studio (best for Termux on Android)
make web   # 🌐 Creative Studio Web UI -> http://localhost:8000
make run   # 🎬 Batch Video Render -> assets/output/final_story.mp4
```

---

## 📱 Interactive Termux Terminal UI (TUI)

For Android Termux users who want an interactive dashboard without memorizing command line flags:

```bash
make tui
# or
fb-storymaker --tui
```

```text
┌────────────────────────────────────────────────────────┐
│  FB-2MINUTES STORYMAKER  -  TERMUX CREATIVE STUDIO     │
│  Picture-Book Motion & Narrative Synchronizer          │
└────────────────────────────────────────────────────────┘
  [✓] Narration Audio  : assets/voice-over/narration.mp3
  [✓] Story Script     : assets/scripts/story.txt
  [✓] Visuals (Zip)    : assets/visuals/story_visuals.zip
  [✓] Master Video     : assets/output/final_story.mp4 (4.2 MB)
──────────────────────────────────────────────────────────
  [1] 🎬 Render Master Video (Picture-Book Motion 9:16)
  [2] 🌐 Launch Web Creative Studio (open in Android browser)
  [3] 🔍 Inspect Scene Mapping Matrix & Audio Beats
  [4] ▶️  Play / Watch Rendered Video (Android Player)
  [5] ✨ Switch / Reset Sample Story (Scout & Jem / Elsa)
  [6] 🩺 Termux Dependency Check & Auto-Repair
  [0] 🚪 Exit
```

### Features built specifically for Termux:
- **Zero External Dependencies**: Pure Python 3 ANSI escape codes and UTF-8 box drawing.
- **Live Asset Monitor**: Instantly see if your voice-over, script, and image assets are in place.
- **Live Render Progress**: Real-time rendering percentage bar `[████████░░░░] 67%`.
- **Android Intent Integration**:
  - Automatically opens Web Studio in Android Chrome/Firefox via `termux-open-url`.
  - Automatically opens the rendered `.mp4` directly in your phone's default video player via `termux-open`.
- **Termux Doctor**: Checks for `pkg install -y python-pillow ffmpeg` and repairs missing packages with a single keystroke.


---

## 🌐 Creative Studio: Pure In-Browser Web App

FB-2minutes Storymaker features a complete, zero-dependency **in-browser Creative Studio** (`index.html` & `web/index.html`). It runs 100% in your browser using the HTML5 Canvas, Web Audio API, and MediaRecorder—requiring **zero installation of Python C-libraries or FFmpeg**!

### Launching the Studio:
```bash
make web
# or
python3 -m http.server 8000
# or
fb-storymaker --web
```
Then open **[http://localhost:8000](http://localhost:8000)** in any browser (Chrome, Safari, Firefox, or Android Termux browser).

### The 4-Phase End-to-End Workflow:
1. **Phase 1: Ingestion Deck**
   - Drop `script.txt` (single sentence beats per line).
   - Drop `narration.mp3` or `.wav` (recorded voice-over with 0.3s–0.5s pauses).
   - Drop `scenes.zip` or select individual image files (`01_scout_intro.png`, etc.).
   - *Tip:* Click **"✨ Load Scout & Jem Sample Story"** to instantly load a complete ready-to-test demo with synthesized voice-over, script beats, and illustrations!

2. **Phase 2: Real Waveform & -35dB Silence Detection**
   - Analyzes audio volume envelope and automatically spots natural breathing gaps below **-35dB**.
   - Interactive waveform canvas with **draggable cut markers**: simply drag markers left or right to fine-tune scene cuts.
   - Click anywhere to scrub the playhead.

3. **Phase 3: Scene Mapping Matrix**
   - Interactive matrix table pairing Scene #, Illustration artwork, Narration lines (split into dynamic Beat A &rarr; Beat B), and Start/End timestamps.
   - Customize choreography rules per scene:
     - **Entrances**: Gentle Pop-in (scale $0.94 \to 1.0$), Soft 150ms Dissolve, or Zoom Pop-in.
     - **Continuous Motion**: Camera Push-in (+4% Zoom), Horizontal Pan (+30px slide), or Handheld Subtle Float (breathing sway).

4. **Phase 4: Live 9:16 Canvas & 1-Click Master Export**
   - Watch real-time 30 FPS Picture-Book Motion playback directly on the 9:16 vertical canvas with synced audio and two-beat lower-third captions.
   - Click **"🚀 Export Master Video"** to record the canvas stream and download the finished vertical 1080&times;1920 video directly to your device downloads folder.

---

## 📁 Repository Structure

```
FB-2minutes-Storymaker/
├── src/
│   ├── align_engine/           # Speech-Cue Align Engine
│   │   ├── align_engine.py     # Script parser, audio duration & pause timing
│   │   └── __init__.py
│   ├── duration_director/      # Scene Duration Director
│   │   ├── duration_director.py# Asset resolution, Scene[N] -> Img[N], timeline plan
│   │   └── __init__.py
│   ├── choreography_core/      # Visual Choreography Core
│   │   ├── choreography_core.py# Picture-Book Motion: Spring-pop, micro-drift, captions
│   │   └── __init__.py
│   └── exporter/               # Final Master Video Exporter
│       ├── video_exporter.py   # Raw frame piping to FFmpeg, audio multiplexing
│       └── __init__.py
├── web/
│   ├── index.html              # Creative Studio Web UI
│   └── server.py               # Lightweight zero-dependency Web & API server
├── scripts/
│   └── generate_sample_assets.py # Sample story generator (audio, images, script, zip)
├── assets/
│   ├── voice-over/             # Narration audio (narration.mp3)
│   ├── scripts/                # Story text script (story.txt)
│   ├── visuals/                # Visual illustrations zip (story_visuals.zip)
│   ├── processed/              # Alignment, timeline JSON, extracted frames
│   └── output/                 # Rendered video (final_story.mp4)
├── tests/                      # Automated test suite
│   ├── test_align_engine.py
│   ├── test_duration_director.py
│   └── test_choreography_core.py
├── setup_local.sh              # Local environment setup script
├── Makefile                    # Make targets (setup, run, web, test, clean)
├── main.py                     # Main CLI and pipeline orchestrator
├── requirements.txt            # Python dependencies (Pillow, etc.)
└── setup.py                    # Package configuration
```

---

## 📝 Custom Asset Specification

To create your own custom story video, replace or place files in `assets/`:

### 1. Voice-Over Audio (`assets/voice-over/narration.mp3` or `.wav`)
- Standard MP3 or WAV audio track containing your narration.
- The pipeline reads the duration and cadence to synchronize scene cuts.

### 2. Scene Script (`assets/scripts/story.txt`)
Format your script with `[Scene N: Title]` headers followed by the scene narration:
```text
[Scene 1: Introduction]
In a quiet village nestled between rolling hills, a young baker named Elsa begins her day before sunrise.

[Scene 2: The Problem]
But today, the magical yeast that makes her bread rise has gone missing from her pantry.

[Scene 3: The Journey]
Elsa must venture into the Enchanted Forest to find the legendary Golden Yeast.
```

### 3. Visual Assets (`assets/visuals/story_visuals.zip`)
- A `.zip` archive containing your illustrations (PNG, JPG, or WebP).
- Files should be named with numbers matching the scene sequence (e.g. `scene_1.png`, `scene_2.png`, or `1.png`, `2.png`).
- Resolution: Recommended square (1080x1080) or vertical (1080x1350) artwork. The choreographer automatically scales, adds drop-shadows, and frames the visuals within the 9:16 vertical canvas.

---

## ⚙️ CLI Reference

```bash
# Run the pipeline with default settings
python3 main.py

# Launch Web UI on a specific port
python3 main.py --web --port 8080

# Specify output frame rate (default: 24 fps)
python3 main.py --run --fps 30

# Re-generate bundled demo sample assets
python3 main.py --generate-assets

# Check asset readiness
python3 main.py --check
```

---

## 🛠️ Makefile Commands

| Command | Description |
| :--- | :--- |
| `make setup` | Run automated local setup (`setup_local.sh`) |
| `make run` | Execute the full pipeline and output `assets/output/final_story.mp4` |
| `make web` | Launch the local Web UI on `http://localhost:8000` |
| `make sample-assets` | Regenerate bundled sample story assets |
| `make test` | Run automated unit and integration tests |
| `make clean` | Clean up generated videos, caches, and intermediate files |
| `make format` | Format Python code with `black` and `isort` |
| `make lint` | Lint Python source code with `flake8` |

---

## 🧪 Running Tests

To run the automated test suite:
```bash
make test
```
*(Or `python3 -m unittest discover -s tests -p "test_*.py" -v`)*

---

## 📄 License
MIT License. Created by AllensCreations.