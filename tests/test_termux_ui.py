import contextlib
import io
import os
import re
import shutil
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

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
            def __init__(self, keys, height=24):
                self.keys = list(keys)
                self.height = height
                self.lines = []

            def keypad(self, enabled):
                pass

            def erase(self):
                pass

            def getmaxyx(self):
                return self.height, 80

            def addnstr(self, *args):
                self.lines.append(args[2])

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
            self.assertEqual(_draw_interactive_menu(FakeScreen([ord("7")]), status), "7")

    def test_short_terminal_scrolls_arrow_menu_to_all_actions(self):
        class ShortScreen:
            def __init__(self):
                self.keys = [termux_ui.curses.KEY_DOWN] * 6 + [10]
                self.lines = []

            def keypad(self, enabled):
                pass

            def erase(self):
                pass

            def getmaxyx(self):
                return 16, 80

            def addnstr(self, y, x, text, limit, attr):
                self.lines.append(text)

            def refresh(self):
                pass

            def getch(self):
                return self.keys.pop(0)

        screen = ShortScreen()
        status = {key: (True, f"assets/{key}") for key in ("voice", "script", "visuals", "video")}
        with patch("termux_ui.curses.has_colors", return_value=False), patch(
            "termux_ui.curses.color_pair", return_value=0
        ):
            self.assertEqual(_draw_interactive_menu(screen, status), "7")
        self.assertTrue(any("[7] Check for updates" in line for line in screen.lines))
        self.assertFalse(any("sample story" in line.lower() for line in screen.lines))

    @patch("termux_ui.input")
    @patch("termux_ui.os.execv")
    def test_update_menu_restarts_dashboard_after_update(self, execv, _input):
        with patch("termux_ui.sys.executable", "/usr/bin/python"):
            termux_ui._check_for_updates(lambda: True)

        execv.assert_called_once_with(
            "/usr/bin/python",
            ["/usr/bin/python", str(REPO_ROOT / "main.py"), "--tui"],
        )

    @patch("termux_ui.input")
    @patch("termux_ui.os.execv")
    def test_update_menu_returns_to_dashboard_when_current(self, execv, _input):
        checker = Mock(return_value=False)
        termux_ui._check_for_updates(checker)

        checker.assert_called_once_with()
        execv.assert_not_called()

    def test_env_settings_opens_editor_and_creates_local_env_from_example(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env.example").write_text('GEMINI_API_KEY=""\n', encoding="utf-8")
            with patch("termux_ui.REPO_ROOT", root), patch.dict(
                "termux_ui.os.environ", {"EDITOR": "nano"}, clear=True
            ), patch("termux_ui.shutil.which", return_value="/usr/bin/nano"), patch(
                "termux_ui.subprocess.run"
            ) as run:
                termux_ui.edit_env_settings()

            self.assertEqual((root / ".env").read_text(encoding="utf-8"), 'GEMINI_API_KEY=""\n')
            self.assertEqual(run.call_args.args[0], ["nano", str(root / ".env")])


if __name__ == "__main__":
    unittest.main()
