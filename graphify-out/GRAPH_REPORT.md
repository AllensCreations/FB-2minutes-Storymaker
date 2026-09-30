# Graph Report - FB-2minutes-Storymaker  (2026-09-29)

## Corpus Check
- 48 files · ~117,112 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 8, .zip 1, .lock 1)

## Summary
- 523 nodes · 987 edges · 37 communities (24 shown, 13 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 79 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `96e4ece9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- termux_ui.py
- server.py
- SpeechCueAlignEngine
- VisualChoreographer
- StorymakerRequestHandler
- ItemsManager
- gemini_service.py
- video_exporter.py
- ArchiveManager
- TestItemsManager
- FB-2minutes Storymaker System Overview
- ci_render_and_publish.py
- generate_sample_assets.py
- TestServerlessApp
- TestGeminiService
- Visual Choreography Core Module Blueprint
- TestApiGatewayNode
- vercel.json
- install.sh
- Default Story Script Template
- Turso HTTP v2 Pipeline API
- Development and Linting Tooling Suite
- setup.py
- setup_local.sh
- End-to-End Story Workflow Guide
- fb-2minutes-storymaker
- SceneDurationDirector
- handler
- duration_director.py
- .do_POST
- package_story
- package_images_to_zip
- TestPortHelper
- TestAlignEngine
- GraphHandler
- save_active_port

## God Nodes (most connected - your core abstractions)
1. `SpeechCueAlignEngine` - 28 edges
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
- `Waveform Silence Detection and Scene Cut Snapping` --semantically_similar_to--> `Multimodal AI Audio Alignment and Silence Snapping`  [INFERRED] [semantically similar]
  EXAMPLE_WORKFLOW.md → README.md
- `run_pipeline()` --uses--> `SpeechCueAlignEngine`  [INFERRED]
  main.py → src/align_engine/align_engine.py
- `run_pipeline()` --uses--> `SceneDurationDirector`  [INFERRED]
  main.py → src/duration_director/duration_director.py
- `run_pipeline()` --calls--> `VideoExporter`  [INFERRED]
  main.py → src/exporter/video_exporter.py
- `auto_publish_story_item_thread()` --uses--> `SpeechSegment`  [INFERRED]
  web/server.py → src/align_engine/align_engine.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Core Sequential Video Rendering Pipeline** — src_align_engine_readme_speech_cue_align_engine, src_duration_director_readme_overview, src_choreography_core_readme_overview, src_exporter_readme_overview [EXTRACTED 1.00]
- **Automated Cloud Rendering and Social Distribution Flow** — docs_automation_guide_overview, _github_workflows_generate_and_publish_workflow, docs_automation_guide_make_webhook, docs_turso_make_guide_overview [INFERRED 0.85]
- **Story Asset Ingestion and Schema Packaging System** — docs_google_studio_guide_json_schema, docs_google_studio_guide_zip_package, readme_storymaker_overview [INFERRED 0.85]

## Communities (37 total, 13 thin omitted)

### Community 0 - "termux_ui.py"
Cohesion: 0.07
Nodes (48): check_assets(), generate_sample_assets(), handler(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Starts the local web studio interface., WSGI entrypoint for Vercel deployment: serves index.html and web studio assets., Check if required assets are present in assets/ directory. (+40 more)

### Community 1 - "server.py"
Cohesion: 0.08
Nodes (42): Vercel Serverless Entrypoint for FB 2minutes Storymaker Compatible with: 1.…, argparse, datetime, gzip, http, http_server, Vercel Serverless Entrypoint alias for app.py, io (+34 more)

### Community 2 - "SpeechCueAlignEngine"
Cohesion: 0.19
Nodes (9): main(), Path, Parse script file into structured [(scene_title, scene_text)] entries., Align speech segments from audio with script scenes based on narrative cadence.…, Export alignment to both human-readable text and JSON., Analyzes voice-over audio and aligns it with scene scripts to determine optimal…, Get exact duration of audio file in seconds via ffprobe or wave/fallback., Parses script content string into structured [(scene_title, scene_text)]… (+1 more)

### Community 3 - "VisualChoreographer"
Cohesion: 0.07
Nodes (24): dataclasses, ImageDraw, ImageFont, skipUnless, main(), Image, Visual Choreography Core for FB 2minutes Storymaker Implements "Picture-Book…, Draws word-wrapped stroked subtitles inside a TikTok dark pill badge. (+16 more)

### Community 4 - "StorymakerRequestHandler"
Cohesion: 0.08
Nodes (24): SimpleHTTPRequestHandler, get_local_ip(), Detect primary LAN IP address for local network access., delete_file_from_dropbox(), delete_from_google_sheet(), get_assets_status(), get_project_assets_info(), get_story_scenes() (+16 more)

### Community 5 - "ItemsManager"
Cohesion: 0.10
Nodes (21): ItemsManager, natural_sort_key(), Any, Path, Register an SSE subscriber queue., Unregister an SSE subscriber queue., Send an SSE event payload to all active subscriber queues., Return all stories in the items queue, newest first. (+13 more)

### Community 6 - "gemini_service.py"
Cohesion: 0.11
Nodes (30): logging, align_audio_with_gemini_multimodal(), compute_fallback_cuts(), apply_audio_speed(), call_gemini_api(), call_gemini_audio_api(), _do_request(), detect_audio_silences() (+22 more)

### Community 7 - "video_exporter.py"
Cohesion: 0.21
Nodes (9): MasterTimeline, Complete master timeline manifest., main(), Path, Final Master Video Exporter for FB 2minutes Storymaker Pipes generated Picture-…, Renders video frames and multiplexes audio using FFmpeg to export the final…, Find the scene corresponding to timestamp t., Renders the complete story video and exports it to output_path. (+1 more)

### Community 8 - "ArchiveManager"
Cohesion: 0.19
Nodes (7): ArchiveManager, Any, Path, Mark Facebook or YouTube status for a given record., List all archived videos, auto-syncing with files on disk., Save MP4 video file to output directory and log to local manifest., TestArchiveManager

### Community 9 - "TestItemsManager"
Cohesion: 0.13
Nodes (3): parse_multipart_request(), Zero-dependency multipart/form-data parser for file uploads., TestItemsManager

### Community 10 - "FB-2minutes Storymaker System Overview"
Cohesion: 0.15
Nodes (14): Video Render and Webhook Notification CI Job, Generate & Publish Video GitHub Actions Workflow, Make.com Social Auto-Publishing Webhook, Automated Publishing Pipeline Architecture, Vercel API Gateway Dispatch Trigger, Story Script JSON Schema, Storymaker JSON & ZIP Bridge Integration Guide, Story Pack ZIP Ingestion Architecture (+6 more)

### Community 11 - "ci_render_and_publish.py"
Cohesion: 0.21
Nodes (13): base64, create_github_release_and_upload(), download_file(), main(), notify_make_webhook(), Path, Sends the minimal payload to Make.com incoming webhook. Payload: { video_url,…, CI Render & Publish Helper for GitHub Actions & Make.com Automation Handles… (+5 more)

### Community 12 - "generate_sample_assets.py"
Cohesion: 0.18
Nodes (12): math, pil, create_gradient(), generate_audio_voiceover(), generate_scene_image(), Path, Draw vertical linear gradient., Generate a high-resolution 1080x1080 scene illustration card. (+4 more)

### Community 13 - "TestServerlessApp"
Cohesion: 0.17
Nodes (6): Vercel's vc_init.py requires issubclass(handler, BaseHTTPRequestHandler)., Vercel executes handler via HTTPServer in HTTP Handler mode., Vercel WSGI mode calls app(environ, start_response)., Metaclass allows direct AWS Lambda (event, context) calls., Fallback decompresses to full index.html even without disk access., TestServerlessApp

### Community 15 - "Visual Choreography Core Module Blueprint"
Cohesion: 0.25
Nodes (8): Speech Alignment Export Dataset, Visual Choreography & Sub-Caption Styling Rules, Smart Aspect Ratio Auto-Adaptation, Picture-Book Motion Aesthetics, Speech-Cue Align Engine Documentation, Visual Choreography Core Module Blueprint, Scene Duration Director Module Blueprint, Master Video Exporter Module Blueprint

### Community 17 - "vercel.json"
Cohesion: 0.33
Nodes (5): includeFiles, functions, app.py, headers, rewrites

### Community 27 - "SceneDurationDirector"
Cohesion: 0.18
Nodes (8): Path, Builds the MasterTimeline combining speech alignment segments with visual…, Export timeline manifest to JSON for visual choreographer and exporter., Directs scene duration allocation and pairs visual assets with aligned speech…, Locate and order image files from a zip archive or directory. Orders by numeric…, Detects aspect ratio from input images. If images are square (1:1),…, SceneDurationDirector, TestDurationDirector

### Community 28 - "handler"
Cohesion: 0.14
Nodes (10): get_fallback_html(), handler, HandlerMeta, WSGI application entrypoint for WSGI servers and Vercel WSGI adapter., Resolve requested path to bytes and content-type., Metaclass enabling both BaseHTTPRequestHandler inheritance and direct Lambda…, Vercel HTTP Handler inheriting from BaseHTTPRequestHandler., resolve_asset() (+2 more)

### Community 29 - "duration_director.py"
Cohesion: 0.21
Nodes (8): AlignmentResult, Represents a segment of speech with timing information., Result of aligning speech segments with visual scenes., SpeechSegment, main(), Scene Duration Director for FB 2minutes Storymaker Maps Scene[N] -> Img[N],…, Background worker that renders an item from the Items Queue using FFmpeg., render_story_item_thread()

### Community 30 - ".do_POST"
Cohesion: 0.17
Nodes (10): auto_publish_story_item_thread(), check_dropbox_duplicate(), check_sheet_duplicate(), get_dropbox_access_token(), Background thread function that executes the full rendering pipeline., Exchange Dropbox OAuth refresh token for a short-lived access token., Queries Google Sheets manifest to check if filename or story title already…, Checks if a video file already exists on Dropbox. (+2 more)

### Community 31 - "package_story"
Cohesion: 0.20
Nodes (11): create_storybook_image(), main(), natural_sort_key(), package_story(), Any, Image, Path, Generate a clean visual storybook canvas when real AI images are not yet… (+3 more)

### Community 32 - "package_images_to_zip"
Cohesion: 0.28
Nodes (9): main(), natural_sort_key(), package_images_to_zip(), Any, Path, Convenience function: Package images and POST them to Storymaker API. Zero…, Sort strings containing numbers naturally (e.g. 1.png, 2.png, 10.png)., Bundle image files into an in-memory ZIP archive with auto-generated story.json… (+1 more)

### Community 33 - "TestPortHelper"
Cohesion: 0.33
Nodes (3): get_active_port(), Read saved port from marker file if present., TestPortHelper

### Community 36 - "save_active_port"
Cohesion: 0.67
Nodes (3): Path, Save active server port to a root marker file for auto-discovery by client…, save_active_port()

## Knowledge Gaps
- **21 isolated node(s):** `install.sh script`, `GIT_TERMINAL_PROMPT`, `fb-2minutes-storymaker`, `setup_local.sh script`, `includeFiles` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 239 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ItemsManager` connect `ItemsManager` to `server.py`, `TestItemsManager`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `VisualChoreographer` to `video_exporter.py`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `termux_ui.py`, `server.py`, `TestAlignEngine`, `StorymakerRequestHandler`, `video_exporter.py`, `SceneDurationDirector`, `duration_director.py`, `.do_POST`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and `TestAlignEngine`) actually correct?**
  _`SpeechCueAlignEngine` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ItemsManager` (e.g. with `TestItemsManager` and `.setUp()`) actually correct?**
  _`ItemsManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 7 INFERRED edges - model-reasoned connections that need verification._