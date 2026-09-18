# Graph Report - FB-2minutes-Storymaker  (2026-09-18)

## Corpus Check
- 30 files · ~40,359 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .zip 1)

## Summary
- 305 nodes · 525 edges · 25 communities (12 shown, 13 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 41 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2ff495df`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.py
- VisualChoreographer
- video_exporter.py
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
- VideoExporter
- vercel.json
- TestApiGatewayNode
- io
- render
- unittest_mock
- urllib_error

## God Nodes (most connected - your core abstractions)
1. `SpeechCueAlignEngine` - 25 edges
2. `VisualChoreographer` - 18 edges
3. `SceneDurationDirector` - 18 edges
4. `SceneTimeline` - 16 edges
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
- ``SpeechCueAlignEngine`` --references--> `SpeechCueAlignEngine`  [INFERRED]
  src/align_engine/README.md → src/align_engine/align_engine.py
- `run_pipeline_thread()` --calls--> `ensure_pillow()`  [INFERRED]
  web/server.py → src/deps_helper.py

## Import Cycles
- None detected.

## Communities (25 total, 13 thin omitted)

### Community 0 - "server.py"
Cohesion: 0.13
Nodes (16): http, http_server, mimetypes, SimpleHTTPRequestHandler, threading, get_assets_status(), get_project_assets_info(), get_story_scenes() (+8 more)

### Community 1 - "VisualChoreographer"
Cohesion: 0.10
Nodes (18): Image, ImageDraw, ImageFont, skipUnless, main(), Visual Choreography Core for FB 2minutes Storymaker Implements "Picture-Book…, Draws word-wrapped stroked subtitles inside a TikTok dark pill badge., Computes (scale, offset_x, offset_y) for smooth cinematic push-in & drift.… (+10 more)

### Community 2 - "video_exporter.py"
Cohesion: 0.27
Nodes (7): pathlib, Final Master Video Exporter for FB 2minutes Storymaker Pipes generated Picture-…, subprocess, sys, time, typing, unittest

### Community 3 - "FB-2minutes Storymaker"
Cohesion: 0.08
Nodes (25): 1. Voice-Over Audio (`assets/voice-over/narration.mp3` or `.wav`), 2. Scene Script (`assets/scripts/story.txt`), 3. Visual Assets (`assets/visuals/story_visuals.zip`), Alternative: Clone & Run via Makefile, 🏗️ Architecture, ⚙️ CLI Reference, Core Philosophy: "Picture-Book Motion", 🌐 Creative Studio: Pure In-Browser Web App (+17 more)

### Community 4 - "ci_render_and_publish.py"
Cohesion: 0.17
Nodes (15): base64, os, create_github_release_and_upload(), download_file(), main(), notify_make_webhook(), Path, Sends the minimal payload to Make.com incoming webhook. Payload: { video_url,… (+7 more)

### Community 6 - "generate_sample_assets.py"
Cohesion: 0.15
Nodes (14): argparse, math, pil, create_gradient(), generate_audio_voiceover(), generate_scene_image(), Path, Draw vertical linear gradient. (+6 more)

### Community 7 - "SpeechCueAlignEngine"
Cohesion: 0.07
Nodes (27): dataclasses, json, re, AlignmentResult, main(), Path, Speech-Cue Align Engine for FB 2minutes Storymaker Implements audio analysis…, Parse script file into structured [(scene_title, scene_text)] entries. (+19 more)

### Community 8 - "termux_ui.py"
Cohesion: 0.08
Nodes (46): check_assets(), generate_sample_assets(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Starts the local web studio interface., Check if required assets are present in assets/ directory., Invoke the sample asset generator., Executes the full Picture-Book Motion storytelling pipeline. (+38 more)

### Community 9 - "Speech-Cue Align Engine"
Cohesion: 0.12
Nodes (15): 1. Audio Analysis, 2. Speech-Script Alignment, As a Module, Command Line Interface, Core Classes, Dependencies, Functionality, Future Enhancements (+7 more)

### Community 10 - "End-to-End Workflow: FB 2minutes Storymaker"
Cohesion: 0.18
Nodes (10): 1. Script Preparation (`script.txt`), 2. Voice-Over Recording (`narration.mp3` or `.wav`), 3. Visual Asset Packaging (`scenes.zip` or individual images), End-to-End Workflow: FB 2minutes Storymaker, Phase 1: Asset Preparation & Ingestion, Phase 2: Automated Analysis & Timing Alignment, Phase 3: Visual Choreography & Styling Engine, Phase 4: Review & One-Click Master Export (+2 more)

### Community 16 - "🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com"
Cohesion: 0.20
Nodes (9): 1. ⚡ Calling the API from Google Flow, 2. 📦 Payload Sent to Make.com Webhook, 3. 🎯 Setting Up Make.com Scenario, 4. 🔑 Vercel Environment Variables, 🏗️ Architecture Overview, 🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com, Detailed Confirmation Response from Vercel (`202 Accepted`):, Method A: Via Vercel Gateway (Recommended) (+1 more)

### Community 17 - "VideoExporter"
Cohesion: 0.13
Nodes (11): MasterTimeline, Path, Builds the MasterTimeline combining speech alignment segments with visual…, Export timeline manifest to JSON for visual choreographer and exporter., Complete master timeline manifest., Locate and order image files from a zip archive or directory. Orders by numeric…, Path, Renders video frames and multiplexes audio using FFmpeg to export the final… (+3 more)

## Knowledge Gaps
- **47 isolated node(s):** `install.sh script`, `setup_local.sh script`, `rewrites`, `headers`, `1. Script Preparation (`script.txt`)` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 159 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `termux_ui.py`, `Speech-Cue Align Engine`, `video_exporter.py`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `VisualChoreographer` to `VideoExporter`, `video_exporter.py`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `Core Classes` connect `Speech-Cue Align Engine` to `SpeechCueAlignEngine`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and ``SpeechCueAlignEngine``) actually correct?**
  _`SpeechCueAlignEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SceneTimeline` (e.g. with `VisualChoreographer` and `VideoExporter`) actually correct?**
  _`SceneTimeline` has 5 INFERRED edges - model-reasoned connections that need verification._