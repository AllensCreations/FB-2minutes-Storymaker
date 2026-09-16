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

## 🚀 Quickstart: Running Locally

### 1. Prerequisites
- **Python 3.8+**
- **FFmpeg** (required for video rendering and audio multiplexing)
  - **Ubuntu / Debian**: `sudo apt update && sudo apt install -y ffmpeg`
  - **macOS (Homebrew)**: `brew install ffmpeg`
  - **Windows**: `winget install Gyan.FFmpeg` or `choco install ffmpeg`

### 2. Automated One-Command Setup
Clone the repository and run the setup script:
```bash
git clone https://github.com/AllensCreations/FB-2minutes-Storymaker.git
cd FB-2minutes-Storymaker

# One-command environment setup (checks ffmpeg, python, dependencies, sample assets)
make setup
```
*(Alternatively: `./setup_local.sh`)*

### 3. Generate the Master Video via CLI
To run the full end-to-end rendering pipeline:
```bash
make run
```
*(Or `python3 main.py`)*

Output video will be saved to:
`assets/output/final_story.mp4`

---

## 🌐 Creative Studio Web UI

FB-2minutes Storymaker includes a modern, zero-dependency local Web UI (`web/index.html`) tailored for story creators.

### Launching the Web UI:
```bash
make web
```
*(Or `python3 main.py --web --port 8000`)*

Then open **[http://localhost:8000](http://localhost:8000)** in your browser.

### Web UI Features:
1. **Asset Readiness Monitor**: Live indicators checking your voice-over (`narration.mp3`), scene script (`story.txt`), and visual assets archive (`story_visuals.zip`).
2. **Master Video Theater**: An interactive 9:16 vertical video player previewing `final_story.mp4` with stream scrubbing, timecode, and direct `.mp4` download.
3. **One-Click Render Station**: "✨ Render Master Video" button with a real-time progress bar, frame rate counter, ETA, and activity log.
4. **Storyboard & Scene Visualizer**: Interactive scene cards showing scene artwork thumbnails, script text, duration timings, and animation types.
5. **Narration Audio Preview**: In-browser audio player to review the narration audio track before generating.
6. **Demo Asset Reset**: "🎨 Refresh Assets" button to reload the bundled sample fairytale story at any time.

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