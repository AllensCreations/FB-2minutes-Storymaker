import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from port_helper import find_random_available_port, save_active_port, get_active_port


class TestPortHelper(unittest.TestCase):
    def test_find_random_available_port(self):
        port = find_random_available_port(min_port=7000, max_port=7500)
        self.assertIsInstance(port, int)
        self.assertGreaterEqual(port, 1024)
        self.assertLessEqual(port, 65535)

    def test_find_random_port_with_exclude(self):
        exclude = {7001, 7002, 7003}
        port = find_random_available_port(min_port=7001, max_port=7005, exclude=exclude)
        self.assertNotIn(port, exclude)

    def test_save_and_get_active_port(self):
        test_file = ".test_active_port"
        try:
            path = save_active_port(8765, filename=test_file)
            self.assertTrue(path.is_file())
            loaded = get_active_port(filename=test_file)
            self.assertEqual(loaded, 8765)
        finally:
            p = REPO_ROOT / test_file
            if p.is_file():
                p.unlink()

    def test_get_active_port_default_fallback(self):
        loaded = get_active_port(filename=".non_existent_port_file", default=9999)
        self.assertEqual(loaded, 9999)


if __name__ == "__main__":
    unittest.main()
