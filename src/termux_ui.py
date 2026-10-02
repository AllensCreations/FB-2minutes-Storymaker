"""
Interactive Terminal UI (TUI) for Termux & Android
Provides a mobile-optimized terminal console with:
- ASCII studio dashboard & live asset readiness
- Web Studio launcher that automatically opens the Android browser (termux-open-url)
- Scene Mapping Matrix viewer showing -35dB cut timestamps
- Mobile video launcher (termux-open) to watch the exported MP4 in Android media player
- Dependency inspector & local .env editor
"""

import os
import shutil
import shlex
import subprocess
import sys
import textwrap
import time
from pathlib import Path

try:
    import curses
except ImportError:
    curses = None

# Add src to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from align_engine import SpeechCueAlignEngine
from archive_manager import get_local_ip
from deps_helper import is_termux
from duration_director import SceneDurationDirector

ASSETS_DIR = REPO_ROOT / "assets"
SCRIPTS_DIR = ASSETS_DIR / "scripts"
VOICE_DIR = ASSETS_DIR / "voice-over"
VISUALS_DIR = ASSETS_DIR / "visuals"
OUTPUT_DIR = ASSETS_DIR / "output"
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
    width = max(42, min(72, shutil.get_terminal_size((80, 24)).columns - 2))
    detail_width = width - 34
    title = "┌─ STORY ASSETS " + "─" * (width - 17) + "┐"
    print(f"{C_BOLD}{title}{C_RESET}")

    def render_row(icon, label, found, detail):
        tag = f"{C_GREEN}[ READY  ]{C_RESET}" if found else f"{C_RED}[ MISSING]{C_RESET}"
        detail = textwrap.shorten(detail, width=detail_width, placeholder="…")
        print(f"│ {icon} {C_BOLD}{label:<15}{C_RESET} {tag} {C_GRAY}{detail:<{detail_width}}{C_RESET} │")

    render_row("🎙️", "Voice-over", status["voice"][0], status["voice"][1])
    render_row("📜", "Script", status["script"][0], status["script"][1])
    render_row("🖼️", "Visuals", status["visuals"][0], status["visuals"][1])
    render_row("🎬", "Master MP4", status["video"][0], status["video"][1])

    print(f"{C_BOLD}└{'─' * (width - 2)}┘{C_RESET}")


