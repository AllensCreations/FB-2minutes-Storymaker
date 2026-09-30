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

from termux_ui import print_status_box


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


if __name__ == "__main__":
    unittest.main()
