# Graph Report - FB-2minutes-Storymaker  (2026-09-29)

## Corpus Check
- 48 files · ~110,939 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .zip 1, .lock 1)

## Summary
- 515 nodes · 990 edges · 30 communities (18 shown, 12 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 87 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ba781bc3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- termux_ui.py
- server.py
- VisualChoreographer
- .do_POST
- ItemsManager
- gemini_service.py
- ArchiveManager
- TestItemsManager
- FB-2minutes Storymaker System Overview
- main
- generate_sample_assets.py
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
- SpeechCueAlignEngine
- app.py
- package_story
- package_images_to_zip
- find_random_available_port
- GraphHandler

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
- `main()` --calls--> `natural_sort_key()`  [INFERRED]
  scripts/google_studio_bridge.py → src/items_manager.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Core Sequential Video Rendering Pipeline** — src_align_engine_readme_speech_cue_align_engine, src_duration_director_readme_overview, src_choreography_core_readme_overview, src_exporter_readme_overview [EXTRACTED 1.00]
- **Automated Cloud Rendering and Social Distribution Flow** — docs_automation_guide_overview, _github_workflows_generate_and_publish_workflow, docs_automation_guide_make_webhook, docs_turso_make_guide_overview [INFERRED 0.85]
- **Story Asset Ingestion and Schema Packaging System** — docs_google_studio_guide_json_schema, docs_google_studio_guide_zip_package, readme_storymaker_overview [INFERRED 0.85]

## Communities (30 total, 12 thin omitted)

### Community 0 - "termux_ui.py"
Cohesion: 0.08
Nodes (46): check_assets(), generate_sample_assets(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Starts the local web studio interface., Check if required assets are present in assets/ directory., Invoke the sample asset generator., Executes the full Picture-Book Motion storytelling pipeline. (+38 more)

### Community 1 - "server.py"
Cohesion: 0.09
Nodes (40): argparse, dataclasses, datetime, http, io, json, os, pathlib (+32 more)

### Community 3 - "VisualChoreographer"
Cohesion: 0.07
Nodes (23): ImageDraw, ImageFont, skipUnless, main(), Image, Visual Choreography Core for FB 2minutes Storymaker Implements "Picture-Book…, Draws word-wrapped stroked subtitles inside a TikTok dark pill badge., Computes (scale, offset_x, offset_y) for subtle micro-motion push-in. Scale:… (+15 more)

### Community 4 - ".do_POST"
Cohesion: 0.07
Nodes (32): SimpleHTTPRequestHandler, get_local_ip(), Detect primary LAN IP address for local network access., auto_publish_story_item_thread(), check_dropbox_duplicate(), check_sheet_duplicate(), delete_file_from_dropbox(), delete_from_google_sheet() (+24 more)

### Community 5 - "ItemsManager"
Cohesion: 0.10
Nodes (21): ItemsManager, natural_sort_key(), Any, Path, Register an SSE subscriber queue., Unregister an SSE subscriber queue., Send an SSE event payload to all active subscriber queues., Return all stories in the items queue, newest first. (+13 more)

### Community 6 - "gemini_service.py"
Cohesion: 0.11
Nodes (30): logging, align_audio_with_gemini_multimodal(), compute_fallback_cuts(), apply_audio_speed(), call_gemini_api(), call_gemini_audio_api(), _do_request(), detect_audio_silences() (+22 more)

### Community 8 - "ArchiveManager"
Cohesion: 0.19
Nodes (7): ArchiveManager, Any, Path, Mark Facebook or YouTube status for a given record., List all archived videos, auto-syncing with files on disk., Save MP4 video file to output directory and log to local manifest., TestArchiveManager

### Community 9 - "TestItemsManager"
Cohesion: 0.13
Nodes (3): parse_multipart_request(), Zero-dependency multipart/form-data parser for file uploads., TestItemsManager

### Community 10 - "FB-2minutes Storymaker System Overview"
Cohesion: 0.15
Nodes (14): Video Render and Webhook Notification CI Job, Generate & Publish Video GitHub Actions Workflow, Make.com Social Auto-Publishing Webhook, Automated Publishing Pipeline Architecture, Vercel API Gateway Dispatch Trigger, Story Script JSON Schema, Storymaker JSON & ZIP Bridge Integration Guide, Story Pack ZIP Ingestion Architecture (+6 more)

### Community 11 - "main"
Cohesion: 0.24
Nodes (10): create_github_release_and_upload(), download_file(), main(), notify_make_webhook(), Path, Sends the minimal payload to Make.com incoming webhook. Payload: { video_url,…, Downloads a file from a remote URL to dest_path., Decodes a base64 string to dest_path. (+2 more)

### Community 12 - "generate_sample_assets.py"
Cohesion: 0.18
Nodes (12): math, pil, create_gradient(), generate_audio_voiceover(), generate_scene_image(), Path, Draw vertical linear gradient., Generate a high-resolution 1080x1080 scene illustration card. (+4 more)

### Community 15 - "Visual Choreography Core Module Blueprint"
Cohesion: 0.25
Nodes (8): Speech Alignment Export Dataset, Visual Choreography & Sub-Caption Styling Rules, Smart Aspect Ratio Auto-Adaptation, Picture-Book Motion Aesthetics, Speech-Cue Align Engine Documentation, Visual Choreography Core Module Blueprint, Scene Duration Director Module Blueprint, Master Video Exporter Module Blueprint

### Community 17 - "vercel.json"
Cohesion: 0.33
Nodes (5): includeFiles, functions, app.py, headers, rewrites

### Community 27 - "SpeechCueAlignEngine"
Cohesion: 0.05
Nodes (33): AlignmentResult, main(), Path, Parse script file into structured [(scene_title, scene_text)] entries., Align speech segments from audio with script scenes based on narrative cadence.…, Export alignment to both human-readable text and JSON., Result of aligning speech segments with visual scenes., Analyzes voice-over audio and aligns it with scene scripts to determine optimal… (+25 more)

### Community 28 - "app.py"
Cohesion: 0.07
Nodes (22): get_fallback_html(), handler, HandlerMeta, Vercel Serverless Entrypoint for FB 2minutes Storymaker Compatible with: 1.…, WSGI application entrypoint for WSGI servers and Vercel WSGI adapter., Resolve requested path to bytes and content-type., Metaclass enabling both BaseHTTPRequestHandler inheritance and direct Lambda…, Vercel HTTP Handler inheriting from BaseHTTPRequestHandler. (+14 more)

### Community 31 - "package_story"
Cohesion: 0.22
Nodes (10): create_storybook_image(), main(), package_story(), Any, Image, Path, Generate a clean visual storybook canvas when real AI images are not yet…, Bundle story images + story.json into an in-memory ZIP archive. (+2 more)

### Community 32 - "package_images_to_zip"
Cohesion: 0.38
Nodes (7): main(), package_images_to_zip(), Any, Path, Convenience function: Package images and POST them to Storymaker API. Zero…, Bundle image files into an in-memory ZIP archive with auto-generated story.json…, send_images_to_api()

### Community 33 - "find_random_available_port"
Cohesion: 0.18
Nodes (9): main(), find_random_available_port(), get_active_port(), Path, Find a random available port within the specified range [min_port, max_port].…, Save active server port to a root marker file for auto-discovery by client…, Read saved port from marker file if present., save_active_port() (+1 more)

## Knowledge Gaps
- **21 isolated node(s):** `install.sh script`, `GIT_TERMINAL_PROMPT`, `fb-2minutes-storymaker`, `setup_local.sh script`, `includeFiles` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 233 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ItemsManager` connect `ItemsManager` to `server.py`, `TestItemsManager`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `VisualChoreographer` to `server.py`, `SpeechCueAlignEngine`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `termux_ui.py`, `server.py`, `.do_POST`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and `TestAlignEngine`) actually correct?**
  _`SpeechCueAlignEngine` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ItemsManager` (e.g. with `TestItemsManager` and `.setUp()`) actually correct?**
  _`ItemsManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 7 INFERRED edges - model-reasoned connections that need verification._