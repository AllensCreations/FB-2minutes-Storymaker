"""
Dependency Helper for FB 2minutes Storymaker
Detects platform (Termux, Linux, macOS, Windows) and auto-installs or validates
essential runtime dependencies (Pillow and FFmpeg).
"""

import os
import shutil
import subprocess
import sys


def is_termux() -> bool:
    """Detect if running in Termux on Android."""
    return (
        bool(os.environ.get("TERMUX_VERSION"))
        or (shutil.which("pkg") is not None and "com.termux" in os.environ.get("PREFIX", ""))
    )


def is_root() -> bool:
    """Check if running as root / superuser."""
    return hasattr(os, "geteuid") and os.geteuid() == 0


def ensure_pillow() -> bool:
    """
    Checks if Pillow (PIL) is installed.
    If missing, automatically attempts to install it based on the platform.
    Returns True if Pillow is available, False otherwise.
    """
    try:
        import PIL
        return True
    except ImportError:
        pass

    print("\n⚡ Required dependency 'Pillow' (PIL) is missing.")
    print("Attempting automatic installation for your environment...")

    # Platform 1: Termux (Android)
    if is_termux():
        print("📱 Termux environment detected! Installing pre-compiled 'python-pillow' package...")
        try:
            cmd = ["pkg", "install", "-y", "python-pillow"]
            res = subprocess.run(cmd, check=False)
            if res.returncode == 0:
                try:
                    import PIL
                    print("✅ Successfully installed python-pillow in Termux!")
                    return True
                except ImportError:
                    pass
        except Exception as e:
            print(f"Termux pkg install notice: {e}")

        # Fallback to apt in Termux
        if shutil.which("apt") is not None:
            try:
                subprocess.run(["apt", "install", "-y", "python-pillow"], check=False)
                import PIL
                print("✅ Successfully installed python-pillow via apt in Termux!")
                return True
            except (subprocess.SubprocessError, ImportError):
                pass

    # Platform 2: Debian / Ubuntu as root
    if is_root() and shutil.which("apt-get") is not None:
        print("🐧 Debian/Ubuntu system detected! Installing python3-pil via apt-get...")
        try:
            subprocess.run(["apt-get", "update", "-qq"], check=False)
            subprocess.run(["apt-get", "install", "-y", "-qq", "python3-pil"], check=False)
            try:
                import PIL
                print("✅ Successfully installed python3-pil via apt-get!")
                return True
            except ImportError:
                pass
        except Exception:
            pass

    # Platform 3: Standard pip install
    print("📦 Trying pip install Pillow...")
    pip_cmds = [
        [sys.executable, "-m", "pip", "install", "Pillow>=10.0.0"],
        [sys.executable, "-m", "pip", "install", "Pillow>=10.0.0", "--break-system-packages"],
    ]

    for cmd in pip_cmds:
        try:
            res = subprocess.run(cmd, check=False)
            if res.returncode == 0:
                try:
                    import PIL
                    print("✅ Successfully installed Pillow via pip!")
                    return True
                except ImportError:
                    pass
        except Exception:
            pass

    # If all auto-install attempts failed, provide clear actionable guidance
    print("\n❌ Automatic installation of Pillow could not be completed.")
    print("👉 Please run the following command manually:")
    if is_termux():
        print("   pkg install -y python-pillow ffmpeg")
    elif shutil.which("apt-get") is not None:
        print("   sudo apt-get install -y python3-pil ffmpeg")
    else:
        print("   pip install Pillow")
    print()
    return False


def ensure_ffmpeg() -> bool:
    """
    Checks if ffmpeg is on PATH.
    If missing, attempts auto-install on Termux or prints actionable instructions.
    """
    if shutil.which("ffmpeg") is not None:
        return True

    print("\n⚠️ FFmpeg binary is not found on PATH.")
    if is_termux():
        print("📱 Termux detected! Installing ffmpeg via pkg...")
        try:
            res = subprocess.run(["pkg", "install", "-y", "ffmpeg"], check=False)
            if res.returncode == 0 and shutil.which("ffmpeg") is not None:
                print("✅ Successfully installed ffmpeg in Termux!")
                return True
        except Exception:
            pass

    if is_root() and shutil.which("apt-get") is not None:
        print("Installing ffmpeg via apt-get...")
        try:
            subprocess.run(["apt-get", "install", "-y", "ffmpeg"], check=False)
            if shutil.which("ffmpeg") is not None:
                print("✅ Successfully installed ffmpeg!")
                return True
        except Exception:
            pass

    print("👉 Please install FFmpeg:")
    if is_termux():
        print("   pkg install -y ffmpeg")
    elif shutil.which("apt-get") is not None:
        print("   sudo apt-get install -y ffmpeg")
    elif sys.platform == "darwin":
        print("   brew install ffmpeg")
    else:
        print("   winget install Gyan.FFmpeg")
    return False
