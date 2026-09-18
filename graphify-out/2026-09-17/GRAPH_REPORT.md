# Graph Report - FB-2minutes-Storymaker  (2026-09-17)

## Corpus Check
- 25 files · ~36,165 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .zip 1)

## Summary
- 257 nodes · 460 edges · 17 communities (10 shown, 7 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 40 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0e1565cf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.py
- VisualChoreographer
- SpeechCueAlignEngine
- FB-2minutes Storymaker
- .resolve_visual_assets
- install.sh
- generate_sample_assets.py
- video_exporter.py
- termux_ui.py
- Speech-Cue Align Engine
- End-to-End Workflow: FB 2minutes Storymaker
- setup.py
- setup_local.sh
- choreography_core/README.md
- duration_director/README.md
- exporter/README.md
- TestAlignEngine

## God Nodes (most connected - your core abstractions)
1. `SpeechCueAlignEngine` - 25 edges
2. `SceneDurationDirector` - 18 edges
3. `VisualChoreographer` - 17 edges
4. `SceneTimeline` - 14 edges
5. `VideoExporter` - 14 edges
6. `run_video_render()` - 13 edges
7. `run_tui_main()` - 13 edges
8. `FB-2minutes Storymaker` - 11 edges
9. `AlignmentResult` - 10 edges
10. `ensure_pillow()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `generate_sample_assets()` --calls--> `ensure_pillow()`  [INFERRED]
  main.py → src/deps_helper.py
- `run_pipeline()` --calls--> `ensure_ffmpeg()`  [INFERRED]
  main.py → src/deps_helper.py
- `run_pipeline()` --calls--> `ensure_pillow()`  [INFERRED]
  main.py → src/deps_helper.py
- `run_pipeline()` --calls--> `VideoExporter`  [INFERRED]
  main.py → src/exporter/video_exporter.py
- `start_web_server()` --calls--> `ensure_pillow()`  [INFERRED]
  main.py → src/deps_helper.py

## Import Cycles
- None detected.

## Communities (17 total, 7 thin omitted)

### Community 0 - "server.py"
Cohesion: 0.10
Nodes (20): http, http_server, mimetypes, SimpleHTTPRequestHandler, threading, time, urllib_parse, get_assets_status() (+12 more)

### Community 1 - "VisualChoreographer"
Cohesion: 0.12
Nodes (13): Image, ImageDraw, ImageFont, skipUnless, Draws word-wrapped stroked subtitles inside a TikTok dark pill badge., Computes (scale, offset_x, offset_y) for subtle Ken Burns zoom-in (1.0 -> 1.05)., Renders a single 1080x1920 video frame with: - Heavy blurred background of the…, Renders video frames applying Picture-Book Motion choreographic rules. (+5 more)

### Community 2 - "SpeechCueAlignEngine"
Cohesion: 0.10
Nodes (26): dataclasses, json, Executes the full Picture-Book Motion storytelling pipeline., run_pipeline(), re, AlignmentResult, main(), Path (+18 more)

### Community 3 - "FB-2minutes Storymaker"
Cohesion: 0.10
Nodes (20): 1. Voice-Over Audio (`assets/voice-over/narration.mp3` or `.wav`), 2. Scene Script (`assets/scripts/story.txt`), 3. Visual Assets (`assets/visuals/story_visuals.zip`), Alternative: Clone & Run via Makefile, ⚙️ CLI Reference, Core Philosophy: "Picture-Book Motion", 🌐 Creative Studio: Pure In-Browser Web App, 📝 Custom Asset Specification (+12 more)

### Community 4 - ".resolve_visual_assets"
Cohesion: 0.29
Nodes (3): Path, Export timeline manifest to JSON for visual choreographer and exporter., Locate and order image files from a zip archive or directory. Orders by numeric…

### Community 6 - "generate_sample_assets.py"
Cohesion: 0.09
Nodes (29): argparse, check_assets(), generate_sample_assets(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Starts the local web studio interface., Check if required assets are present in assets/ directory., Invoke the sample asset generator. (+21 more)

### Community 7 - "video_exporter.py"
Cohesion: 0.13
Nodes (17): pathlib, main(), Visual Choreography Core for FB 2minutes Storymaker Implements "Picture-Book…, MasterTimeline, Builds the MasterTimeline combining speech alignment segments with visual…, Represents a scheduled scene in the master video timeline., Complete master timeline manifest., SceneTimeline (+9 more)

### Community 8 - "termux_ui.py"
Cohesion: 0.11
Nodes (31): shutil, ensure_ffmpeg(), ensure_pillow(), is_root(), is_termux(), Dependency Helper for FB 2minutes Storymaker Detects platform (Termux, Linux,…, Checks if ffmpeg is on PATH. If missing, attempts auto-install on Termux or…, Detect if running in Termux on Android. (+23 more)

### Community 9 - "Speech-Cue Align Engine"
Cohesion: 0.12
Nodes (15): 1. Audio Analysis, 2. Speech-Script Alignment, As a Module, Command Line Interface, Core Classes, Dependencies, Functionality, Future Enhancements (+7 more)

### Community 10 - "End-to-End Workflow: FB 2minutes Storymaker"
Cohesion: 0.18
Nodes (10): 1. Script Preparation (`script.txt`), 2. Voice-Over Recording (`narration.mp3` or `.wav`), 3. Visual Asset Packaging (`scenes.zip` or individual images), End-to-End Workflow: FB 2minutes Storymaker, Phase 1: Asset Preparation & Ingestion, Phase 2: Automated Analysis & Timing Alignment, Phase 3: Visual Choreography & Styling Engine, Phase 4: Review & One-Click Master Export (+2 more)

## Knowledge Gaps
- **35 isolated node(s):** `install.sh script`, `setup_local.sh script`, `1. Script Preparation (`script.txt`)`, `2. Voice-Over Recording (`narration.mp3` or `.wav`)`, `3. Visual Asset Packaging (`scenes.zip` or individual images)` (+30 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 133 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `server.py`, `video_exporter.py`, `termux_ui.py`, `Speech-Cue Align Engine`, `TestAlignEngine`?**
  _High betweenness centrality (0.184) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `VisualChoreographer` to `video_exporter.py`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `Core Classes` connect `Speech-Cue Align Engine` to `SpeechCueAlignEngine`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and ``SpeechCueAlignEngine``) actually correct?**
  _`SpeechCueAlignEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SceneTimeline` (e.g. with `VisualChoreographer` and `VideoExporter`) actually correct?**
  _`SceneTimeline` has 4 INFERRED edges - model-reasoned connections that need verification._