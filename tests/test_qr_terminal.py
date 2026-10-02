import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from qr_terminal import generate_qr_matrix, render_qr_ansi, get_qr_terminal_display


class TestQRTerminal(unittest.TestCase):
    def test_generate_qr_matrix_for_valid_url(self):
        url = "http://192.168.1.100:8000"
        matrix = generate_qr_matrix(url)
        self.assertIsNotNone(matrix)
        self.assertEqual(len(matrix), 25)  # Version 2 is 25x25
        self.assertEqual(len(matrix[0]), 25)

        # Check top-left finder pattern is 7x7 with black border and 3x3 black center
        self.assertEqual(matrix[0][0], 1)
        self.assertEqual(matrix[0][6], 1)
        self.assertEqual(matrix[6][0], 1)
        self.assertEqual(matrix[6][6], 1)
        self.assertEqual(matrix[2][2], 1)
        self.assertEqual(matrix[1][1], 0)

    def test_render_qr_ansi_generates_blocks_with_quiet_zone(self):
        url = "http://10.0.0.5:8000"
        matrix = generate_qr_matrix(url)
        ansi = render_qr_ansi(matrix, border=1)
        self.assertIn("\033[47;30m", ansi)
        self.assertIn("\033[0m", ansi)
        lines = ansi.splitlines()
        # Matrix 25 + 2 border = 27 rows -> (27 + 1) // 2 = 14 lines
        self.assertEqual(len(lines), 14)

    def test_get_qr_terminal_display_respects_column_limits(self):
        url = "http://192.168.1.1:8000"
        # Narrow terminal should return empty string rather than corrupted wrapping
        self.assertEqual(get_qr_terminal_display(url, max_columns=15), "")
        # Standard width should return rendered QR code
        display = get_qr_terminal_display(url, max_columns=80)
        self.assertTrue(len(display) > 0)


if __name__ == "__main__":
    unittest.main()
