# Graph Report - FB-2minutes-Storymaker  (2026-09-17)

## Corpus Check
- 29 files · ~38,134 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .zip 1)

## Summary
- 291 nodes · 508 edges · 19 communities (12 shown, 7 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 40 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1823bcd8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_pipeline_thread
- VisualChoreographer
- SpeechCueAlignEngine
- FB-2minutes Storymaker
- server.py
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
- 🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com
- handler
- vercel.json

## God Nodes (most connected - your core abstractions)
1. `SpeechCueAlignEngine` - 25 edges
2. `SceneDurationDirector` - 18 edges
3. `VisualChoreographer` - 17 edges
4. `SceneTimeline` - 14 edges
5. `VideoExporter` - 14 edges
6. `run_video_render()` - 13 edges
7. `run_tui_main()` - 13 edges
8. `FB-2minutes Storymaker` - 11 edges
9. `run_pipeline()` - 10 edges
10. `AlignmentResult` - 10 edges

## Surprising Connections (you probably didn't know these)
- `run_pipeline()` --uses--> `SpeechCueAlignEngine`  [INFERRED]
  main.py → src/align_engine/align_engine.py
- `run_pipeline()` --uses--> `SceneDurationDirector`  [INFERRED]
  main.py → src/duration_director/duration_director.py
- `run_pipeline()` --calls--> `VideoExporter`  [INFERRED]
  main.py → src/exporter/video_exporter.py
- `TestAlignEngine` --uses--> `AlignmentResult`  [INFERRED]
  tests/test_align_engine.py → src/align_engine/align_engine.py
- ``SpeechCueAlignEngine`` --references--> `SpeechCueAlignEngine`  [INFERRED]
  src/align_engine/README.md → src/align_engine/align_engine.py

## Import Cycles
- None detected.

## Communities (19 total, 7 thin omitted)

### Community 0 - "run_pipeline_thread"
Cohesion: 0.14
Nodes (13): SimpleHTTPRequestHandler, get_assets_status(), get_project_assets_info(), get_story_scenes(), Path, Returns full metadata and content for preloading local Termux assets into Web…, Background thread function that executes the full rendering pipeline., Custom HTTP request handler serving Web UI and storymaker APIs. (+5 more)

### Community 1 - "VisualChoreographer"
Cohesion: 0.12
Nodes (13): Image, ImageDraw, ImageFont, skipUnless, Draws word-wrapped stroked subtitles inside a TikTok dark pill badge., Computes (scale, offset_x, offset_y) for subtle Ken Burns zoom-in (1.0 -> 1.05)., Renders a single 1080x1920 video frame with: - Heavy blurred background of the…, Renders video frames applying Picture-Book Motion choreographic rules. (+5 more)

### Community 2 - "SpeechCueAlignEngine"
Cohesion: 0.11
Nodes (10): main(), Path, Parse script file into structured [(scene_title, scene_text)] entries., Export alignment to both human-readable text and JSON., Analyzes voice-over audio and aligns it with scene scripts to determine optimal…, Get exact duration of audio file in seconds via ffprobe or wave/fallback., Parses script content string into structured [(scene_title, scene_text)]…, SpeechCueAlignEngine (+2 more)

### Community 3 - "FB-2minutes Storymaker"
Cohesion: 0.10
Nodes (20): 1. Voice-Over Audio (`assets/voice-over/narration.mp3` or `.wav`), 2. Scene Script (`assets/scripts/story.txt`), 3. Visual Assets (`assets/visuals/story_visuals.zip`), Alternative: Clone & Run via Makefile, ⚙️ CLI Reference, Core Philosophy: "Picture-Book Motion", 🌐 Creative Studio: Pure In-Browser Web App, 📝 Custom Asset Specification (+12 more)

### Community 4 - "server.py"
Cohesion: 0.08
Nodes (31): Vercel Serverless Function: API Gateway for Google Flow -> GitHub Actions…, base64, http, http_server, json, check_assets(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Check if required assets are present in assets/ directory. (+23 more)

### Community 6 - "generate_sample_assets.py"
Cohesion: 0.15
Nodes (14): argparse, math, pil, create_gradient(), generate_audio_voiceover(), generate_scene_image(), Path, Draw vertical linear gradient. (+6 more)

### Community 7 - "SceneDurationDirector"
Cohesion: 0.08
Nodes (29): dataclasses, AlignmentResult, Represents a segment of speech with timing information., Align speech segments from audio with script scenes based on narrative cadence.…, Result of aligning speech segments with visual scenes., SpeechSegment, Data Classes, main() (+21 more)

### Community 8 - "termux_ui.py"
Cohesion: 0.08
Nodes (44): generate_sample_assets(), main(), Starts the local web studio interface., Invoke the sample asset generator., Executes the full Picture-Book Motion storytelling pipeline., run_pipeline(), start_web_server(), generate_all_sample_assets() (+36 more)

### Community 9 - "Speech-Cue Align Engine"
Cohesion: 0.12
Nodes (15): 1. Audio Analysis, 2. Speech-Script Alignment, As a Module, Command Line Interface, Core Classes, Dependencies, Functionality, Future Enhancements (+7 more)

### Community 10 - "End-to-End Workflow: FB 2minutes Storymaker"
Cohesion: 0.18
Nodes (10): 1. Script Preparation (`script.txt`), 2. Voice-Over Recording (`narration.mp3` or `.wav`), 3. Visual Asset Packaging (`scenes.zip` or individual images), End-to-End Workflow: FB 2minutes Storymaker, Phase 1: Asset Preparation & Ingestion, Phase 2: Automated Analysis & Timing Alignment, Phase 3: Visual Choreography & Styling Engine, Phase 4: Review & One-Click Master Export (+2 more)

### Community 16 - "🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com"
Cohesion: 0.22
Nodes (8): 1. ⚡ Calling the API from Google Flow, 2. 📦 Payload Sent to Make.com Webhook, 3. 🎯 Setting Up Make.com Scenario, 4. 🔑 Vercel Environment Variables, 🏗️ Architecture Overview, 🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com, Method A: Via Vercel Gateway (Recommended), Method B: Direct to GitHub REST API (Zero Servers)

### Community 18 - "vercel.json"
Cohesion: 0.50
Nodes (3): builds, routes, version

## Knowledge Gaps
- **44 isolated node(s):** `install.sh script`, `setup_local.sh script`, `version`, `builds`, `routes` (+39 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 152 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `run_pipeline_thread`, `server.py`, `SceneDurationDirector`, `termux_ui.py`, `Speech-Cue Align Engine`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `VisualChoreographer` to `SceneDurationDirector`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `Core Classes` connect `Speech-Cue Align Engine` to `SceneDurationDirector`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and ``SpeechCueAlignEngine``) actually correct?**
  _`SpeechCueAlignEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SceneTimeline` (e.g. with `VisualChoreographer` and `VideoExporter`) actually correct?**
  _`SceneTimeline` has 4 INFERRED edges - model-reasoned connections that need verification._