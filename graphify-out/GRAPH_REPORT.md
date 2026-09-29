# Graph Report - FB-2minutes-Storymaker  (2026-09-29)

## Corpus Check
- 44 files · ~109,879 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .zip 1, .lock 1)

## Summary
- 546 nodes · 988 edges · 33 communities (21 shown, 12 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 71 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `af5178ac`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- StorymakerRequestHandler
- Speech-Cue Align Engine
- fb-2minutes-storymaker
- FB-2minutes Storymaker
- read_env_settings
- install.sh
- ItemsManager
- TestGeminiService
- termux_ui.py
- package_story
- End-to-End Workflow: FB 2minutes Storymaker
- setup.py
- setup_local.sh
- choreography_core/README.md
- duration_director/README.md
- exporter/README.md
- 🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com
- generate_scene_image
- vercel.json
- TestApiGatewayNode
- server.py
- render
- ArchiveManager
- TestServerlessApp
- handler
- GOOGLE_STUDIO_GUIDE.md
- VisualChoreographer
- main
- package_images_to_zip
- TestItemsManager
- TestAlignEngine
- SpeechCueAlignEngine

## God Nodes (most connected - your core abstractions)
1. `SpeechCueAlignEngine` - 29 edges
2. `VisualChoreographer` - 23 edges
3. `ItemsManager` - 23 edges
4. `SceneDurationDirector` - 21 edges
5. `SceneTimeline` - 16 edges
6. `VideoExporter` - 16 edges
7. `TestItemsManager` - 15 edges
8. `run_video_render()` - 13 edges
9. `run_tui_main()` - 13 edges
10. `StorymakerRequestHandler` - 13 edges

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

## Communities (33 total, 12 thin omitted)

### Community 0 - "StorymakerRequestHandler"
Cohesion: 0.08
Nodes (24): SimpleHTTPRequestHandler, get_local_ip(), Detect primary LAN IP address for local network access., delete_file_from_dropbox(), delete_from_google_sheet(), get_assets_status(), get_project_assets_info(), get_story_scenes() (+16 more)

### Community 1 - "Speech-Cue Align Engine"
Cohesion: 0.12
Nodes (15): 1. Audio Analysis, 2. Speech-Script Alignment, As a Module, Command Line Interface, Core Classes, Dependencies, Functionality, Future Enhancements (+7 more)

### Community 3 - "FB-2minutes Storymaker"
Cohesion: 0.07
Nodes (26): 1. Ingest a New Story Package, 1. Installation, 1. Modern 3-Tab Studio Navigation, 2. Auto-Jump & Instant Canvas Preview on "Open & Render", 2. Environment Configuration, 2. Update and Replace an Existing Package (by Item ID), 3. Launching the Application, 3. Minimalist Studio UI (+18 more)

### Community 4 - "read_env_settings"
Cohesion: 0.10
Nodes (27): align_audio_with_gemini_multimodal(), compute_fallback_cuts(), apply_audio_speed(), call_gemini_api(), call_gemini_audio_api(), _do_request(), detect_audio_silences(), generate_gemini_tts() (+19 more)

### Community 6 - "ItemsManager"
Cohesion: 0.10
Nodes (21): ItemsManager, natural_sort_key(), Any, Path, Register an SSE subscriber queue., Unregister an SSE subscriber queue., Send an SSE event payload to all active subscriber queues., Return all stories in the items queue, newest first. (+13 more)

### Community 8 - "termux_ui.py"
Cohesion: 0.08
Nodes (47): check_assets(), generate_sample_assets(), handler(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Starts the local web studio interface., WSGI entrypoint for Vercel deployment: serves index.html and web studio assets., Check if required assets are present in assets/ directory. (+39 more)

### Community 9 - "package_story"
Cohesion: 0.20
Nodes (11): create_storybook_image(), main(), natural_sort_key(), package_story(), Any, Image, Path, Generate a clean visual storybook canvas when real AI images are not yet… (+3 more)

### Community 10 - "End-to-End Workflow: FB 2minutes Storymaker"
Cohesion: 0.18
Nodes (10): 1. Script Preparation (`script.txt`), 2. Voice-Over Recording (`narration.mp3` or `.wav`), 3. Visual Asset Packaging (`scenes.zip` or individual images), End-to-End Workflow: FB 2minutes Storymaker, Phase 1: Asset Preparation & Ingestion, Phase 2: Automated Analysis & Timing Alignment, Phase 3: Visual Choreography & Styling Engine, Phase 4: Review & One-Click Master Export (+2 more)

### Community 16 - "🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com"
Cohesion: 0.20
Nodes (9): 1. ⚡ Calling the API from Google Flow, 2. 📦 Payload Sent to Make.com Webhook, 3. 🎯 Setting Up Make.com Scenario, 4. 🔑 Vercel Environment Variables, 🏗️ Architecture Overview, 🚀 Automated Publishing Pipeline: Google Flow -> Vercel / GitHub Actions -> Make.com, Detailed Confirmation Response from Vercel (`202 Accepted`):, Method A: Via Vercel Gateway (Recommended) (+1 more)

### Community 17 - "generate_scene_image"
Cohesion: 0.29
Nodes (7): create_gradient(), generate_audio_voiceover(), generate_scene_image(), Path, Draw vertical linear gradient., Generate a high-resolution 1080x1080 scene illustration card., Synthesizes a pleasant multi-tone chime & narration track matching the story…

### Community 18 - "vercel.json"
Cohesion: 0.33
Nodes (5): includeFiles, functions, app.py, headers, rewrites

### Community 21 - "server.py"
Cohesion: 0.07
Nodes (49): Vercel Serverless Entrypoint for FB 2minutes Storymaker Compatible with: 1.…, argparse, base64, dataclasses, datetime, gzip, http, http_server (+41 more)

### Community 23 - "ArchiveManager"
Cohesion: 0.19
Nodes (7): ArchiveManager, Any, Path, Mark Facebook or YouTube status for a given record., List all archived videos, auto-syncing with files on disk., Save MP4 video file to output directory and log to local manifest., TestArchiveManager

### Community 24 - "TestServerlessApp"
Cohesion: 0.17
Nodes (6): Vercel's vc_init.py requires issubclass(handler, BaseHTTPRequestHandler)., Vercel executes handler via HTTPServer in HTTP Handler mode., Vercel WSGI mode calls app(environ, start_response)., Metaclass allows direct AWS Lambda (event, context) calls., Fallback decompresses to full index.html even without disk access., TestServerlessApp

### Community 25 - "handler"
Cohesion: 0.14
Nodes (10): get_fallback_html(), handler, HandlerMeta, WSGI application entrypoint for WSGI servers and Vercel WSGI adapter., Resolve requested path to bytes and content-type., Metaclass enabling both BaseHTTPRequestHandler inheritance and direct Lambda…, Vercel HTTP Handler inheriting from BaseHTTPRequestHandler., resolve_asset() (+2 more)

### Community 26 - "GOOGLE_STUDIO_GUIDE.md"
Cohesion: 0.33
Nodes (5): 1. 📄 How the Story JSON is Created (`story.json`), If you have an images folder and story.json:, If you only have images and want auto-generated scene markers:, Recommended JSON Format (Clean Narration Strings), Storymaker JSON & ZIP Bridge Integration Guide

### Community 28 - "VisualChoreographer"
Cohesion: 0.08
Nodes (19): ImageDraw, ImageFont, skipUnless, Image, Draws word-wrapped stroked subtitles inside a TikTok dark pill badge., Computes (scale, offset_x, offset_y) for subtle micro-motion push-in. Scale:…, Creates and caches a subtle top/bottom ambient vignette overlay matching…, Applies a soft Gaussian drop shadow behind the centered artwork. (+11 more)

### Community 29 - "main"
Cohesion: 0.24
Nodes (10): create_github_release_and_upload(), download_file(), main(), notify_make_webhook(), Path, Sends the minimal payload to Make.com incoming webhook. Payload: { video_url,…, Downloads a file from a remote URL to dest_path., Decodes a base64 string to dest_path. (+2 more)

### Community 30 - "package_images_to_zip"
Cohesion: 0.28
Nodes (9): main(), natural_sort_key(), package_images_to_zip(), Any, Path, Convenience function: Package images and POST them to Storymaker API. Zero…, Sort strings containing numbers naturally (e.g. 1.png, 2.png, 10.png)., Bundle image files into an in-memory ZIP archive with auto-generated story.json… (+1 more)

### Community 31 - "TestItemsManager"
Cohesion: 0.13
Nodes (3): parse_multipart_request(), Zero-dependency multipart/form-data parser for file uploads., TestItemsManager

### Community 34 - "SpeechCueAlignEngine"
Cohesion: 0.05
Nodes (47): AlignmentResult, main(), Path, Parse script file into structured [(scene_title, scene_text)] entries., Represents a segment of speech with timing information., Align speech segments from audio with script scenes based on narrative cadence.…, Export alignment to both human-readable text and JSON., Result of aligning speech segments with visual scenes. (+39 more)

## Knowledge Gaps
- **56 isolated node(s):** `install.sh script`, `GIT_TERMINAL_PROMPT`, `fb-2minutes-storymaker`, `setup_local.sh script`, `includeFiles` (+51 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 270 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `StorymakerRequestHandler`, `Speech-Cue Align Engine`, `TestAlignEngine`, `termux_ui.py`, `server.py`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Why does `ItemsManager` connect `ItemsManager` to `server.py`, `TestItemsManager`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `VisualChoreographer` to `SpeechCueAlignEngine`, `server.py`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and ``SpeechCueAlignEngine``) actually correct?**
  _`SpeechCueAlignEngine` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ItemsManager` (e.g. with `TestItemsManager` and `.setUp()`) actually correct?**
  _`ItemsManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 7 INFERRED edges - model-reasoned connections that need verification._