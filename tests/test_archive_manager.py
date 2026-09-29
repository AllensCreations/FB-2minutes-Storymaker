"""
Unit tests for ArchiveManager (Local Offline Server Video Archive).
"""

import shutil
import tempfile
import unittest
from pathlib import Path

import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from archive_manager import ArchiveManager


class TestArchiveManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ArchiveManager(output_dir=Path(self.temp_dir))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_list_video(self):
        video_data = b"MOCK_MP4_VIDEO_BYTES_123"
        record = self.manager.save_video(
            video_bytes=video_data,
            filename="my-story.mp4",
            title="My Amazing Story",
            caption="Check out this animation!",
            description="#shorts #story"
        )

        self.assertEqual(record["filename"], "my-story.mp4")
        self.assertEqual(record["title"], "My Amazing Story")
        self.assertEqual(record["uploaded"], "NO")

        items = self.manager.list_archive()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["filename"], "my-story.mp4")

    def test_mark_status(self):
        self.manager.save_video(b"DATA", filename="v1.mp4")
        res_fb = self.manager.mark_status(1, "facebook", "YES")
        self.assertTrue(res_fb)

        res_yt = self.manager.mark_status(1, "youtube", "YES")
        self.assertTrue(res_yt)

        items = self.manager.list_archive()
        self.assertEqual(items[0]["uploaded"], "YES")
        self.assertEqual(items[0]["youtube"], "YES")


if __name__ == "__main__":
    unittest.main()
