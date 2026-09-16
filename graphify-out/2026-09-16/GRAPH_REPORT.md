# Graph Report - FB-2minutes-Storymaker  (2026-09-16)

## Corpus Check
- 25 files · ~21,381 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .zip 1)

## Summary
- 247 nodes · 440 edges · 15 communities (9 shown, 6 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 37 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d286276a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.py
- video_exporter.py
- SpeechCueAlignEngine
- FB-2minutes Storymaker
- install.sh
- generate_sample_assets.py
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
3. `VisualChoreographer` - 16 edges
4. `SceneTimeline` - 14 edges
5. `VideoExporter` - 14 edges
6. `run_video_render()` - 13 edges
7. `run_tui_main()` - 13 edges
8. `FB-2minutes Storymaker` - 11 edges
9. `AlignmentResult` - 10 edges
10. `ensure_pillow()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `run_pipeline()` --uses--> `SpeechCueAlignEngine`  [INFERRED]
  main.py → src/align_engine/align_engine.py
- `run_pipeline()` --uses--> `SceneDurationDirector`  [INFERRED]
  main.py → src/duration_director/duration_director.py
- `run_pipeline()` --calls--> `VideoExporter`  [INFERRED]
  main.py → src/exporter/video_exporter.py
- ``SpeechCueAlignEngine`` --references--> `SpeechCueAlignEngine`  [INFERRED]
  src/align_engine/README.md → src/align_engine/align_engine.py
- `TestDurationDirector` --uses--> `SpeechCueAlignEngine`  [INFERRED]
  tests/test_duration_director.py → src/align_engine/align_engine.py

## Import Cycles
- None detected.

## Communities (15 total, 6 thin omitted)

### Community 0 - "server.py"
Cohesion: 0.11
Nodes (18): argparse, http, http_server, mimetypes, SimpleHTTPRequestHandler, threading, urllib_parse, get_assets_status() (+10 more)

### Community 1 - "video_exporter.py"
Cohesion: 0.10
Nodes (22): Image, ImageDraw, ImageFont, pathlib, skipUnless, main(), Visual Choreography Core for FB 2minutes Storymaker Implements "Picture-Book…, Computes (scale, offset_x, offset_y) for continuous Ken Burns zoom-in (1.0 ->… (+14 more)

### Community 2 - "SpeechCueAlignEngine"
Cohesion: 0.11
Nodes (20): dataclasses, json, re, AlignmentResult, main(), Path, Speech-Cue Align Engine for FB 2minutes Storymaker Implements audio analysis…, Align speech segments from audio with script scenes based on narrative cadence.… (+12 more)

### Community 3 - "FB-2minutes Storymaker"
Cohesion: 0.10
Nodes (20): 1. Voice-Over Audio (`assets/voice-over/narration.mp3` or `.wav`), 2. Scene Script (`assets/scripts/story.txt`), 3. Visual Assets (`assets/visuals/story_visuals.zip`), Alternative: Clone & Run via Makefile, ⚙️ CLI Reference, Core Philosophy: "Picture-Book Motion", 🌐 Creative Studio: Pure In-Browser Web App, 📝 Custom Asset Specification (+12 more)

### Community 6 - "generate_sample_assets.py"
Cohesion: 0.15
Nodes (14): math, pil, create_gradient(), generate_audio_voiceover(), generate_scene_image(), Path, Draw vertical linear gradient., Generate a high-resolution 1080x1080 scene illustration card. (+6 more)

### Community 7 - "SceneDurationDirector"
Cohesion: 0.11
Nodes (15): MasterTimeline, Path, Builds the MasterTimeline combining speech alignment segments with visual…, Export timeline manifest to JSON for visual choreographer and exporter., Complete master timeline manifest., Directs scene duration allocation and pairs visual assets with aligned speech…, Locate and order image files from a zip archive or directory. Orders by numeric…, SceneDurationDirector (+7 more)

### Community 8 - "termux_ui.py"
Cohesion: 0.08
Nodes (46): check_assets(), generate_sample_assets(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Check if required assets are present in assets/ directory., Invoke the sample asset generator., Executes the full Picture-Book Motion storytelling pipeline., Starts the local web studio interface. (+38 more)

### Community 9 - "Speech-Cue Align Engine"
Cohesion: 0.12
Nodes (15): 1. Audio Analysis, 2. Speech-Script Alignment, As a Module, Command Line Interface, Core Classes, Dependencies, Functionality, Future Enhancements (+7 more)

### Community 10 - "End-to-End Workflow: FB 2minutes Storymaker"
Cohesion: 0.18
Nodes (10): 1. Script Preparation (`script.txt`), 2. Voice-Over Recording (`narration.mp3` or `.wav`), 3. Visual Asset Packaging (`scenes.zip` or individual images), End-to-End Workflow: FB 2minutes Storymaker, Phase 1: Asset Preparation & Ingestion, Phase 2: Automated Analysis & Timing Alignment, Phase 3: Visual Choreography & Styling Engine, Phase 4: Review & One-Click Master Export (+2 more)

## Knowledge Gaps
- **35 isolated node(s):** `install.sh script`, `setup_local.sh script`, `1. Script Preparation (`script.txt`)`, `2. Voice-Over Recording (`narration.mp3` or `.wav`)`, `3. Visual Asset Packaging (`scenes.zip` or individual images)` (+30 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 127 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `server.py`, `video_exporter.py`, `SceneDurationDirector`, `termux_ui.py`, `Speech-Cue Align Engine`?**
  _High betweenness centrality (0.171) - this node is a cross-community bridge._
- **Why does `Core Classes` connect `Speech-Cue Align Engine` to `SpeechCueAlignEngine`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `video_exporter.py` to `SceneDurationDirector`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and ``SpeechCueAlignEngine``) actually correct?**
  _`SpeechCueAlignEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SceneTimeline` (e.g. with `VisualChoreographer` and `VideoExporter`) actually correct?**
  _`SceneTimeline` has 4 INFERRED edges - model-reasoned connections that need verification._