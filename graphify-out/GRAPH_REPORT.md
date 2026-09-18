# Graph Report - FB-2minutes-Storymaker  (2026-09-17)

## Corpus Check
- 29 files · ~38,783 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .zip 1)

## Summary
- 296 nodes · 513 edges · 20 communities (13 shown, 7 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 40 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dac15415`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.py
- VisualChoreographer
- TestAlignEngine
- FB-2minutes Storymaker
- ci_render_and_publish.py
- install.sh
- generate_sample_assets.py
- SpeechCueAlignEngine
- termux_ui.py
- Speech-Cue Align Engine
- End-to-End Workflow: FB 2minutes Storymaker
- setup.py
- setup_local.sh
- choreography_core/README.md
- duration_director/README.md
- exporter/README.md
- 🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com
- video_exporter.py
- vercel.json
- VideoExporter

## God Nodes (most connected - your core abstractions)
1. `SpeechCueAlignEngine` - 25 edges
2. `SceneDurationDirector` - 18 edges
3. `VisualChoreographer` - 17 edges
4. `SceneTimeline` - 14 edges
5. `VideoExporter` - 14 edges
6. `run_video_render()` - 13 edges
7. `run_tui_main()` - 13 edges
8. `FB-2minutes Storymaker` - 12 edges
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

## Communities (20 total, 7 thin omitted)

### Community 0 - "server.py"
Cohesion: 0.13
Nodes (16): http, mimetypes, SimpleHTTPRequestHandler, threading, time, get_assets_status(), get_project_assets_info(), get_story_scenes() (+8 more)

### Community 1 - "VisualChoreographer"
Cohesion: 0.12
Nodes (16): Image, ImageDraw, ImageFont, skipUnless, main(), Draws word-wrapped stroked subtitles inside a TikTok dark pill badge., Computes (scale, offset_x, offset_y) for subtle Ken Burns zoom-in (1.0 -> 1.05)., Renders a single 1080x1920 video frame with: - Heavy blurred background of the… (+8 more)

### Community 3 - "FB-2minutes Storymaker"
Cohesion: 0.08
Nodes (25): 1. Voice-Over Audio (`assets/voice-over/narration.mp3` or `.wav`), 2. Scene Script (`assets/scripts/story.txt`), 3. Visual Assets (`assets/visuals/story_visuals.zip`), Alternative: Clone & Run via Makefile, 🏗️ Architecture, ⚙️ CLI Reference, Core Philosophy: "Picture-Book Motion", 🌐 Creative Studio: Pure In-Browser Web App (+17 more)

### Community 4 - "ci_render_and_publish.py"
Cohesion: 0.11
Nodes (19): handler, Vercel Serverless Function: API Gateway for Google Flow -> GitHub Actions…, base64, BaseHTTPRequestHandler, http_server, json, create_github_release_and_upload(), download_file() (+11 more)

### Community 6 - "generate_sample_assets.py"
Cohesion: 0.18
Nodes (12): argparse, create_gradient(), generate_audio_voiceover(), generate_scene_image(), Path, Draw vertical linear gradient., Generate a high-resolution 1080x1080 scene illustration card., Sample Asset Generator for FB 2minutes Storymaker Creates complete, realistic… (+4 more)

### Community 7 - "SpeechCueAlignEngine"
Cohesion: 0.08
Nodes (29): re, AlignmentResult, main(), Path, Speech-Cue Align Engine for FB 2minutes Storymaker Implements audio analysis…, Parse script file into structured [(scene_title, scene_text)] entries., Represents a segment of speech with timing information., Align speech segments from audio with script scenes based on narrative cadence.… (+21 more)

### Community 8 - "termux_ui.py"
Cohesion: 0.08
Nodes (47): check_assets(), generate_sample_assets(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Starts the local web studio interface., Check if required assets are present in assets/ directory., Invoke the sample asset generator., Executes the full Picture-Book Motion storytelling pipeline. (+39 more)

### Community 9 - "Speech-Cue Align Engine"
Cohesion: 0.12
Nodes (15): 1. Audio Analysis, 2. Speech-Script Alignment, As a Module, Command Line Interface, Core Classes, Dependencies, Functionality, Future Enhancements (+7 more)

### Community 10 - "End-to-End Workflow: FB 2minutes Storymaker"
Cohesion: 0.18
Nodes (10): 1. Script Preparation (`script.txt`), 2. Voice-Over Recording (`narration.mp3` or `.wav`), 3. Visual Asset Packaging (`scenes.zip` or individual images), End-to-End Workflow: FB 2minutes Storymaker, Phase 1: Asset Preparation & Ingestion, Phase 2: Automated Analysis & Timing Alignment, Phase 3: Visual Choreography & Styling Engine, Phase 4: Review & One-Click Master Export (+2 more)

### Community 16 - "🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com"
Cohesion: 0.22
Nodes (8): 1. ⚡ Calling the API from Google Flow, 2. 📦 Payload Sent to Make.com Webhook, 3. 🎯 Setting Up Make.com Scenario, 4. 🔑 Vercel Environment Variables, 🏗️ Architecture Overview, 🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com, Method A: Via Vercel Gateway (Recommended), Method B: Direct to GitHub REST API (Zero Servers)

### Community 17 - "video_exporter.py"
Cohesion: 0.23
Nodes (9): dataclasses, math, pathlib, pil, Visual Choreography Core for FB 2minutes Storymaker Implements "Picture-Book…, Final Master Video Exporter for FB 2minutes Storymaker Pipes generated Picture-…, sys, typing (+1 more)

### Community 18 - "vercel.json"
Cohesion: 0.50
Nodes (3): builds, routes, version

### Community 19 - "VideoExporter"
Cohesion: 0.18
Nodes (7): Path, Renders video frames and multiplexes audio using FFmpeg to export the final…, Find the scene corresponding to timestamp t., Renders the complete story video and exports it to output_path., VideoExporter, Background thread function that executes the full rendering pipeline., run_pipeline_thread()

## Knowledge Gaps
- **48 isolated node(s):** `install.sh script`, `setup_local.sh script`, `version`, `builds`, `routes` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 156 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `TestAlignEngine`, `termux_ui.py`, `Speech-Cue Align Engine`, `video_exporter.py`, `VideoExporter`?**
  _High betweenness centrality (0.155) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `VisualChoreographer` to `video_exporter.py`, `VideoExporter`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `Core Classes` connect `Speech-Cue Align Engine` to `SpeechCueAlignEngine`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and ``SpeechCueAlignEngine``) actually correct?**
  _`SpeechCueAlignEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SceneTimeline` (e.g. with `VisualChoreographer` and `VideoExporter`) actually correct?**
  _`SceneTimeline` has 4 INFERRED edges - model-reasoned connections that need verification._