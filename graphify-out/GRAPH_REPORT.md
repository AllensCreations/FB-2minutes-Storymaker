# Graph Report - FB-2minutes-Storymaker  (2026-09-29)

## Corpus Check
- 58 files · ~110,939 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 6, .zip 1, .lock 1)

## Summary
- 536 nodes · 1012 edges · 32 communities (15 shown, 17 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 94 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Speech Alignment Engine
- Main CLI Story Pipeline
- Story Packages Items Queue
- Multipart Parser & Item Tests
- Visual Choreography & Subtitles
- Gemini Multimodal Alignment
- Client Studio & Canvas Preview
- Local Web Server & Endpoints
- Video Archive Manager
- Fallback Asset Handler
- GitHub Actions CI Pipeline
- Sample Asset Generator
- Port Helper & Allocation
- CI Publish & Release Dispatcher
- Serverless Integration Tests
- Gemini Service Unit Tests
- Google Studio Bridge
- Storymaker Architecture Docs
- Direct Story Dispatcher
- API Gateway Node Tests
- Vercel Configuration
- Termux Install Scripts
- Knowledge Graph Server
- Story Script Assets
- Turso & Make.com Pipeline
- Package Dependencies Config
- Local Setup Automation
- Workflow Documentation
- Project Packaging Metadata

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
- `AR Aspect Ratio StoryShorts Studio` --semantically_similar_to--> `StoryShorts Studio Main Application`  [INFERRED] [semantically similar]
  AR.html → index.html
- `Web Hosted StoryShorts Studio` --semantically_similar_to--> `StoryShorts Studio Main Application`  [INFERRED] [semantically similar]
  web/index.html → index.html
- `AR Cinema Monitor Canvas Preview` --semantically_similar_to--> `Cinema Monitor Preview Canvas`  [INFERRED] [semantically similar]
  AR.html → index.html
- `Web Canvas Preview Engine` --semantically_similar_to--> `Cinema Monitor Preview Canvas`  [INFERRED] [semantically similar]
  web/index.html → index.html
- `Waveform Silence Detection and Scene Cut Snapping` --semantically_similar_to--> `Multimodal AI Audio Alignment and Silence Snapping`  [INFERRED] [semantically similar]
  EXAMPLE_WORKFLOW.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Automated Cloud Rendering and Social Distribution Flow** — docs_automation_guide_overview, _github_workflows_generate_and_publish_workflow, docs_automation_guide_make_webhook, docs_turso_make_guide_overview [INFERRED 0.85]
- **Story Asset Ingestion and Schema Packaging System** — docs_google_studio_guide_json_schema, docs_google_studio_guide_zip_package, readme_storymaker_overview [INFERRED 0.85]
- **Core Sequential Video Rendering Pipeline** — src_align_engine_readme_speech_cue_align_engine, src_duration_director_readme_overview, src_choreography_core_readme_overview, src_exporter_readme_overview [EXTRACTED 1.00]
- **Story Creation and Alignment Pipeline** — index_html_script_parser, index_html_gemini_voice_studio, index_html_audio_alignment, index_html_canvas_preview [EXTRACTED 1.00]
- **Cloud Rendering and Social Publishing Flow** — index_html_client_studio, index_html_cloud_publisher, index_html_ffmpeg_renderer, index_html_social_lock_pattern [EXTRACTED 1.00]
- **Client Application Deployment Mirrors** — index_html_client_studio, ar_html_studio, web_index_html_studio [EXTRACTED 1.00]

## Communities (32 total, 17 thin omitted)

### Community 0 - "Speech Alignment Engine"
Cohesion: 0.05
Nodes (14): AlignmentResult, main(), SpeechCueAlignEngine, SpeechSegment, main(), main(), MasterTimeline, SceneDurationDirector (+6 more)

### Community 2 - "Main CLI Story Pipeline"
Cohesion: 0.08
Nodes (24): check_assets(), generate_sample_assets(), main(), run_pipeline(), start_web_server(), generate_all_sample_assets(), ensure_ffmpeg(), ensure_pillow() (+16 more)

### Community 4 - "Multipart Parser & Item Tests"
Cohesion: 0.06
Nodes (12): parse_multipart_request(), TestItemsManager, auto_publish_story_item_thread(), check_dropbox_duplicate(), check_sheet_duplicate(), delete_file_from_dropbox(), delete_from_google_sheet(), get_dropbox_access_token() (+4 more)

### Community 6 - "Gemini Multimodal Alignment"
Cohesion: 0.10
Nodes (14): align_audio_with_gemini_multimodal(), compute_fallback_cuts(), apply_audio_speed(), call_gemini_api(), call_gemini_audio_api(), _do_request(), detect_audio_silences(), generate_gemini_tts() (+6 more)

### Community 7 - "Client Studio & Canvas Preview"
Cohesion: 0.10
Nodes (20): Aspect Ratio Auto-Switching Controller, AR Cinema Monitor Canvas Preview, AR Aspect Ratio StoryShorts Studio, Automatic Aspect Ratio Adaptation, Auto Speech-Cut Alignment Engine, Cinema Monitor Preview Canvas, StoryShorts Studio Main Application, Cloud Video Publisher and Manifest Sync (+12 more)

### Community 8 - "Local Web Server & Endpoints"
Cohesion: 0.14
Nodes (5): get_local_ip(), get_assets_status(), get_project_assets_info(), get_story_scenes(), StorymakerRequestHandler

### Community 10 - "Fallback Asset Handler"
Cohesion: 0.14
Nodes (5): get_fallback_html(), handler, HandlerMeta, resolve_asset(), wsgi_app()

### Community 11 - "GitHub Actions CI Pipeline"
Cohesion: 0.15
Nodes (14): Video Render and Webhook Notification CI Job, Generate & Publish Video GitHub Actions Workflow, Make.com Social Auto-Publishing Webhook, Automated Publishing Pipeline Architecture, Vercel API Gateway Dispatch Trigger, Story Script JSON Schema, Storymaker JSON & ZIP Bridge Integration Guide, Story Pack ZIP Ingestion Architecture (+6 more)

### Community 12 - "Sample Asset Generator"
Cohesion: 0.18
Nodes (3): create_gradient(), generate_audio_voiceover(), generate_scene_image()

### Community 13 - "Port Helper & Allocation"
Cohesion: 0.18
Nodes (5): main(), find_random_available_port(), get_active_port(), save_active_port(), TestPortHelper

### Community 14 - "CI Publish & Release Dispatcher"
Cohesion: 0.26
Nodes (5): create_github_release_and_upload(), download_file(), main(), notify_make_webhook(), save_base64_file()

### Community 17 - "Google Studio Bridge"
Cohesion: 0.22
Nodes (4): create_storybook_image(), main(), package_story(), upload_zip()

### Community 18 - "Storymaker Architecture Docs"
Cohesion: 0.25
Nodes (7): Speech Alignment Export Dataset, Visual Choreography & Sub-Caption Styling Rules, Picture-Book Motion Aesthetics, Speech-Cue Align Engine Documentation, Visual Choreography Core Module Blueprint, Scene Duration Director Module Blueprint, Master Video Exporter Module Blueprint

### Community 19 - "Direct Story Dispatcher"
Cohesion: 0.38
Nodes (3): main(), package_images_to_zip(), send_images_to_api()

### Community 21 - "Vercel Configuration"
Cohesion: 0.33
Nodes (5): includeFiles, functions, app.py, headers, rewrites

## Knowledge Gaps
- **31 isolated node(s):** `install.sh script`, `GIT_TERMINAL_PROMPT`, `fb-2minutes-storymaker`, `setup_local.sh script`, `includeFiles` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 244 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ItemsManager` connect `Story Packages Items Queue` to `Serverless App Entrypoint`, `Multipart Parser & Item Tests`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `VisualChoreographer` connect `Visual Choreography & Subtitles` to `Speech Alignment Engine`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `SpeechCueAlignEngine` connect `Speech Alignment Engine` to `Local Web Server & Endpoints`, `Main CLI Story Pipeline`, `Multipart Parser & Item Tests`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and `TestAlignEngine`) actually correct?**
  _`SpeechCueAlignEngine` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ItemsManager` (e.g. with `TestItemsManager` and `.setUp()`) actually correct?**
  _`ItemsManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 7 INFERRED edges - model-reasoned connections that need verification._