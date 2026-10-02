import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import termux_server_helper


class TestTermuxServerHelper(unittest.TestCase):
    def test_enable_and_disable_termux_boot(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_home = Path(tmp) / "home"
            with patch.object(Path, "home", return_value=fake_home):
                repo_dir = Path(tmp) / "repo"
                repo_dir.mkdir()

                self.assertFalse(termux_server_helper.is_termux_boot_enabled())
                ok, script_path = termux_server_helper.enable_termux_boot(repo_dir)
                self.assertTrue(ok)
                self.assertTrue(Path(script_path).exists())
                self.assertTrue(termux_server_helper.is_termux_boot_enabled())

                # Check contents of boot script
                content = Path(script_path).read_text(encoding="utf-8")
                self.assertIn("termux-wake-lock", content)
                self.assertIn("start_server", content)
                self.assertIn(str(repo_dir), content)

                # Test disable
                ok, msg = termux_server_helper.disable_termux_boot()
                self.assertTrue(ok)
                self.assertFalse(termux_server_helper.is_termux_boot_enabled())

    def test_get_battery_status_parses_json(self):
        fake_json = json.dumps({
            "percentage": 88,
            "status": "CHARGING",
            "plugged": "PLUGGED_AC",
            "temperature": 32.5,
        })
        with patch("shutil.which", return_value="/data/data/com.termux/files/usr/bin/termux-battery-status"), \
             patch("subprocess.run", return_value=Mock(returncode=0, stdout=fake_json)):
            status = termux_server_helper.get_battery_status()
            self.assertIsNotNone(status)
            self.assertIn("88%", status)
            self.assertIn("CHARGING", status)
            self.assertIn("AC", status)
            self.assertIn("32.5°C", status)

    def test_set_screen_brightness_clamps_and_runs_command(self):
        with patch("shutil.which", return_value="/data/data/com.termux/files/usr/bin/termux-brightness"), \
             patch("subprocess.run", return_value=Mock(returncode=0)) as mock_run:
            self.assertTrue(termux_server_helper.set_screen_brightness(-10))
            mock_run.assert_called_with(
                ["termux-brightness", "0"],
                stdout=-3, stderr=-3, check=False, timeout=2
            )

            self.assertTrue(termux_server_helper.set_screen_brightness(500))
            mock_run.assert_called_with(
                ["termux-brightness", "255"],
                stdout=-3, stderr=-3, check=False, timeout=2
            )


if __name__ == "__main__":
    unittest.main()
