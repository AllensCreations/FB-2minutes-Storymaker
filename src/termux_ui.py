"""
Interactive Terminal UI (TUI) for Termux & Android
Provides a mobile-optimized terminal console with:
- ASCII studio dashboard & live asset readiness
- One-touch video rendering with terminal progress animation
- Web Studio launcher that automatically opens the Android browser (termux-open-url)
- Scene Mapping Matrix viewer showing -35dB cut timestamps
- Mobile video launcher (termux-open) to watch the exported MP4 in Android media player
- Dependency inspector & sample story switcher
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Add src to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from align_engine import SpeechCueAlignEngine
from deps_helper import ensure_ffmpeg, ensure_pillow, is_termux
from duration_director import SceneDurationDirector

ASSETS_DIR = REPO_ROOT / "assets"
SCRIPTS_DIR = ASSETS_DIR / "scripts"
VOICE_DIR = ASSETS_DIR / "voice-over"
VISUALS_DIR = ASSETS_DIR / "visuals"
OUTPUT_DIR = ASSETS_DIR / "output"
PROCESSED_DIR = ASSETS_DIR / "processed"

# ANSI Color Codes
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_ORANGE = "\033[38;5;208m"
C_AMBER = "\033[38;5;214m"
C_GREEN = "\033[38;5;42m"
C_BLUE = "\033[38;5;75m"
C_RED = "\033[38;5;203m"
C_GRAY = "\033[38;5;244m"
C_CYAN = "\033[38;5;80m"


def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")


def print_banner():
    print(f"{C_ORANGE}{C_BOLD}╭─────────────────────────────────────────────────────────────╮{C_RESET}")
    print(f"{C_ORANGE}{C_BOLD}│  🎬 FB-2MINUTES STORYMAKER • TERMUX STUDIO                  │{C_RESET}")
    print(f"{C_ORANGE}{C_BOLD}│  {C_GRAY}Picture-Book Motion Engine & Interactive Console           {C_ORANGE}{C_BOLD}│{C_RESET}")
    print(f"{C_ORANGE}{C_BOLD}╰─────────────────────────────────────────────────────────────╯{C_RESET}")


def get_asset_status():
    has_voice = any(VOICE_DIR.glob("*.mp3")) or any(VOICE_DIR.glob("*.wav"))
    has_script = any(SCRIPTS_DIR.glob("*.txt"))
    has_visuals = any(VISUALS_DIR.glob("*.zip")) or any((VISUALS_DIR / "raw_frames").glob("*.png"))
    has_video = (OUTPUT_DIR / "final_story.mp4").exists()

    video_info = ""
    if has_video:
        size_mb = (OUTPUT_DIR / "final_story.mp4").stat().st_size / (1024 * 1024)
        video_info = f" ({size_mb:.2f} MB)"

    voice_path = "assets/voice-over/narration.mp3"
    voice_dur = ""
    if has_voice:
        try:
            aligner = SpeechCueAlignEngine()
            dur = aligner.get_audio_duration(VOICE_DIR / "narration.mp3")
            voice_dur = f" [{dur:.1f}s]"
        except Exception:
            pass

    script_lines = ""
    if has_script:
        try:
            with open(SCRIPTS_DIR / "story.txt", "r", encoding="utf-8") as f:
                lines = [l for l in f.read().splitlines() if l.strip() and not l.strip().startswith("#")]
                script_lines = f" [{len(lines)} beats]"
        except Exception:
            pass

    return {
        "voice": (has_voice, f"{voice_path}{voice_dur}"),
        "script": (has_script, f"assets/scripts/story.txt{script_lines}"),
        "visuals": (has_visuals, "assets/visuals/story_visuals.zip"),
        "video": (has_video, f"assets/output/final_story.mp4{video_info}")
    }


def print_status_box(status):
    print(f"{C_BOLD}┌─ Asset Readiness Dashboard ────────────────────────────────┐{C_RESET}")

    def render_row(icon, label, found, detail):
        tag = f"{C_GREEN}[✓ READY]{C_RESET}" if found else f"{C_RED}[✗ MISSING]{C_RESET}"
        print(f"│  {icon} {C_BOLD}{label:<14}{C_RESET} {tag} {C_GRAY}{detail:<30}{C_RESET} │")

    render_row("🎙️", "Voice-Over:", status["voice"][0], status["voice"][1])
    render_row("📜", "Script:", status["script"][0], status["script"][1])
    render_row("🖼️", "Visuals:", status["visuals"][0], status["visuals"][1])
    render_row("🎬", "Master MP4:", status["video"][0], status["video"][1])

    print(f"{C_BOLD}└────────────────────────────────────────────────────────────┘{C_RESET}")


def open_url_in_browser(url: str):
    """Opens a URL using Termux browser intent or system desktop browser."""
    print(f"{C_CYAN}🌐 Launching browser for: {url}...{C_RESET}")
    if shutil.which("termux-open-url") is not None:
        subprocess.run(["termux-open-url", url])
    elif shutil.which("xdg-open") is not None:
        subprocess.run(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif shutil.which("open") is not None:
        subprocess.run(["open", url])
    else:
        print(f"👉 Please open in your mobile browser: {url}")


def open_media_file(file_path: Path):
    """Opens an exported video file in Android default player."""
    if not file_path.exists():
        print(f"{C_RED}❌ File not found: {file_path}{C_RESET}")
        return

    print(f"{C_GREEN}🎬 Opening {file_path.name} in media player...{C_RESET}")
    if shutil.which("termux-open") is not None:
        subprocess.run(["termux-open", str(file_path)])
    elif shutil.which("xdg-open") is not None:
        subprocess.run(["xdg-open", str(file_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif shutil.which("open") is not None:
        subprocess.run(["open", str(file_path)])
    else:
        print(f"👉 Video saved at: {file_path.resolve()}")


def run_video_render():
    """Runs the full Picture-Book Motion video export pipeline with live terminal progress."""
    clear_screen()
    print_banner()
    print(f"\n{C_ORANGE}{C_BOLD}🚀 Starting Master Video Render...{C_RESET}\n")

    if not ensure_pillow() or not ensure_ffmpeg():
        print(f"{C_RED}❌ Missing dependencies. Run option 6 to install.{C_RESET}")
        input(f"\n{C_DIM}Press [Enter] to return to menu...{C_RESET}")
        return

    from exporter import VideoExporter

    voice_path = VOICE_DIR / "narration.mp3"
    script_path = SCRIPTS_DIR / "story.txt"
    visuals_path = VISUALS_DIR / "story_visuals.zip"
    output_path = OUTPUT_DIR / "final_story.mp4"

    try:
        # Step 1: Align
        print(f"{C_BLUE}[1/3] Speech-Cue Alignment...{C_RESET}")
        aligner = SpeechCueAlignEngine()
        alignment = aligner.align_speech_with_script(voice_path, script_path)

        # Step 2: Duration Director
        print(f"\n{C_BLUE}[2/3] Scene Duration Director...{C_RESET}")
        director = SceneDurationDirector()
        timeline = director.build_timeline(alignment, visuals_path, fps=24)

        # Step 3: Exporter with Progress Bar
        ans_cap = input(f"\n{C_AMBER}💬 Include TikTok subtitle captions? [Y/n]: {C_RESET}").strip().lower()
        show_captions = (ans_cap != "n")
        print(f"\n{C_BLUE}[3/3] Picture-Book Motion Video Exporter (FFmpeg, captions: {'ON' if show_captions else 'OFF'})...{C_RESET}")
        exporter = VideoExporter(fps=24)

        def on_progress(percent: float, msg: str):
            bar_len = 24
            filled = int(bar_len * (percent / 100.0))
            bar = "█" * filled + "░" * (bar_len - filled)
            sys.stdout.write(f"\r  {C_ORANGE}[{bar}]{C_RESET} {percent:5.1f}% | {msg[:35]:<35}")
            sys.stdout.flush()

        exporter.export_video(timeline, voice_path, output_path, progress_callback=on_progress, show_captions=show_captions)
        print("\n\n" + f"{C_GREEN}{C_BOLD}🎉 Render completed successfully!{C_RESET}")
        print(f"📁 Video Location: {C_BOLD}{output_path}{C_RESET}")

        # Prompt to open immediately on Termux
        if is_termux() or shutil.which("termux-open") is not None:
            ans = input(f"\n{C_AMBER}▶️ Open video in Android video player now? [Y/n]: {C_RESET}").strip().lower()
            if ans != "n":
                open_media_file(output_path)

    except Exception as e:
        print(f"\n{C_RED}❌ Error during render: {e}{C_RESET}")

    input(f"\n{C_DIM}Press [Enter] to return to menu...{C_RESET}")


def show_scene_matrix():
    """Displays the Scene Mapping Matrix with -35dB cut points."""
    clear_screen()
    print_banner()
    print(f"\n{C_BOLD}📊 Scene Mapping Matrix & -35dB Silence Cut Markers{C_RESET}\n")

    voice_path = VOICE_DIR / "narration.mp3"
    script_path = SCRIPTS_DIR / "story.txt"
    visuals_path = VISUALS_DIR / "story_visuals.zip"

    try:
        aligner = SpeechCueAlignEngine()
        alignment = aligner.align_speech_with_script(voice_path, script_path)
        director = SceneDurationDirector()
        timeline = director.build_timeline(alignment, visuals_path, fps=24)

        print(f"{C_GRAY}Audio Duration: {alignment.total_duration:.2f}s | Total Scenes: {len(timeline.scenes)}{C_RESET}\n")
        print(f"{C_BOLD}{'Scene':<8} {'Time Range':<16} {'Duration':<10} {'Transition':<14} {'Narration Excerpt'}{C_RESET}")
        print("─" * 70)

        for s in timeline.scenes:
            trange = f"{s.start_time:.1f}s - {s.end_time:.1f}s"
            dur = f"{s.duration:.1f}s"
            excerpt = s.text[:32] + "..." if len(s.text) > 32 else s.text
            print(f"{C_ORANGE}#{s.scene_index + 1:<7}{C_RESET} {trange:<16} {dur:<10} {C_CYAN}{s.transition_in:<14}{C_RESET} {excerpt}")

        print("─" * 70)
    except Exception as e:
        print(f"{C_RED}❌ Could not compute matrix: {e}{C_RESET}")

    input(f"\n{C_DIM}Press [Enter] to return to menu...{C_RESET}")


def launch_web_studio_and_browser():
    """Starts the Web Studio server and opens it in Android browser."""
    clear_screen()
    print_banner()
    port = 8000
    print(f"\n{C_GREEN}{C_BOLD}🌐 Launching Creative Studio Web UI...{C_RESET}")
    print(f"\n{C_AMBER}Web Studio is starting! Press [Ctrl + C] to stop and return to menu.{C_RESET}\n")
    from web.server import start_server
    try:
        start_server(host="0.0.0.0", port=port, open_browser=True)
    except KeyboardInterrupt:
        print(f"\n{C_GRAY}Web server stopped.{C_RESET}")
        time.sleep(0.5)


def reset_or_switch_sample_story():
    """Menu to switch demo story theme (Scout & Jem vs Elsa the Baker)."""
    clear_screen()
    print_banner()
    print(f"\n{C_BOLD}🎨 Sample Story Switcher & Reset{C_RESET}\n")
    print("  [1] 👒 Scout & Jem (Southern Town, 4 Scenes, 24.0s)")
    print("  [2] 🥐 Elsa the Baker (Fairytale Bakery, 6 Scenes, 21.0s)")
    print("  [0] ↩️  Back")

    choice = input(f"\n{C_AMBER}Select story [1/2]: {C_RESET}").strip()
    if choice == "1":
        print(f"\n{C_BLUE}Generating Scout & Jem preloaded assets (Southern Town, 4 scenes)...{C_RESET}")
        from scripts.generate_sample_assets import generate_all_sample_assets
        generate_all_sample_assets(theme="scout")
        print(f"{C_GREEN}✓ Scout & Jem story activated! (Syncs with Web Studio & CLI){C_RESET}")
        time.sleep(1.2)
    elif choice == "2":
        print(f"\n{C_BLUE}Generating Elsa the Baker preloaded assets (Fairytale Bakery, 6 scenes)...{C_RESET}")
        from scripts.generate_sample_assets import generate_all_sample_assets
        generate_all_sample_assets(theme="elsa")
        print(f"{C_GREEN}✓ Elsa the Baker story activated! (Syncs with Web Studio & CLI){C_RESET}")
        time.sleep(1.2)


def run_termux_health_check():
    """Validates packages and allows 1-click Termux package repair."""
    clear_screen()
    print_banner()
    print(f"\n{C_BOLD}🛠️  Termux Environment Health Check{C_RESET}\n")

    py_ok = sys.version_info >= (3, 8)
    print(f"  Python:  {'✓ ' + sys.version.split()[0] if py_ok else '✗ Outdated'}")

    pil_ok = False
    try:
        import PIL
        pil_ok = True
        print(f"  Pillow:  ✓ Installed ({PIL.__version__})")
    except ImportError:
        print(f"  Pillow:  {C_RED}✗ Not Installed{C_RESET}")

    ffmpeg_ok = shutil.which("ffmpeg") is not None
    print(f"  FFmpeg:  {'✓ Found' if ffmpeg_ok else C_RED + '✗ Not Found' + C_RESET}")

    is_tx = is_termux()
    print(f"  Termux:  {'✓ Detected (Android)' if is_tx else 'ℹ️ Standard Linux/Other'}")

    if not (pil_ok and ffmpeg_ok):
        print(f"\n{C_AMBER}⚡ Some dependencies are missing.{C_RESET}")
        if is_tx:
            ans = input(f"Install 'python-pillow' and 'ffmpeg' via Termux pkg now? [Y/n]: ").strip().lower()
            if ans != "n":
                subprocess.run(["pkg", "install", "-y", "python-pillow", "ffmpeg"])
        else:
            ans = input(f"Install Pillow via pip now? [Y/n]: ").strip().lower()
            if ans != "n":
                subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"])

    input(f"\n{C_DIM}Press [Enter] to return to menu...{C_RESET}")


def run_tui_main():
    """Main event loop for the Termux TUI."""
    while True:
        clear_screen()
        print_banner()
        status = get_asset_status()
        print_status_box(status)

        print(f"\n{C_BOLD}Interactive Controls:{C_RESET}")
        print(f"  {C_ORANGE}[1]{C_RESET} 🚀 {C_BOLD}Render Master Video{C_RESET} (9:16 Picture-Book Motion MP4)")
        print(f"  {C_CYAN}[2]{C_RESET} 🌐 {C_BOLD}Launch Web Studio & Open Browser{C_RESET} (Interactive Waveform)")
        print(f"  {C_BLUE}[3]{C_RESET} 📊 {C_BOLD}Inspect Scene Mapping Matrix{C_RESET} (-35dB Cut Timestamps)")
        print(f"  {C_GREEN}[4]{C_RESET} ▶️  {C_BOLD}Watch Output Video in Android Player{C_RESET}")
        print(f"  {C_AMBER}[5]{C_RESET} 🎨 {C_BOLD}Switch or Reset Sample Story Assets{C_RESET}")
        print(f"  {C_GRAY}[6]{C_RESET} 🛠️  {C_BOLD}Termux Dependency Health Check{C_RESET}")
        print(f"  {C_RED}[0]{C_RESET} 🚪 {C_BOLD}Exit Studio{C_RESET}")

        choice = input(f"\n{C_BOLD}Select an action [0-6]: {C_RESET}").strip()

        if choice == "1":
            run_video_render()
        elif choice == "2":
            launch_web_studio_and_browser()
        elif choice == "3":
            show_scene_matrix()
        elif choice == "4":
            open_media_file(OUTPUT_DIR / "final_story.mp4")
            time.sleep(1)
        elif choice == "5":
            reset_or_switch_sample_story()
        elif choice == "6":
            run_termux_health_check()
        elif choice in ("0", "q", "quit", "exit"):
            clear_screen()
            print(f"{C_ORANGE}👋 Thank you for using FB-2minutes Storymaker!{C_RESET}\n")
            break


if __name__ == "__main__":
    run_tui_main()
