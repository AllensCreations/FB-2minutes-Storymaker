"""
Termux Server & Battery Guard Helper
Manages Termux:Boot autostart, wake-lock, battery monitoring, and screen preservation
for dedicated Android server operation.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def get_termux_boot_script_path() -> Path:
    """Return path to Termux:Boot autostart script."""
    return Path.home() / ".termux" / "boot" / "fb-storymaker-server.sh"


def is_termux_boot_enabled() -> bool:
    """Check if the autostart boot script exists and is executable."""
    p = get_termux_boot_script_path()
    return p.exists() and os.access(p, os.X_OK)


def enable_termux_boot(repo_dir: Path) -> Tuple[bool, str]:
    """Install Termux:Boot autostart script."""
    boot_dir = Path.home() / ".termux" / "boot"
    try:
        boot_dir.mkdir(parents=True, exist_ok=True)
        script_path = boot_dir / "fb-storymaker-server.sh"
        content = f"""#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# FB 2minutes Storymaker - Dedicated Server Boot Autostart
# Automatically launched on Android power-on via Termux:Boot
# ==============================================================================
if command -v termux-wake-lock >/dev/null 2>&1; then
    termux-wake-lock
fi

cd "{repo_dir.resolve()}" || exit 1

# Auto-restart loop with crash log persistence
while true; do
    python3 -c "from web.server import start_server; start_server(host='0.0.0.0', port=8000, open_browser=False)" >> assets/server.log 2>&1
    sleep 3
done
"""
        script_path.write_text(content, encoding="utf-8")
        script_path.chmod(0o755)
        return True, str(script_path)
    except Exception as e:
        return False, str(e)


def disable_termux_boot() -> Tuple[bool, str]:
    """Remove Termux:Boot autostart script."""
    script_path = get_termux_boot_script_path()
    try:
        if script_path.exists():
            script_path.unlink()
            return True, "Termux:Boot autostart disabled."
        return True, "Termux:Boot autostart was not enabled."
    except Exception as e:
        return False, str(e)


def get_battery_status() -> Optional[str]:
    """
    Fetch Android battery information using termux-battery-status if available.
    Returns formatted string like '92% • CHARGING (AC) • 31.5°C' or None.
    """
    if shutil.which("termux-battery-status") is None:
        return None

    try:
        res = subprocess.run(
            ["termux-battery-status"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            pct = data.get("percentage")
            status = data.get("status", "").upper()
            plugged = data.get("plugged", "").replace("PLUGGED_", "").upper()
            temp = data.get("temperature")

            parts = []
            if pct is not None:
                parts.append(f"{pct}%")
            if status:
                parts.append(f"{status}" + (f" ({plugged})" if plugged and plugged != "UNPLUGGED" else ""))
            if temp is not None:
                parts.append(f"{temp:.1f}°C")
            return " • ".join(parts) if parts else None
    except Exception:
        pass
    return None


def set_screen_brightness(level: int) -> bool:
    """
    Set Android screen brightness (0 to 255) using termux-brightness if available.
    0 dims the screen to minimum to prevent screen burn-in and save power.
    """
    if shutil.which("termux-brightness") is None:
        return False

    try:
        level = max(0, min(255, int(level)))
        res = subprocess.run(
            ["termux-brightness", str(level)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=2,
        )
        return res.returncode == 0
    except Exception:
        return False
