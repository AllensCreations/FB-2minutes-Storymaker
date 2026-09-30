import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from main import check_for_updates, main


class TestStartupUpdates(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.remote = root / "remote.git"
        self.seed = root / "seed"
        self.checkout = root / "checkout"
        subprocess.run(["git", "init", "--bare", str(self.remote)], check=True, capture_output=True)
        self.seed.mkdir()
        self._git(self.seed, "init", "-b", "main")
        self._git(self.seed, "config", "user.name", "Test")
        self._git(self.seed, "config", "user.email", "test@example.com")
        (self.seed / "VERSION").write_text("1.0.0\n", encoding="utf-8")
        self._git(self.seed, "add", "VERSION")
        self._git(self.seed, "commit", "-m", "Initial")
        self._git(self.seed, "remote", "add", "origin", str(self.remote))
        self._git(self.seed, "push", "-u", "origin", "main")
        subprocess.run(
            ["git", f"--git-dir={self.remote}", "symbolic-ref", "HEAD", "refs/heads/main"],
            check=True,
            capture_output=True,
        )
        self._git(self.seed.parent, "clone", str(self.remote), str(self.checkout))
        self._git(self.checkout, "config", "user.name", "Test")
        self._git(self.checkout, "config", "user.email", "test@example.com")

    def tearDown(self):
        self.temp_dir.cleanup()

    @staticmethod
    def _git(cwd, *args):
        return subprocess.run(
            ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
        ).stdout.strip()

    def test_fast_forwards_when_upstream_has_update(self):
        (self.seed / "VERSION").write_text("1.0.1\n", encoding="utf-8")
        self._git(self.seed, "commit", "--allow-empty", "-am", "Update")
        self._git(self.seed, "push")

        self.assertTrue(check_for_updates(self.checkout))
        self.assertEqual((self.checkout / "VERSION").read_text().strip(), "1.0.1")
        self.assertEqual(self._git(self.checkout, "rev-parse", "HEAD"), self._git(self.seed, "rev-parse", "HEAD"))

    def test_refuses_update_when_local_changes_exist(self):
        self._git(self.seed, "commit", "--allow-empty", "-m", "Update")
        self._git(self.seed, "push")
        (self.checkout / "VERSION").write_text("local edit\n", encoding="utf-8")

        with self.assertRaisesRegex(RuntimeError, "local changes prevent a safe update"):
            check_for_updates(self.checkout)

        self.assertEqual((self.checkout / "VERSION").read_text().strip(), "local edit")

    def test_reports_current_checkout_as_up_to_date(self):
        self.assertFalse(check_for_updates(self.checkout))

    def test_restarts_cli_after_update(self):
        with patch("main.sys.argv", ["main.py", "--check"]), patch(
            "main.check_for_updates", return_value=True
        ), patch("main.os.execv") as execv:
            main()

        execv.assert_called_once_with(
            sys.executable,
            [sys.executable, str(Path(__file__).resolve().parent.parent / "main.py"), "--check"],
        )


if __name__ == "__main__":
    unittest.main()
