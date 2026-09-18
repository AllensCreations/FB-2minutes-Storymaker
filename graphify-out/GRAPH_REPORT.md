# Graph Report - FB-2minutes-Storymaker  (2026-09-18)

## Corpus Check
- 32 files · ~40,967 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .zip 1)

## Summary
- 319 nodes · 553 edges · 21 communities (12 shown, 9 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 42 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a2f33ebc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.py
- VisualChoreographer
- os
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
- TestAlignEngine
- render.js

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
- `TestAlignEngine` --uses--> `AlignmentResult`  [INFERRED]
  tests/test_align_engine.py → src/align_engine/align_engine.py
- ``SpeechCueAlignEngine`` --references--> `SpeechCueAlignEngine`  [INFERRED]
  src/align_engine/README.md → src/align_engine/align_engine.py

## Import Cycles
- None detected.

## Communities (21 total, 9 thin omitted)

### Community 0 - "server.py"
Cohesion: 0.14
Nodes (15): http, mimetypes, SimpleHTTPRequestHandler, threading, get_assets_status(), get_project_assets_info(), get_story_scenes(), Path (+7 more)

### Community 1 - "VisualChoreographer"
Cohesion: 0.08
Nodes (24): Image, ImageDraw, ImageFont, pathlib, skipUnless, main(), Visual Choreography Core for FB 2minutes Storymaker Implements "Picture-Book…, Draws word-wrapped stroked subtitles inside a TikTok dark pill badge. (+16 more)

### Community 2 - "os"
Cohesion: 0.10
Nodes (14): handler, Vercel Serverless Function: API Gateway for Google Flow -> GitHub Actions…, BaseHTTPRequestHandler, http_server, io, json, os, patch (+6 more)

### Community 3 - "FB-2minutes Storymaker"
Cohesion: 0.08
Nodes (25): 1. Voice-Over Audio (`assets/voice-over/narration.mp3` or `.wav`), 2. Scene Script (`assets/scripts/story.txt`), 3. Visual Assets (`assets/visuals/story_visuals.zip`), Alternative: Clone & Run via Makefile, 🏗️ Architecture, ⚙️ CLI Reference, Core Philosophy: "Picture-Book Motion", 🌐 Creative Studio: Pure In-Browser Web App (+17 more)

### Community 4 - "ci_render_and_publish.py"
Cohesion: 0.19
Nodes (14): base64, create_github_release_and_upload(), download_file(), main(), notify_make_webhook(), Path, Sends the minimal payload to Make.com incoming webhook. Payload: { video_url,…, CI Render & Publish Helper for GitHub Actions & Make.com Automation Handles… (+6 more)

### Community 6 - "generate_sample_assets.py"
Cohesion: 0.16
Nodes (13): argparse, math, pil, create_gradient(), generate_audio_voiceover(), generate_scene_image(), Path, Draw vertical linear gradient. (+5 more)

### Community 7 - "SpeechCueAlignEngine"
Cohesion: 0.08
Nodes (29): dataclasses, re, AlignmentResult, main(), Path, Speech-Cue Align Engine for FB 2minutes Storymaker Implements audio analysis…, Parse script file into structured [(scene_title, scene_text)] entries., Represents a segment of speech with timing information. (+21 more)

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
Cohesion: 0.20
Nodes (9): 1. ⚡ Calling the API from Google Flow, 2. 📦 Payload Sent to Make.com Webhook, 3. 🎯 Setting Up Make.com Scenario, 4. 🔑 Vercel Environment Variables, 🏗️ Architecture Overview, 🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com, Detailed Confirmation Response from Vercel (`202 Accepted`):, Method A: Via Vercel Gateway (Recommended) (+1 more)

### Community 17 - "VideoExporter"
Cohesion: 0.18
Nodes (7): Path, Renders video frames and multiplexes audio using FFmpeg to export the final…, Find the scene corresponding to timestamp t., Renders the complete story video and exports it to output_path., VideoExporter, Background thread function that executes the full rendering pipeline., run_pipeline_thread()

## Knowledge Gaps
- **47 isolated node(s):** `install.sh script`, `setup_local.sh script`, `rewrites`, `headers`, `1. Script Preparation (`script.txt`)` (+42 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 163 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `VisualChoreographer`, `termux_ui.py`, `Speech-Cue Align Engine`, `VideoExporter`, `TestAlignEngine`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `VisualChoreographer` to `VideoExporter`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `Core Classes` connect `Speech-Cue Align Engine` to `SpeechCueAlignEngine`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and ``SpeechCueAlignEngine``) actually correct?**
  _`SpeechCueAlignEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SceneTimeline` (e.g. with `VisualChoreographer` and `VideoExporter`) actually correct?**
  _`SceneTimeline` has 5 INFERRED edges - model-reasoned connections that need verification._