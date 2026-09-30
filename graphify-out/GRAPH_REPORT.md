# Graph Report - FB-2minutes-Storymaker  (2026-09-29)

## Corpus Check
- 50 files · ~122,784 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .zip 1, .lock 1)

## Summary
- 577 nodes · 1104 edges · 39 communities (24 shown, 15 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 101 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c821e333`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SceneDurationDirector
- server.py
- termux_ui.py
- ItemsManager
- TestItemsManager
- VisualChoreographer
- read_env_settings
- StoryShorts Studio Main Application
- turso_client.py
- ArchiveManager
- handler
- FB-2minutes Storymaker System Overview
- generate_sample_assets.py
- find_random_available_port
- main
- TestServerlessApp
- TestGeminiService
- package_story
- Visual Choreography Core Module Blueprint
- package_images_to_zip
- TestApiGatewayNode
- vercel.json
- install.sh
- GraphHandler
- Default Story Script Template
- Turso HTTP v2 Pipeline API
- Development and Linting Tooling Suite
- setup.py
- setup_local.sh
- End-to-End Story Workflow Guide
- fb-2minutes-storymaker
- video_exporter.py
- duration_director.py
- SpeechCueAlignEngine
- TestTursoClient
- TestAlignEngine
- run_pipeline_thread
- StorymakerRequestHandler

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
10. `TestTursoClient` - 13 edges

## Surprising Connections (you probably didn't know these)
- `AR Cinema Monitor Canvas Preview` --semantically_similar_to--> `Cinema Monitor Preview Canvas`  [INFERRED] [semantically similar]
  AR.html → index.html
- `AR Aspect Ratio StoryShorts Studio` --semantically_similar_to--> `StoryShorts Studio Main Application`  [INFERRED] [semantically similar]
  AR.html → index.html
- `Web Canvas Preview Engine` --semantically_similar_to--> `Cinema Monitor Preview Canvas`  [INFERRED] [semantically similar]
  web/index.html → index.html
- `Web Hosted StoryShorts Studio` --semantically_similar_to--> `StoryShorts Studio Main Application`  [INFERRED] [semantically similar]
  web/index.html → index.html
- `Web Incoming Packages Queue` --semantically_similar_to--> `Incoming Story Packages Queue Manager`  [INFERRED] [semantically similar]
  web/index.html → index.html

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Cloud Rendering and Social Publishing Flow**  -  index_html_client_studio, index_html_cloud_publisher, index_html_ffmpeg_renderer, index_html_social_lock_pattern [EXTRACTED 1.00]
- **Client Application Deployment Mirrors**  -  index_html_client_studio, ar_html_studio, web_index_html_studio [EXTRACTED 1.00]
- **Story Creation and Alignment Pipeline**  -  index_html_script_parser, index_html_gemini_voice_studio, index_html_audio_alignment, index_html_canvas_preview [EXTRACTED 1.00]
- **Core Sequential Video Rendering Pipeline**  -  src_align_engine_readme_speech_cue_align_engine, src_duration_director_readme_overview, src_choreography_core_readme_overview, src_exporter_readme_overview [EXTRACTED 1.00]
- **Automated Cloud Rendering and Social Distribution Flow**  -  docs_automation_guide_overview, _github_workflows_generate_and_publish_workflow, docs_automation_guide_make_webhook, docs_turso_make_guide_overview [INFERRED 0.85]
- **Story Asset Ingestion and Schema Packaging System**  -  docs_google_studio_guide_json_schema, docs_google_studio_guide_zip_package, readme_storymaker_overview [INFERRED 0.85]

## Communities (39 total, 15 thin omitted)

### Community 0 - "SceneDurationDirector"
Cohesion: 0.18
Nodes (8): Path, Builds the MasterTimeline combining speech alignment segments with visual…, Export timeline manifest to JSON for visual choreographer and exporter., Directs scene duration allocation and pairs visual assets with aligned speech…, Locate and order image files from a zip archive or directory. Orders by numeric…, Detects aspect ratio from input images. If images are square (1:1),…, SceneDurationDirector, TestDurationDirector

### Community 1 - "server.py"
Cohesion: 0.08
Nodes (44): Vercel Serverless Entrypoint for FB 2minutes Storymaker Compatible with: 1.…, argparse, base64, datetime, gzip, http, http_server, Vercel Serverless Entrypoint alias for app.py (+36 more)

### Community 2 - "termux_ui.py"
Cohesion: 0.08
Nodes (46): check_assets(), generate_sample_assets(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Starts the local web studio interface., Check if required assets are present in assets/ directory., Invoke the sample asset generator., Executes the full Picture-Book Motion storytelling pipeline. (+38 more)

### Community 3 - "ItemsManager"
Cohesion: 0.10
Nodes (21): ItemsManager, natural_sort_key(), Any, Path, Register an SSE subscriber queue., Unregister an SSE subscriber queue., Send an SSE event payload to all active subscriber queues., Return all stories in the items queue, newest first. (+13 more)

### Community 4 - "TestItemsManager"
Cohesion: 0.13
Nodes (3): parse_multipart_request(), Zero-dependency multipart/form-data parser for file uploads., TestItemsManager

### Community 5 - "VisualChoreographer"
Cohesion: 0.07
Nodes (23): ImageDraw, ImageFont, skipUnless, main(), Image, Visual Choreography Core for FB 2minutes Storymaker Implements "Picture-Book…, Draws word-wrapped stroked subtitles inside a TikTok dark pill badge., Computes (scale, offset_x, offset_y) for subtle micro-motion push-in. Scale:… (+15 more)

### Community 6 - "read_env_settings"
Cohesion: 0.10
Nodes (27): align_audio_with_gemini_multimodal(), compute_fallback_cuts(), apply_audio_speed(), call_gemini_api(), call_gemini_audio_api(), _do_request(), detect_audio_silences(), generate_gemini_tts() (+19 more)

### Community 7 - "StoryShorts Studio Main Application"
Cohesion: 0.10
Nodes (21): Aspect Ratio Auto-Switching Controller, AR Cinema Monitor Canvas Preview, AR Aspect Ratio StoryShorts Studio, Automatic Aspect Ratio Adaptation, Auto Speech-Cut Alignment Engine, Cinema Monitor Preview Canvas, StoryShorts Studio Main Application, Cloud Video Publisher and Manifest Sync (+13 more)

### Community 8 - "turso_client.py"
Cohesion: 0.08
Nodes (39): execute_turso_pipeline(), init_turso_schema(), normalize_turso_url(), Any, Turso (libSQL Edge SQLite) HTTP Client for FB 2minutes Storymaker Provides…, Verify Turso credentials, ensure schema exists, and seed initial sample story…, Normalize libSQL/turso URL to standard https:// endpoint., Upsert story record into Turso stories table with social upload statuses. (+31 more)

### Community 9 - "ArchiveManager"
Cohesion: 0.19
Nodes (7): ArchiveManager, Any, Path, Mark Facebook or YouTube status for a given record., List all archived videos, auto-syncing with files on disk., Save MP4 video file to output directory and log to local manifest., TestArchiveManager

### Community 10 - "handler"
Cohesion: 0.14
Nodes (10): get_fallback_html(), handler, HandlerMeta, WSGI application entrypoint for WSGI servers and Vercel WSGI adapter., Resolve requested path to bytes and content-type., Metaclass enabling both BaseHTTPRequestHandler inheritance and direct Lambda…, Vercel HTTP Handler inheriting from BaseHTTPRequestHandler., resolve_asset() (+2 more)

### Community 11 - "FB-2minutes Storymaker System Overview"
Cohesion: 0.15
Nodes (14): Video Render and Webhook Notification CI Job, Generate & Publish Video GitHub Actions Workflow, Make.com Social Auto-Publishing Webhook, Automated Publishing Pipeline Architecture, Vercel API Gateway Dispatch Trigger, Story Script JSON Schema, Storymaker JSON & ZIP Bridge Integration Guide, Story Pack ZIP Ingestion Architecture (+6 more)

### Community 12 - "generate_sample_assets.py"
Cohesion: 0.18
Nodes (12): math, pil, create_gradient(), generate_audio_voiceover(), generate_scene_image(), Path, Draw vertical linear gradient., Generate a high-resolution 1080x1080 scene illustration card. (+4 more)

### Community 13 - "find_random_available_port"
Cohesion: 0.18
Nodes (9): main(), find_random_available_port(), get_active_port(), Path, Find a random available port within the specified range [min_port, max_port].…, Save active server port to a root marker file for auto-discovery by client…, Read saved port from marker file if present., save_active_port() (+1 more)

### Community 14 - "main"
Cohesion: 0.24
Nodes (10): create_github_release_and_upload(), download_file(), main(), notify_make_webhook(), Path, Sends the minimal payload to Make.com incoming webhook. Payload: { video_url,…, Downloads a file from a remote URL to dest_path., Decodes a base64 string to dest_path. (+2 more)

### Community 15 - "TestServerlessApp"
Cohesion: 0.17
Nodes (6): Vercel's vc_init.py requires issubclass(handler, BaseHTTPRequestHandler)., Vercel executes handler via HTTPServer in HTTP Handler mode., Vercel WSGI mode calls app(environ, start_response)., Metaclass allows direct AWS Lambda (event, context) calls., Fallback decompresses to full index.html even without disk access., TestServerlessApp

### Community 17 - "package_story"
Cohesion: 0.22
Nodes (10): create_storybook_image(), main(), package_story(), Any, Image, Path, Generate a clean visual storybook canvas when real AI images are not yet…, Bundle story images + story.json into an in-memory ZIP archive. (+2 more)

### Community 18 - "Visual Choreography Core Module Blueprint"
Cohesion: 0.25
Nodes (8): Speech Alignment Export Dataset, Visual Choreography & Sub-Caption Styling Rules, Smart Aspect Ratio Auto-Adaptation, Picture-Book Motion Aesthetics, Speech-Cue Align Engine Documentation, Visual Choreography Core Module Blueprint, Scene Duration Director Module Blueprint, Master Video Exporter Module Blueprint

### Community 19 - "package_images_to_zip"
Cohesion: 0.38
Nodes (7): main(), package_images_to_zip(), Any, Path, Convenience function: Package images and POST them to Storymaker API. Zero…, Bundle image files into an in-memory ZIP archive with auto-generated story.json…, send_images_to_api()

### Community 21 - "vercel.json"
Cohesion: 0.33
Nodes (5): includeFiles, functions, app.py, headers, rewrites

### Community 32 - "video_exporter.py"
Cohesion: 0.20
Nodes (9): MasterTimeline, Complete master timeline manifest., main(), Path, Final Master Video Exporter for FB 2minutes Storymaker Pipes generated Picture-…, Renders video frames and multiplexes audio using FFmpeg to export the final…, Find the scene corresponding to timestamp t., Renders the complete story video and exports it to output_path. (+1 more)

### Community 33 - "duration_director.py"
Cohesion: 0.21
Nodes (10): dataclasses, AlignmentResult, Speech-Cue Align Engine for FB 2minutes Storymaker Implements audio analysis…, Represents a segment of speech with timing information., Result of aligning speech segments with visual scenes., SpeechSegment, main(), Scene Duration Director for FB 2minutes Storymaker Maps Scene[N] -> Img[N],… (+2 more)

### Community 34 - "SpeechCueAlignEngine"
Cohesion: 0.18
Nodes (10): main(), Path, Parse script file into structured [(scene_title, scene_text)] entries., Detect silence intervals in audio using FFmpeg silencedetect. Returns a list of…, Align speech segments from audio with script scenes based on narrative cadence.…, Export alignment to both human-readable text and JSON., Analyzes voice-over audio and aligns it with scene scripts to determine optimal…, Get exact duration of audio file in seconds via ffprobe or wave/fallback. (+2 more)

### Community 38 - "StorymakerRequestHandler"
Cohesion: 0.14
Nodes (13): SimpleHTTPRequestHandler, get_local_ip(), Detect primary LAN IP address for local network access., get_assets_status(), get_project_assets_info(), get_story_scenes(), Path, Returns full metadata and content for preloading local Termux assets into Web… (+5 more)

## Knowledge Gaps
- **31 isolated node(s):** `install.sh script`, `GIT_TERMINAL_PROMPT`, `fb-2minutes-storymaker`, `setup_local.sh script`, `includeFiles` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 258 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report**  -  run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ItemsManager` connect `ItemsManager` to `server.py`, `TestItemsManager`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `VisualChoreographer` to `video_exporter.py`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `video_exporter.py`, `duration_director.py`, `termux_ui.py`, `SceneDurationDirector`, `TestAlignEngine`, `run_pipeline_thread`, `StorymakerRequestHandler`, `turso_client.py`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and `TestAlignEngine`) actually correct?**
  _`SpeechCueAlignEngine` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ItemsManager` (e.g. with `TestItemsManager` and `.setUp()`) actually correct?**
  _`ItemsManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 7 INFERRED edges - model-reasoned connections that need verification._