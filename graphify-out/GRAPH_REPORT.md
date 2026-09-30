# Graph Report - FB-2minutes-Storymaker  (2026-09-29)

## Corpus Check
- 56 files · ~116,189 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .zip 1, .lock 1)

## Summary
- 497 nodes · 940 edges · 27 communities (16 shown, 11 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 77 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Main CLI Orchestrator
- Universal Web Server Gateway
- Speech Cue Alignment Engine
- Choreography Test Suite
- Server Request & Upload Handlers
- Story Package Items Manager
- Gemini TTS & Multimodal Alignment
- Scene Duration Director
- Archive & Manifest Manager
- Multipart Parsing & Item Tests
- Automated GitHub Actions Pipeline
- CI Video Render & Release
- Sample Asset Generator
- Vercel & Lambda Serverless Adapter
- Gemini Service Unit Tests
- Visual Choreography Documentation
- API Gateway Integration Tests
- Vercel Serverless Configuration
- One-Line Installer Script
- Story Script & Narration Samples
- Turso libSQL & Make.com Database
- Project Dependencies & Tooling
- Package Setup Configuration
- Local Environment Setup
- End-to-End Workflow Documentation
- CLI Command Entrypoint

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
- `run_pipeline()` --calls--> `VideoExporter`  [INFERRED]
  main.py → src/exporter/video_exporter.py
- `auto_publish_story_item_thread()` --uses--> `SpeechSegment`  [INFERRED]
  web/server.py → src/align_engine/align_engine.py
- `render_story_item_thread()` --uses--> `SpeechSegment`  [INFERRED]
  web/server.py → src/align_engine/align_engine.py
- `auto_publish_story_item_thread()` --uses--> `AlignmentResult`  [INFERRED]
  web/server.py → src/align_engine/align_engine.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Core Sequential Video Rendering Pipeline** — src_align_engine_readme_speech_cue_align_engine, src_duration_director_readme_overview, src_choreography_core_readme_overview, src_exporter_readme_overview [EXTRACTED 1.00]
- **Automated Cloud Rendering and Social Distribution Flow** — docs_automation_guide_overview, _github_workflows_generate_and_publish_workflow, docs_automation_guide_make_webhook, docs_turso_make_guide_overview [INFERRED 0.85]
- **Story Asset Ingestion and Schema Packaging System** — docs_google_studio_guide_json_schema, docs_google_studio_guide_zip_package, readme_storymaker_overview [INFERRED 0.85]

## Communities (27 total, 11 thin omitted)

### Community 0 - "Main CLI Orchestrator"
Cohesion: 0.06
Nodes (58): check_assets(), generate_sample_assets(), handler(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Starts the local web studio interface., WSGI entrypoint for Vercel deployment: serves index.html and web studio assets., Check if required assets are present in assets/ directory. (+50 more)

### Community 1 - "Universal Web Server Gateway"
Cohesion: 0.05
Nodes (54): get_fallback_html(), handler, HandlerMeta, Vercel Serverless Entrypoint for FB 2minutes Storymaker Compatible with: 1.…, WSGI application entrypoint for WSGI servers and Vercel WSGI adapter., Resolve requested path to bytes and content-type., Metaclass enabling both BaseHTTPRequestHandler inheritance and direct Lambda…, Vercel HTTP Handler inheriting from BaseHTTPRequestHandler. (+46 more)

### Community 2 - "Speech Cue Alignment Engine"
Cohesion: 0.07
Nodes (26): dataclasses, pathlib, pil, shutil, AlignmentResult, main(), Path, Speech-Cue Align Engine for FB 2minutes Storymaker Implements audio analysis… (+18 more)

### Community 3 - "Choreography Test Suite"
Cohesion: 0.08
Nodes (22): ImageDraw, ImageFont, skipUnless, main(), Image, Draws word-wrapped stroked subtitles inside a TikTok dark pill badge., Computes (scale, offset_x, offset_y) for subtle micro-motion push-in. Scale:…, Creates and caches a subtle top/bottom ambient vignette overlay matching… (+14 more)

### Community 4 - "Server Request & Upload Handlers"
Cohesion: 0.07
Nodes (32): SimpleHTTPRequestHandler, get_local_ip(), Detect primary LAN IP address for local network access., auto_publish_story_item_thread(), check_dropbox_duplicate(), check_sheet_duplicate(), delete_file_from_dropbox(), delete_from_google_sheet() (+24 more)

### Community 5 - "Story Package Items Manager"
Cohesion: 0.10
Nodes (21): ItemsManager, natural_sort_key(), Any, Path, Register an SSE subscriber queue., Unregister an SSE subscriber queue., Send an SSE event payload to all active subscriber queues., Return all stories in the items queue, newest first. (+13 more)

### Community 6 - "Gemini TTS & Multimodal Alignment"
Cohesion: 0.11
Nodes (30): logging, align_audio_with_gemini_multimodal(), compute_fallback_cuts(), apply_audio_speed(), call_gemini_api(), call_gemini_audio_api(), _do_request(), detect_audio_silences() (+22 more)

### Community 7 - "Scene Duration Director"
Cohesion: 0.11
Nodes (14): MasterTimeline, Path, Builds the MasterTimeline combining speech alignment segments with visual…, Export timeline manifest to JSON for visual choreographer and exporter., Complete master timeline manifest., Locate and order image files from a zip archive or directory. Orders by numeric…, Detects aspect ratio from input images. If images are square (1:1),…, main() (+6 more)

### Community 8 - "Archive & Manifest Manager"
Cohesion: 0.19
Nodes (7): ArchiveManager, Any, Path, Mark Facebook or YouTube status for a given record., List all archived videos, auto-syncing with files on disk., Save MP4 video file to output directory and log to local manifest., TestArchiveManager

### Community 9 - "Multipart Parsing & Item Tests"
Cohesion: 0.13
Nodes (3): parse_multipart_request(), Zero-dependency multipart/form-data parser for file uploads., TestItemsManager

### Community 10 - "Automated GitHub Actions Pipeline"
Cohesion: 0.15
Nodes (14): Video Render and Webhook Notification CI Job, Generate & Publish Video GitHub Actions Workflow, Make.com Social Auto-Publishing Webhook, Automated Publishing Pipeline Architecture, Vercel API Gateway Dispatch Trigger, Story Script JSON Schema, Storymaker JSON & ZIP Bridge Integration Guide, Story Pack ZIP Ingestion Architecture (+6 more)

### Community 11 - "CI Video Render & Release"
Cohesion: 0.21
Nodes (13): base64, create_github_release_and_upload(), download_file(), main(), notify_make_webhook(), Path, Sends the minimal payload to Make.com incoming webhook. Payload: { video_url,…, CI Render & Publish Helper for GitHub Actions & Make.com Automation Handles… (+5 more)

### Community 12 - "Sample Asset Generator"
Cohesion: 0.20
Nodes (11): math, create_gradient(), generate_audio_voiceover(), generate_scene_image(), Path, Draw vertical linear gradient., Generate a high-resolution 1080x1080 scene illustration card., Sample Asset Generator for FB 2minutes Storymaker Creates complete, realistic… (+3 more)

### Community 13 - "Vercel & Lambda Serverless Adapter"
Cohesion: 0.17
Nodes (6): Vercel's vc_init.py requires issubclass(handler, BaseHTTPRequestHandler)., Vercel executes handler via HTTPServer in HTTP Handler mode., Vercel WSGI mode calls app(environ, start_response)., Metaclass allows direct AWS Lambda (event, context) calls., Fallback decompresses to full index.html even without disk access., TestServerlessApp

### Community 15 - "Visual Choreography Documentation"
Cohesion: 0.25
Nodes (8): Speech Alignment Export Dataset, Visual Choreography & Sub-Caption Styling Rules, Smart Aspect Ratio Auto-Adaptation, Picture-Book Motion Aesthetics, Speech-Cue Align Engine Documentation, Visual Choreography Core Module Blueprint, Scene Duration Director Module Blueprint, Master Video Exporter Module Blueprint

### Community 17 - "Vercel Serverless Configuration"
Cohesion: 0.33
Nodes (5): includeFiles, functions, app.py, headers, rewrites

## Knowledge Gaps
- **21 isolated node(s):** `install.sh script`, `GIT_TERMINAL_PROMPT`, `fb-2minutes-storymaker`, `setup_local.sh script`, `includeFiles` (+16 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 228 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ItemsManager` connect `Story Package Items Manager` to `Universal Web Server Gateway`, `Multipart Parsing & Item Tests`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `Choreography Test Suite` to `Speech Cue Alignment Engine`, `Scene Duration Director`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `SpeechCueAlignEngine` connect `Main CLI Orchestrator` to `Speech Cue Alignment Engine`, `Server Request & Upload Handlers`, `Scene Duration Director`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and `TestAlignEngine`) actually correct?**
  _`SpeechCueAlignEngine` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ItemsManager` (e.g. with `TestItemsManager` and `.setUp()`) actually correct?**
  _`ItemsManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 7 INFERRED edges - model-reasoned connections that need verification._