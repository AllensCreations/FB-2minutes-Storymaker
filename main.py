"""
FB 2minutes Storymaker - Automated Storytelling Engine
Based on the architectural blueprint for "Picture-Book Motion" storytelling videos.
"""

import argparse
import os
import sys
from pathlib import Path

# Add src directory to path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from deps_helper import ensure_ffmpeg, ensure_pillow


def check_assets():
    """Check if required assets are present in assets/ directory."""
    voice_over_dir = BASE_DIR / "assets" / "voice-over"
    scripts_dir = BASE_DIR / "assets" / "scripts"
    visuals_dir = BASE_DIR / "assets" / "visuals"
    output_dir = BASE_DIR / "assets" / "output"

    has_voice = any(voice_over_dir.glob("*.mp3")) or any(voice_over_dir.glob("*.wav"))
    has_scripts = any(scripts_dir.glob("*.txt"))
    has_visuals = any(visuals_dir.glob("*.zip")) or any((visuals_dir / "raw_frames").glob("*.png"))

    output_dir.mkdir(parents=True, exist_ok=True)
    return has_voice, has_scripts, has_visuals


def generate_sample_assets():
    """Invoke the sample asset generator."""
    if not ensure_pillow():
        print("❌ Cannot generate sample assets without Pillow. Please install Pillow and try again.")
        return

    from scripts.generate_sample_assets import generate_all_sample_assets
    generate_all_sample_assets()


def run_pipeline(fps: int = 24):
    """Executes the full Picture-Book Motion storytelling pipeline."""
    # Ensure dependencies before running
    if not ensure_pillow() or not ensure_ffmpeg():
        print("❌ Dependencies missing. Execution aborted.")
        sys.exit(1)

    # Lazy import pipeline modules once dependencies are guaranteed
    from align_engine import SpeechCueAlignEngine
    from duration_director import SceneDurationDirector
    from exporter import VideoExporter

    print("\n=======================================================")
    print("🎬 FB 2minutes Storymaker - Video Generation Pipeline")
    print("=======================================================")

    voice_path = BASE_DIR / "assets" / "voice-over" / "narration.mp3"
    script_path = BASE_DIR / "assets" / "scripts" / "story.txt"
    visuals_path = BASE_DIR / "assets" / "visuals" / "story_visuals.zip"
    output_path = BASE_DIR / "assets" / "output" / "final_story.mp4"
    processed_dir = BASE_DIR / "assets" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    if not voice_path.exists():
        wav_fallback = voice_path.with_suffix(".wav")
        if wav_fallback.exists():
            voice_path = wav_fallback

    # Step 1: Speech-Cue Align Engine
    print("\n[Step 1/3] Speech-Cue Alignment...")
    aligner = SpeechCueAlignEngine()
    alignment = aligner.align_speech_with_script(voice_path, script_path)
    aligner.export_alignment(alignment, processed_dir / "alignment.txt")

    # Step 2: Scene Duration Director
    print("\n[Step 2/3] Scene Duration Director...")
    director = SceneDurationDirector()
    timeline = director.build_timeline(alignment, visuals_path, fps=fps)
    director.export_timeline(timeline, processed_dir / "timeline.json")

    # Step 3: Visual Choreography & Exporter
    print("\n[Step 3/3] Visual Choreography & FFmpeg Master Video Exporter...")
    exporter = VideoExporter(fps=fps)
    final_video = exporter.export_video(timeline, voice_path, output_path)

    print("\n" + "=" * 55)
    print("🎉 Master Story Video Successfully Generated!")
    print(f"📁 Video Location: {final_video}")
    print(f"🌐 Launch Web UI:  python3 main.py --web")
    print("=" * 55 + "\n")
    return final_video


def start_web_server(port: int = 8000):
    """Starts the local web studio interface."""
    ensure_pillow()
    from web.server import start_server
    start_server(host="0.0.0.0", port=port)


def main():
    parser = argparse.ArgumentParser(description="FB 2minutes Storymaker - Automated Storytelling Engine")
    parser.add_argument("--run", action="store_true", help="Execute the complete story generation pipeline")
    parser.add_argument("--web", action="store_true", help="Launch the local Web UI Studio")
    parser.add_argument("--port", type=int, default=8000, help="Port for the Web UI (default: 8000)")
    parser.add_argument("--generate-assets", action="store_true", help="Generate or reset demo sample assets")
    parser.add_argument("--fps", type=int, default=24, help="Frames per second for output video (default: 24)")
    parser.add_argument("--check", action="store_true", help="Check asset status and exit")

    args = parser.parse_args()

    # Route: Web UI
    if args.web:
        start_web_server(args.port)
        return

    # Route: Generate Assets
    if args.generate_assets:
        generate_sample_assets()
        return

    print("FB 2minutes Storymaker - Automated Storytelling Engine")
    print("=" * 55)
    print("Architecture: Picture-Book Motion")
    print()

    has_voice, has_scripts, has_visuals = check_assets()
    print("Asset Status:")
    print(f"  Voice-over (.mp3/.wav): {'✓ Found' if has_voice else '✗ Missing'}")
    print(f"  Scene Script (.txt):   {'✓ Found' if has_scripts else '✗ Missing'}")
    print(f"  Visual Assets (.zip):   {'✓ Found' if has_visuals else '✗ Missing'}")
    print()

    if args.check:
        return

    if not (has_voice and has_scripts and has_visuals):
        print("⚡ Assets missing. Automatically generating sample story assets...")
        generate_sample_assets()

    # Run the storytelling pipeline
    run_pipeline(fps=args.fps)


if __name__ == "__main__":
    main()