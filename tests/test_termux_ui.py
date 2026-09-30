import contextlib
import io
import os
import re
import shutil
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import termux_ui
from termux_ui import _draw_interactive_menu, print_status_box


class TestTermuxUI(unittest.TestCase):
    def test_status_box_fits_terminal_and_truncates_long_details(self):
        status = {
            key: (True, "assets/" + "very-long-file-name-" * 5)
            for key in ("voice", "script", "visuals", "video")
        }
        output = io.StringIO()
        with patch("termux_ui.shutil.get_terminal_size", return_value=os.terminal_size((52, 24))):
            with contextlib.redirect_stdout(output):
                print_status_box(status)

        lines = [re.sub(r"\033\[[0-9;]*m", "", line) for line in output.getvalue().splitlines()]
        self.assertTrue(all(len(line) <= 50 for line in lines))
        self.assertEqual(len(lines[0]), 50)
        self.assertEqual(len(lines[-1]), 50)
        self.assertTrue(all("…" in line for line in lines[1:-1]))

    def test_interactive_menu_navigates_with_arrow_keys(self):
        class FakeScreen:
            def __init__(self, keys):
                self.keys = list(keys)

            def keypad(self, enabled):
                pass

            def erase(self):
                pass

            def getmaxyx(self):
                return 24, 80

            def addnstr(self, *args):
                pass

            def refresh(self):
                pass

            def getch(self):
                return self.keys.pop(0)

        status = {key: (True, f"assets/{key}") for key in ("voice", "script", "visuals", "video")}
        with patch("termux_ui.curses.has_colors", return_value=False), patch(
            "termux_ui.curses.color_pair", return_value=0
        ):
            self.assertEqual(_draw_interactive_menu(FakeScreen([termux_ui.curses.KEY_DOWN, 10]), status), "2")
            self.assertEqual(_draw_interactive_menu(FakeScreen([ord("6")]), status), "6")


if __name__ == "__main__":
    unittest.main()
