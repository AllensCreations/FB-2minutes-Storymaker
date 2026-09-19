# Graph Report - FB-2minutes-Storymaker  (2026-09-18)

## Corpus Check
- 34 files · ~42,320 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 3, .zip 1, .lock 1)

## Summary
- 343 nodes · 583 edges · 25 communities (12 shown, 13 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 44 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3840c800`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_pipeline_thread
- VisualChoreographer
- fb-2minutes-storymaker
- FB-2minutes Storymaker
- ci_render_and_publish.py
- install.sh
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
- vercel.json
- TestApiGatewayNode
- io
- render
- unittest_mock
- urllib_error
- server.py
- TestServerlessApp

## God Nodes (most connected - your core abstractions)
1. `SpeechCueAlignEngine` - 25 edges
2. `VisualChoreographer` - 19 edges
3. `SceneDurationDirector` - 19 edges
4. `SceneTimeline` - 16 edges
5. `VideoExporter` - 14 edges
6. `run_video_render()` - 13 edges
7. `run_tui_main()` - 13 edges
8. `FB-2minutes Storymaker` - 13 edges
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
- `run_pipeline_thread()` --uses--> `SpeechCueAlignEngine`  [INFERRED]
  web/server.py → src/align_engine/align_engine.py

## Import Cycles
- None detected.

## Communities (25 total, 13 thin omitted)

### Community 0 - "run_pipeline_thread"
Cohesion: 0.14
Nodes (13): SimpleHTTPRequestHandler, get_assets_status(), get_project_assets_info(), get_story_scenes(), Path, Returns full metadata and content for preloading local Termux assets into Web…, Background thread function that executes the full rendering pipeline., Custom HTTP request handler serving Web UI and storymaker APIs. (+5 more)

### Community 1 - "VisualChoreographer"
Cohesion: 0.06
Nodes (31): dataclasses, Image, ImageDraw, ImageFont, skipUnless, main(), Visual Choreography Core for FB 2minutes Storymaker Implements "Picture-Book…, Draws word-wrapped stroked subtitles inside a TikTok dark pill badge. (+23 more)

### Community 3 - "FB-2minutes Storymaker"
Cohesion: 0.10
Nodes (19): 1. Dynamic Timed Sub-Caption Paging (TikTok / Reels Style), 1. Master System Prompt for Google Flow AI, 2. Sample Input JSON Template for Google Flow, 2. Scene Subdivision Guidelines for Google Flow AI, 3. Webhook Payload Delivered to Make.com, ⚙️ CLI Reference, 🌐 Creative Studio Web UI (`index.html`), FB-2minutes Storymaker (+11 more)

### Community 4 - "ci_render_and_publish.py"
Cohesion: 0.09
Nodes (27): argparse, base64, math, pil, create_github_release_and_upload(), download_file(), main(), notify_make_webhook() (+19 more)

### Community 7 - "SpeechCueAlignEngine"
Cohesion: 0.07
Nodes (27): re, AlignmentResult, main(), Path, Speech-Cue Align Engine for FB 2minutes Storymaker Implements audio analysis…, Parse script file into structured [(scene_title, scene_text)] entries., Represents a segment of speech with timing information., Align speech segments from audio with script scenes based on narrative cadence.… (+19 more)

### Community 8 - "termux_ui.py"
Cohesion: 0.07
Nodes (49): check_assets(), generate_sample_assets(), handler(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Starts the local web studio interface., WSGI entrypoint for Vercel deployment: serves index.html and web studio assets., Check if required assets are present in assets/ directory. (+41 more)

### Community 9 - "Speech-Cue Align Engine"
Cohesion: 0.12
Nodes (15): 1. Audio Analysis, 2. Speech-Script Alignment, As a Module, Command Line Interface, Core Classes, Dependencies, Functionality, Future Enhancements (+7 more)

### Community 10 - "End-to-End Workflow: FB 2minutes Storymaker"
Cohesion: 0.18
Nodes (10): 1. Script Preparation (`script.txt`), 2. Voice-Over Recording (`narration.mp3` or `.wav`), 3. Visual Asset Packaging (`scenes.zip` or individual images), End-to-End Workflow: FB 2minutes Storymaker, Phase 1: Asset Preparation & Ingestion, Phase 2: Automated Analysis & Timing Alignment, Phase 3: Visual Choreography & Styling Engine, Phase 4: Review & One-Click Master Export (+2 more)

### Community 16 - "🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com"
Cohesion: 0.20
Nodes (9): 1. ⚡ Calling the API from Google Flow, 2. 📦 Payload Sent to Make.com Webhook, 3. 🎯 Setting Up Make.com Scenario, 4. 🔑 Vercel Environment Variables, 🏗️ Architecture Overview, 🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com, Detailed Confirmation Response from Vercel (`202 Accepted`):, Method A: Via Vercel Gateway (Recommended) (+1 more)

### Community 18 - "vercel.json"
Cohesion: 0.33
Nodes (5): includeFiles, functions, app.py, headers, rewrites

### Community 25 - "server.py"
Cohesion: 0.08
Nodes (24): get_fallback_html(), handler, HandlerMeta, Vercel Serverless Entrypoint for FB 2minutes Storymaker Compatible with: 1.…, WSGI application entrypoint for WSGI servers and Vercel WSGI adapter., Resolve requested path to bytes and content-type., Metaclass enabling both BaseHTTPRequestHandler inheritance and direct Lambda…, Vercel HTTP Handler inheriting from BaseHTTPRequestHandler. (+16 more)

### Community 27 - "TestServerlessApp"
Cohesion: 0.17
Nodes (6): Vercel's vc_init.py requires issubclass(handler, BaseHTTPRequestHandler)., Vercel executes handler via HTTPServer in HTTP Handler mode., Vercel WSGI mode calls app(environ, start_response)., Metaclass allows direct AWS Lambda (event, context) calls., Fallback decompresses to full index.html even without disk access., TestServerlessApp

## Knowledge Gaps
- **46 isolated node(s):** `install.sh script`, `fb-2minutes-storymaker`, `setup_local.sh script`, `includeFiles`, `rewrites` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 173 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `termux_ui.py`, `Speech-Cue Align Engine`, `VisualChoreographer`, `run_pipeline_thread`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `Core Classes` connect `Speech-Cue Align Engine` to `SpeechCueAlignEngine`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
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