def _draw_interactive_menu(stdscr, status):
    choices = [
        ("1", "Open Web Studio"),
        ("2", "Inspect scene timing"),
        ("3", "Play latest video"),
        ("4", "Edit .env settings"),
        ("5", "Check dependencies"),
        ("6", "Check for updates"),
        ("7", "Run as LAN Server (Phone Server Mode)"),
        ("0", "Exit"),
    ]
    selected = 0
    first_visible = 0
    stdscr.keypad(True)

    if curses.has_colors():
        try:
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        except curses.error:
            pass

    while True:
        stdscr.erase()
        height, width = stdscr.getmaxyx()

        def write(y, text, attr=0, centered=False):
            if 0 <= y < height - 1 and width > 1:
                x = max(0, (width - len(text)) // 2) if centered else 2
                stdscr.addnstr(y, x, text, max(0, width - x - 1), attr)

        write(1, "FB 2MINUTES STORYMAKER", curses.color_pair(3) | curses.A_BOLD, centered=True)
        write(2, "Create, review, and publish story videos", curses.A_DIM, centered=True)
        write(4, "STORY ASSETS", curses.A_BOLD)

        asset_labels = (
            ("VOICE-OVER", status["voice"]),
            ("SCRIPT", status["script"]),
            ("VISUALS", status["visuals"]),
            ("MASTER MP4", status["video"]),
        )
        for row, (label, (ready, detail)) in enumerate(asset_labels, start=5):
            state = "READY  " if ready else "MISSING"
            color = curses.color_pair(1 if ready else 2)
            short_detail = textwrap.shorten(detail, width=max(8, width - 34), placeholder="...")
            write(row, f"{label:<12} [{state}]  {short_detail}", color)

        menu_top = 10
        menu_bottom = max(menu_top + 1, height - 3)
        visible_count = menu_bottom - menu_top
        if selected < first_visible:
            first_visible = selected
        elif selected >= first_visible + visible_count:
            first_visible = selected - visible_count + 1
        write(menu_top - 1, "ACTIONS", curses.A_BOLD)
        for row, index in enumerate(range(first_visible, min(len(choices), first_visible + visible_count))):
            key, label = choices[index]
            y = menu_top + row
            if index == selected:
                write(y, f">  [{key}] {label}", curses.A_REVERSE | curses.A_BOLD)
            else:
                write(y, f"   [{key}] {label}")

        write(height - 2, "UP/DOWN or J/K: move    ENTER: select    Q: quit", curses.A_DIM, centered=True)
        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k"), ord("K")):
            selected = (selected - 1) % len(choices)
        elif key in (curses.KEY_DOWN, ord("j"), ord("J")):
            selected = (selected + 1) % len(choices)
        elif key in (curses.KEY_ENTER, 10, 13):
            return choices[selected][0]
        elif ord("0") <= key <= ord("7"):
            return chr(key)
        elif key in (ord("q"), ord("Q")):
            return "0"


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


def launch_lan_server_mode():
    """Runs Web Studio in headless host/server mode for access from other devices on the LAN."""
    clear_screen()
    print_banner()
    port = 8000
    lan_ip = get_local_ip()

    has_wake_lock = False
    if is_termux() and shutil.which("termux-wake-lock") is not None:
        try:
            subprocess.run(["termux-wake-lock"], check=False)
            has_wake_lock = True
        except Exception:
            pass

    print(f"\n{C_GREEN}{C_BOLD}📱 OLD PHONE SERVER MODE (LAN HOST){C_RESET}")
    print(f"{C_GRAY}Server is active for other devices connected to the same Wi-Fi / Hotspot.{C_RESET}")
    if has_wake_lock:
        print(f"{C_CYAN}🔋 Termux wake-lock active (prevents phone from sleeping).{C_RESET}")
    print(f"\n{C_BOLD}👉 Open this URL on your PC, tablet, or secondary phone:{C_RESET}")
    print(f"   {C_ORANGE}{C_BOLD}http://{lan_ip}:{port}{C_RESET}\n")
    print(f"{C_AMBER}Press [Ctrl + C] to stop the server and return to the menu.{C_RESET}\n")

    from web.server import start_server
    try:
        start_server(host="0.0.0.0", port=port, open_browser=False)
    except KeyboardInterrupt:
        print(f"\n{C_GRAY}Server stopped.{C_RESET}")
        time.sleep(0.5)
    finally:
        if has_wake_lock and shutil.which("termux-wake-unlock") is not None:
            try:
                subprocess.run(["termux-wake-unlock"], check=False)
            except Exception:
                pass


def edit_env_settings():
    """Open the local environment settings in the user's preferred terminal editor."""
    clear_screen()
    print_banner()
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        example_path = REPO_ROOT / ".env.example"
        if example_path.exists():
            shutil.copyfile(example_path, env_path)
        else:
            env_path.touch()

    editor = shlex.split(os.environ.get("VISUAL") or os.environ.get("EDITOR") or "")
    if not editor:
        editor = next(([path] for name in ("nano", "vi") if (path := shutil.which(name))), [])
    if not editor:
        print(f"{C_RED}No terminal editor found. Set EDITOR or VISUAL and try again.{C_RESET}")
    else:
        subprocess.run([*editor, str(env_path)], check=False)


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


def _check_for_updates(update_checker):
    try:
        if update_checker():
            os.execv(sys.executable, [sys.executable, str(REPO_ROOT / "main.py"), "--tui"])
    except RuntimeError as error:
        print(f"{C_RED}Update check failed: {error}{C_RESET}")
    input(f"\n{C_DIM}Press [Enter] to return to menu...{C_RESET}")


def run_tui_main(update_checker=None):
    """Main event loop for the Termux TUI."""
    while True:
        status = get_asset_status()
        if curses and sys.stdin.isatty() and sys.stdout.isatty():
            try:
                choice = curses.wrapper(_draw_interactive_menu, status)
            except curses.error:
                choice = None
        else:
            choice = None

        if choice is None:
            clear_screen()
            print_banner()
            print_status_box(status)
            print(f"\n{C_BOLD}ACTIONS{C_RESET}")
            print(f"  {C_CYAN}[1]{C_RESET} Open Web Studio")
            print(f"  {C_BLUE}[2]{C_RESET} Inspect scene timing")
            print(f"  {C_GREEN}[3]{C_RESET} Play latest video")
            print(f"  {C_AMBER}[4]{C_RESET} Edit .env settings")
            print(f"  {C_GRAY}[5]{C_RESET} Check dependencies")
            print(f"  {C_CYAN}[6]{C_RESET} Check for updates")
            print(f"  {C_GREEN}[7]{C_RESET} Run as LAN Server (Phone Server Mode)")
            print(f"\n{C_DIM}Type a number and press Enter · [0] Exit{C_RESET}")
            choice = input(f"\n{C_BOLD}Action › {C_RESET}").strip().lower()

        if choice == "1":
            launch_web_studio_and_browser()
        elif choice == "2":
            show_scene_matrix()
        elif choice == "3":
            open_media_file(OUTPUT_DIR / "final_story.mp4")
            time.sleep(1)
        elif choice == "4":
            edit_env_settings()
        elif choice == "5":
            run_termux_health_check()
        elif choice == "6":
            if update_checker is None:
                from main import check_for_updates
                update_checker = check_for_updates
            _check_for_updates(update_checker)
        elif choice == "7":
            launch_lan_server_mode()
        elif choice in ("0", "q", "quit", "exit"):
            clear_screen()
            print(f"{C_ORANGE}👋 Thank you for using FB-2minutes Storymaker!{C_RESET}\n")
            break
        else:
            print(f"\n{C_RED}Choose one of the listed actions (1-7), or 0 to exit.{C_RESET}")
            input(f"{C_DIM}Press Enter to continue...{C_RESET}")


if __name__ == "__main__":
    from main import check_for_updates
    run_tui_main(check_for_updates)
