# Graph Report - FB-2minutes-Storymaker  (2026-09-16)

## Corpus Check
- 23 files · ~12,527 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 2, .zip 1)

## Summary
- 216 nodes · 358 edges · 15 communities (10 shown, 5 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 35 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `469645e8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- server.py
- VisualChoreographer
- SpeechCueAlignEngine
- FB-2minutes Storymaker
- duration_director.py
- generate_sample_assets.py
- video_exporter.py
- main.py
- Speech-Cue Align Engine
- Example Workflow for FB 2minutes Storymaker
- setup.py
- setup_local.sh
- choreography_core/README.md
- duration_director/README.md
- exporter/README.md

## God Nodes (most connected - your core abstractions)
1. `SpeechCueAlignEngine` - 20 edges
2. `VisualChoreographer` - 15 edges
3. `SceneDurationDirector` - 15 edges
4. `SceneTimeline` - 14 edges
5. `VideoExporter` - 12 edges
6. `AlignmentResult` - 10 edges
7. `MasterTimeline` - 10 edges
8. `FB-2minutes Storymaker` - 10 edges
9. `run_pipeline_thread()` - 9 edges
10. `run_pipeline()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `run_pipeline()` --uses--> `SpeechCueAlignEngine`  [INFERRED]
  main.py → src/align_engine/align_engine.py
- `run_pipeline()` --uses--> `SceneDurationDirector`  [INFERRED]
  main.py → src/duration_director/duration_director.py
- `run_pipeline()` --calls--> `VideoExporter`  [INFERRED]
  main.py → src/exporter/video_exporter.py
- `TestAlignEngine` --uses--> `AlignmentResult`  [INFERRED]
  tests/test_align_engine.py → src/align_engine/align_engine.py
- `TestDurationDirector` --uses--> `SpeechCueAlignEngine`  [INFERRED]
  tests/test_duration_director.py → src/align_engine/align_engine.py

## Import Cycles
- None detected.

## Communities (15 total, 5 thin omitted)

### Community 0 - "server.py"
Cohesion: 0.10
Nodes (19): argparse, http, http_server, mimetypes, SimpleHTTPRequestHandler, threading, time, urllib_parse (+11 more)

### Community 1 - "VisualChoreographer"
Cohesion: 0.14
Nodes (13): Image, ImageDraw, skipUnless, main(), Renders a single 1080x1920 video frame for the given scene and timestamp., Renders video frames applying Picture-Book Motion choreographic rules., Loads and caches source artwork in RGBA format., Draws word-wrapped text, centered at x, and returns total height. (+5 more)

### Community 2 - "SpeechCueAlignEngine"
Cohesion: 0.14
Nodes (10): Path, Align speech segments from audio with script scenes based on narrative cadence.…, Export alignment to both human-readable text and JSON., Analyzes voice-over audio and aligns it with scene scripts to determine optimal…, Get exact duration of audio file in seconds via ffprobe or wave/fallback., Parse script file into structured [(scene_title, scene_text)] entries. Supports…, SpeechCueAlignEngine, Methods: (+2 more)

### Community 3 - "FB-2minutes Storymaker"
Cohesion: 0.10
Nodes (19): 1. Prerequisites, 1. Voice-Over Audio (`assets/voice-over/narration.mp3` or `.wav`), 2. Automated One-Command Setup, 2. Scene Script (`assets/scripts/story.txt`), 3. Generate the Master Video via CLI, 3. Visual Assets (`assets/visuals/story_visuals.zip`), ⚙️ CLI Reference, Core Philosophy: "Picture-Book Motion" (+11 more)

### Community 4 - "duration_director.py"
Cohesion: 0.13
Nodes (19): dataclasses, json, pathlib, re, AlignmentResult, main(), Speech-Cue Align Engine for FB 2minutes Storymaker Implements audio analysis…, Represents a segment of speech with timing information. (+11 more)

### Community 6 - "generate_sample_assets.py"
Cohesion: 0.18
Nodes (12): math, pil, create_gradient(), generate_audio_voiceover(), generate_scene_image(), Path, Draw vertical linear gradient., Generate a high-resolution 1080x1080 scene illustration card. (+4 more)

### Community 7 - "video_exporter.py"
Cohesion: 0.11
Nodes (17): main(), MasterTimeline, Path, Builds the MasterTimeline combining speech alignment segments with visual…, Export timeline manifest to JSON for visual choreographer and exporter., Complete master timeline manifest., Directs scene duration allocation and pairs visual assets with aligned speech…, Locate and order image files from a zip archive or directory. Orders by numeric… (+9 more)

### Community 8 - "main.py"
Cohesion: 0.12
Nodes (25): check_assets(), generate_sample_assets(), main(), FB 2minutes Storymaker - Automated Storytelling Engine Based on the…, Check if required assets are present in assets/ directory., Invoke the sample asset generator., Executes the full Picture-Book Motion storytelling pipeline., Starts the local web studio interface. (+17 more)

### Community 9 - "Speech-Cue Align Engine"
Cohesion: 0.17
Nodes (11): 1. Audio Analysis, 2. Speech-Script Alignment, As a Module, Command Line Interface, Dependencies, Functionality, Future Enhancements, Integration with Pipeline (+3 more)

### Community 10 - "Example Workflow for FB 2minutes Storymaker"
Cohesion: 0.18
Nodes (10): 1. Voice-Over (`assets/voice-over/narration.mp3` or `.wav`), 2. Scene Script (`assets/scripts/story.txt`), 3. Visual Assets (`assets/visuals/story_visuals.zip`), Example Workflow for FB 2minutes Storymaker, Option A: Via Command Line, Option B: Via Creative Studio Web UI, Step 1: Prepare Your Assets, Step 2: Run the Storymaker (+2 more)

## Knowledge Gaps
- **33 isolated node(s):** `setup_local.sh script`, `1. Voice-Over (`assets/voice-over/narration.mp3` or `.wav`)`, `2. Scene Script (`assets/scripts/story.txt`)`, `3. Visual Assets (`assets/visuals/story_visuals.zip`)`, `Option A: Via Command Line` (+28 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 111 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SpeechCueAlignEngine` connect `SpeechCueAlignEngine` to `main.py`, `server.py`, `duration_director.py`, `video_exporter.py`?**
  _High betweenness centrality (0.166) - this node is a cross-community bridge._
- **Why does `Core Classes` connect `duration_director.py` to `SpeechCueAlignEngine`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `Implementation Details` connect `duration_director.py` to `Speech-Cue Align Engine`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `SpeechCueAlignEngine` (e.g. with `run_pipeline()` and ``SpeechCueAlignEngine``) actually correct?**
  _`SpeechCueAlignEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `VisualChoreographer` (e.g. with `SceneTimeline` and `VideoExporter`) actually correct?**
  _`VisualChoreographer` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `SceneDurationDirector` (e.g. with `run_pipeline()` and `AlignmentResult`) actually correct?**
  _`SceneDurationDirector` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `SceneTimeline` (e.g. with `VisualChoreographer` and `VideoExporter`) actually correct?**
  _`SceneTimeline` has 4 INFERRED edges - model-reasoned connections that need verification._