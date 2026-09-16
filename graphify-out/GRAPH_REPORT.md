# Graph Report - FB-2minutes-Storymaker  (2026-09-16)

## Corpus Check
- 25 files · ~22,428 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .zip 1)

## Summary
- 244 nodes · 436 edges · 16 communities (10 shown, 6 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 37 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c0ccf384`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_pipeline_thread
- video_exporter.py
- SpeechCueAlignEngine
- FB-2minutes Storymaker
- server.py
- install.sh
- main.py
- SceneDurationDirector
- termux_ui.py
- Speech-Cue Align Engine
- End-to-End Workflow: FB 2minutes Storymaker
- setup.py
- setup_local.sh
- choreography_core/README.md
- duration_director/README.md
- exporter/README.md

## God Nodes (most connected - your core abstractions)
1. `SpeechCueAlignEngine` - 24 edges
2. `SceneDurationDirector` - 18 edges
3. `VisualChoreographer` - 15 edges
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
- `run_pipeline()` --uses--> `SpeechCueAlignEngine`  [INFERRED]
  main.py → src/align_engine/align_engine.py
- `run_pipeline()` --uses--> `SceneDurationDirector`  [INFERRED]
  main.py → src/duration_director/duration_director.py
- `run_pipeline()` --calls--> `VideoExporter`  [INFERRED]
  main.py → src/exporter/video_exporter.py
- `start_web_server()` --calls--> `ensure_pillow()`  [INFERRED]
  main.py → src/deps_helper.py

## Import Cycles
- None detected.

## Communities (16 total, 6 thin omitted)

### Community 0 - "run_pipeline_thread"
Cohesion: 0.15
Nodes (11): SimpleHTTPRequestHandler, get_assets_status(), get_story_scenes(), Path, Background thread function that executes the full rendering pipeline., Custom HTTP request handler serving Web UI and storymaker APIs., Supports HTTP 206 Partial Content for streaming/scrubbing in HTML5 video., Check existence and metadata of required assets. (+3 more)

### Community 1 - "video_exporter.py"
Cohesion: 0.08
Nodes (24): dataclasses, Image, ImageDraw, math, skipUnless, main(), Visual Choreography Core for FB 2minutes Storymaker Implements "Picture-Book…, Renders a single 1080x1920 video frame for the given scene and timestamp. (+16 more)

### Community 2 - "SpeechCueAlignEngine"
Cohesion: 0.16
Nodes (8): Path, Align speech segments from audio with script scenes based on narrative cadence.…, Export alignment to both human-readable text and JSON., Analyzes voice-over audio and aligns it with scene scripts to determine optimal…, Get exact duration of audio file in seconds via ffprobe or wave/fallback., Parse script file into structured [(scene_title, scene_text)] entries. Supports…, SpeechCueAlignEngine, TestAlignEngine

### Community 3 - "FB-2minutes Storymaker"
Cohesion: 0.10
Nodes (20): 1. Voice-Over Audio (`assets/voice-over/narration.mp3` or `.wav`), 2. Scene Script (`assets/scripts/story.txt`), 3. Visual Assets (`assets/visuals/story_visuals.zip`), Alternative: Clone & Run via Makefile, ⚙️ CLI Reference, Core Philosophy: "Picture-Book Motion", 🌐 Creative Studio: Pure In-Browser Web App, 📝 Custom Asset Specification (+12 more)

### Community 4 - "server.py"
Cohesion: 0.14
Nodes (16): http, http_server, json, mimetypes, pathlib, re, main(), Speech-Cue Align Engine for FB 2minutes Storymaker Implements audio analysis… (+8 more)

### Community 6 - "main.py"
Cohesion: 0.10
Nodes (24): argparse, check_assets(), generate_sample_assets(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Check if required assets are present in assets/ directory., Invoke the sample asset generator., Starts the local web studio interface. (+16 more)

### Community 7 - "SceneDurationDirector"
Cohesion: 0.15
Nodes (13): AlignmentResult, Result of aligning speech segments with visual scenes., main(), MasterTimeline, Path, Scene Duration Director for FB 2minutes Storymaker Maps Scene[N] -> Img[N],…, Builds the MasterTimeline combining speech alignment segments with visual…, Export timeline manifest to JSON for visual choreographer and exporter. (+5 more)

### Community 8 - "termux_ui.py"
Cohesion: 0.10
Nodes (36): Executes the full Picture-Book Motion storytelling pipeline., run_pipeline(), shutil, ensure_ffmpeg(), ensure_pillow(), is_root(), is_termux(), Dependency Helper for FB 2minutes Storymaker Detects platform (Termux, Linux,… (+28 more)

### Community 9 - "Speech-Cue Align Engine"
Cohesion: 0.12
Nodes (16): 1. Audio Analysis, 2. Speech-Script Alignment, As a Module, Command Line Interface, Core Classes, Data Classes, Dependencies, Functionality (+8 more)

### Community 10 - "End-to-End Workflow: FB 2minutes Storymaker"
Cohesion: 0.18
Nodes (10): 1. Script Preparation (`script.txt`), 2. Voice-Over Recording (`narration.mp3` or `.wav`), 3. Visual Asset Packaging (`scenes.zip` or individual images), End-to-End Workflow: FB 2minutes Storymaker, Phase 1: Asset Preparation & Ingestion, Phase 2: Automated Analysis & Timing Alignment, Phase 3: Visual Choreography & Styling Engine, Phase 4: Review & One-Click Master Export (+2 more)

## Knowledge Gaps
- **35 isolated node(s):** `install.sh script`, `setup_local.sh script`, `1. Script Preparation (`script.txt`)`, `2. Voice-Over Recording (`narration.mp3` or `.wav`)`, `3. Visual Asset Packaging (`scenes.zip` or individual images)` (+30 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 125 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `run_pipeline_thread`, `video_exporter.py`, `server.py`, `SceneDurationDirector`, `termux_ui.py`, `Speech-Cue Align Engine`?**
  _High betweenness centrality (0.172) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and ``SpeechCueAlignEngine``) actually correct?**
  _`SpeechCueAlignEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SceneTimeline` (e.g. with `VisualChoreographer` and `VideoExporter`) actually correct?**
  _`SceneTimeline` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `VideoExporter` (e.g. with `run_pipeline()` and `VisualChoreographer`) actually correct?**
  _`VideoExporter` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `install.sh script`, `setup_local.sh script`, `1. Script Preparation (`script.txt`)` to the rest of the system?**
  _35 weakly-connected nodes found - possible documentation gaps or missing edges._