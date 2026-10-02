"""
FB 2minutes Storymaker - Automated Storytelling Engine
Based on the architectural blueprint for "Picture-Book Motion" storytelling videos.
"""

import argparse
import os
import subprocess
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


def run_pipeline(fps: int = 24, show_captions: bool = True):
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
    print(f"   Mode: 9:16 Full Image TikTok Video (Captions: {'ON' if show_captions else 'OFF'})")
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
    final_video = exporter.export_video(timeline, voice_path, output_path, show_captions=show_captions)

    print("\n" + "=" * 55)
    print("🎉 Master Story Video Successfully Generated!")
    print(f"📁 Video Location: {final_video}")
    print(f"🌐 Launch Web UI:  python3 main.py --web")
    print("=" * 55 + "\n")
    return final_video


def start_web_server(port=None, open_browser: bool = False):
    """Starts the local web studio interface."""
    ensure_pillow()
    from web.server import start_server
    start_server(host="0.0.0.0", port=port, open_browser=open_browser)


__version__ = "1.0.25"


def check_for_updates(repo_dir: Path = BASE_DIR) -> bool:
    """Fetch and fast-forward the current branch; fail closed if freshness is unknown."""
    def git(*args):
        try:
            return subprocess.run(
                ["git", *args],
                cwd=repo_dir,
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError) as error:
            detail = getattr(error, "stderr", None)
            raise RuntimeError(detail.strip() if detail else str(error)) from error

    if not (repo_dir / ".git").exists():
        raise RuntimeError("This installation has no Git checkout; reinstall it with install.sh.")

    upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    remote, _, branch = upstream.partition("/")
    if not remote or not branch:
        raise RuntimeError("The current branch has no configured upstream.")

    git("fetch", "--quiet", remote, branch)
    ahead, behind = map(int, git("rev-list", "--left-right", "--count", f"HEAD...{upstream}").split())

    if behind == 0:
        if ahead:
            print(f"ℹ️ Local branch is {ahead} commit(s) ahead of {upstream}.")
        else:
            print(f"✓ Storymaker is up to date ({upstream}).")
        return False

    if ahead:
        raise RuntimeError(f"Local branch has diverged from {upstream}; resolve it with Git before continuing.")
    if git("status", "--porcelain"):
        raise RuntimeError(f"An update is available on {upstream}, but local changes prevent a safe update.")

    git("merge", "--ff-only", upstream)
    print(f"⬆ Updated to the latest {upstream}; restarting.")
    return True


def main():
    parser = argparse.ArgumentParser(
        description=f"FB 2minutes Storymaker v{__version__} - Web-Based Storytelling Engine"
    )
    parser.add_argument("--version", "-v", action="version", version=f"FB 2minutes Storymaker v{__version__}")
    parser.add_argument("--port", type=int, default=None, help="Port for the Web UI (default: randomly assigned)")
    parser.add_argument("--open", action="store_true", help="Automatically open Web UI in browser")
    parser.add_argument("--check", action="store_true", help="Check asset status and exit")
    # Legacy/deprecated args for backward compatibility (no-op)
    parser.add_argument("--web", action="store_true", help="Launch the Web Studio directly")
    parser.add_argument("--tui", action="store_true", help="Launch the interactive terminal selector menu")
    parser.add_argument("--run", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--fps", type=int, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--no-captions", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    try:
        if check_for_updates():
            os.execv(sys.executable, [sys.executable, str(BASE_DIR / "main.py"), *sys.argv[1:]])
    except RuntimeError as error:
        parser.error(f"Unable to verify/update Storymaker: {error}")

    if args.check:
        print("FB 2minutes Storymaker - Asset Status Check")
        print("=" * 55)
        has_voice, has_scripts, has_visuals = check_assets()
        print("Asset Status:")
        print(f"  Voice-over (.mp3/.wav): {'✓ Found' if has_voice else '✗ Missing'}")
        print(f"  Scene Script (.txt):   {'✓ Found' if has_scripts else '✗ Missing'}")
        print(f"  Visual Assets (.zip):   {'✓ Found' if has_visuals else '✗ Missing'}")
        print()
        return

    if args.tui or (not args.web and sys.stdin.isatty() and sys.stdout.isatty()):
        from termux_ui import run_tui_main
        run_tui_main(check_for_updates)
        return

    # Non-interactive launches and explicit --web invocations open the Web Studio.
    from deps_helper import is_termux
    auto_open = args.open or is_termux()
    start_web_server(args.port, open_browser=auto_open)


if __name__ == "__main__":
    main()


# Top-level WSGI / Serverless exports for Vercel deployment (delegated to app.py)
from app import app, application, handler

__all__ = ["app", "application", "handler", "main", "run_pipeline"]