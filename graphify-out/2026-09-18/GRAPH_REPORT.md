# Graph Report - FB-2minutes-Storymaker  (2026-09-18)

## Corpus Check
- 34 files · ~41,193 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 3, .zip 1, .lock 1)

## Summary
- 344 nodes · 580 edges · 28 communities (15 shown, 13 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 44 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `53e2ad41`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- StorymakerRequestHandler
- VisualChoreographer
- fb-2minutes-storymaker
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
- SceneDurationDirector
- vercel.json
- TestApiGatewayNode
- io
- render
- unittest_mock
- urllib_error
- app.py
- run_tui_main
- TestServerlessApp

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
- `main()` --calls--> `run_tui_main()`  [INFERRED]
  main.py → src/termux_ui.py
- `TestDurationDirector` --uses--> `SpeechCueAlignEngine`  [INFERRED]
  tests/test_duration_director.py → src/align_engine/align_engine.py

## Import Cycles
- None detected.

## Communities (28 total, 13 thin omitted)

### Community 0 - "StorymakerRequestHandler"
Cohesion: 0.17
Nodes (11): SimpleHTTPRequestHandler, get_assets_status(), get_project_assets_info(), get_story_scenes(), Path, Returns full metadata and content for preloading local Termux assets into Web…, Custom HTTP request handler serving Web UI and storymaker APIs., Supports HTTP 206 Partial Content for streaming/scrubbing in HTML5 video. (+3 more)

### Community 1 - "VisualChoreographer"
Cohesion: 0.10
Nodes (19): dataclasses, Image, ImageDraw, ImageFont, skipUnless, main(), Visual Choreography Core for FB 2minutes Storymaker Implements "Picture-Book…, Draws word-wrapped stroked subtitles inside a TikTok dark pill badge. (+11 more)

### Community 3 - "FB-2minutes Storymaker"
Cohesion: 0.08
Nodes (25): 1. Voice-Over Audio (`assets/voice-over/narration.mp3` or `.wav`), 2. Scene Script (`assets/scripts/story.txt`), 3. Visual Assets (`assets/visuals/story_visuals.zip`), Alternative: Clone & Run via Makefile, 🏗️ Architecture, ⚙️ CLI Reference, Core Philosophy: "Picture-Book Motion", 🌐 Creative Studio: Pure In-Browser Web App (+17 more)

### Community 4 - "ci_render_and_publish.py"
Cohesion: 0.21
Nodes (13): create_github_release_and_upload(), download_file(), main(), notify_make_webhook(), Path, Sends the minimal payload to Make.com incoming webhook. Payload: { video_url,…, CI Render & Publish Helper for GitHub Actions & Make.com Automation Handles…, Downloads a file from a remote URL to dest_path. (+5 more)

### Community 6 - "generate_sample_assets.py"
Cohesion: 0.18
Nodes (12): math, pil, create_gradient(), generate_audio_voiceover(), generate_scene_image(), Path, Draw vertical linear gradient., Generate a high-resolution 1080x1080 scene illustration card. (+4 more)

### Community 7 - "SpeechCueAlignEngine"
Cohesion: 0.08
Nodes (24): re, AlignmentResult, main(), Path, Speech-Cue Align Engine for FB 2minutes Storymaker Implements audio analysis…, Parse script file into structured [(scene_title, scene_text)] entries., Represents a segment of speech with timing information., Align speech segments from audio with script scenes based on narrative cadence.… (+16 more)

### Community 8 - "termux_ui.py"
Cohesion: 0.08
Nodes (39): argparse, http, json, check_assets(), generate_sample_assets(), handler(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the… (+31 more)

### Community 9 - "Speech-Cue Align Engine"
Cohesion: 0.17
Nodes (11): 1. Audio Analysis, 2. Speech-Script Alignment, As a Module, Command Line Interface, Dependencies, Functionality, Future Enhancements, Integration with Pipeline (+3 more)

### Community 10 - "End-to-End Workflow: FB 2minutes Storymaker"
Cohesion: 0.18
Nodes (10): 1. Script Preparation (`script.txt`), 2. Voice-Over Recording (`narration.mp3` or `.wav`), 3. Visual Asset Packaging (`scenes.zip` or individual images), End-to-End Workflow: FB 2minutes Storymaker, Phase 1: Asset Preparation & Ingestion, Phase 2: Automated Analysis & Timing Alignment, Phase 3: Visual Choreography & Styling Engine, Phase 4: Review & One-Click Master Export (+2 more)

### Community 16 - "🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com"
Cohesion: 0.20
Nodes (9): 1. ⚡ Calling the API from Google Flow, 2. 📦 Payload Sent to Make.com Webhook, 3. 🎯 Setting Up Make.com Scenario, 4. 🔑 Vercel Environment Variables, 🏗️ Architecture Overview, 🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com, Detailed Confirmation Response from Vercel (`202 Accepted`):, Method A: Via Vercel Gateway (Recommended) (+1 more)

### Community 17 - "SceneDurationDirector"
Cohesion: 0.10
Nodes (18): MasterTimeline, Path, Builds the MasterTimeline combining speech alignment segments with visual…, Export timeline manifest to JSON for visual choreographer and exporter., Complete master timeline manifest., Directs scene duration allocation and pairs visual assets with aligned speech…, Locate and order image files from a zip archive or directory. Orders by numeric…, SceneDurationDirector (+10 more)

### Community 18 - "vercel.json"
Cohesion: 0.33
Nodes (5): includeFiles, functions, app.py, headers, rewrites

### Community 25 - "app.py"
Cohesion: 0.10
Nodes (18): get_fallback_html(), handler, HandlerMeta, Vercel Serverless Entrypoint for FB 2minutes Storymaker Compatible with: 1.…, WSGI application entrypoint for WSGI servers and Vercel WSGI adapter., Resolve requested path to bytes and content-type., Metaclass enabling both BaseHTTPRequestHandler inheritance and direct Lambda…, Vercel HTTP Handler inheriting from BaseHTTPRequestHandler. (+10 more)

### Community 26 - "run_tui_main"
Cohesion: 0.15
Nodes (19): clear_screen(), get_asset_status(), launch_web_studio_and_browser(), open_media_file(), print_banner(), print_status_box(), Path, Opens an exported video file in Android default player. (+11 more)

### Community 27 - "TestServerlessApp"
Cohesion: 0.17
Nodes (6): Vercel's vc_init.py requires issubclass(handler, BaseHTTPRequestHandler)., Vercel executes handler via HTTPServer in HTTP Handler mode., Vercel WSGI mode calls app(environ, start_response)., Metaclass allows direct AWS Lambda (event, context) calls., Fallback decompresses to full index.html even without disk access., TestServerlessApp

## Knowledge Gaps
- **49 isolated node(s):** `install.sh script`, `fb-2minutes-storymaker`, `setup_local.sh script`, `includeFiles`, `rewrites` (+44 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 173 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `termux_ui.py`, `SceneDurationDirector`, `run_tui_main`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `VisualChoreographer` to `SceneDurationDirector`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and ``SpeechCueAlignEngine``) actually correct?**
  _`SpeechCueAlignEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SceneTimeline` (e.g. with `VisualChoreographer` and `VideoExporter`) actually correct?**
  _`SceneTimeline` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `VideoExporter` (e.g. with `run_pipeline()` and `VisualChoreographer`) actually correct?**
  _`VideoExporter` has 5 INFERRED edges - model-reasoned connections that need verification._