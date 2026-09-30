"""
Port Helper for FB 2minutes Storymaker
Provides random available port discovery and port discovery persistence
to prevent server port overlap and address collision.
"""

import random
import socket
from pathlib import Path
from typing import Optional, Set

REPO_ROOT = Path(__file__).resolve().parent.parent


def find_random_available_port(
    host: str = "0.0.0.0",
    min_port: int = 5000,
    max_port: int = 9999,
    exclude: Optional[Set[int]] = None
) -> int:
    """
    Find a random available port within the specified range [min_port, max_port].
    Tests socket binding to ensure the port is currently free.
    Falls back to OS-assigned port 0 if all random attempts fail.
    """
    exclude_set = exclude or set()
    pool = [p for p in range(min_port, max_port + 1) if p not in exclude_set]
    
    if pool:
        # Sample random candidate ports
        candidates = random.sample(pool, min(len(pool), 200))
        for p in candidates:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((host, p))
                    return p
            except OSError:
                continue

    # Fallback to OS assigned ephemeral port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return s.getsockname()[1]


def save_active_port(port: int, filename: str = ".active_port") -> Path:
    """Save active server port to a root marker file for auto-discovery by client scripts."""
    target_path = REPO_ROOT / filename
    try:
        target_path.write_text(str(port).strip(), encoding="utf-8")
    except Exception:
        pass
    return target_path


def get_active_port(filename: str = ".active_port", default: Optional[int] = None) -> Optional[int]:
    """Read saved port from marker file if present."""
    target_path = REPO_ROOT / filename
    if target_path.is_file():
        try:
            val = int(target_path.read_text(encoding="utf-8").strip())
            if 1 <= val <= 65535:
                return val
        except Exception:
            pass
    return default
