import sys
import unittest
from pathlib import Path

# Add src to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from align_engine import SpeechCueAlignEngine
from duration_director import MasterTimeline, SceneDurationDirector


class TestDurationDirector(unittest.TestCase):

    def setUp(self):
        self.aligner = SpeechCueAlignEngine()
        self.director = SceneDurationDirector()
        self.script_path = REPO_ROOT / "assets" / "scripts" / "story.txt"
        self.audio_path = REPO_ROOT / "assets" / "voice-over" / "narration.mp3"
        self.visuals_path = REPO_ROOT / "assets" / "visuals" / "story_visuals.zip"

    def test_build_timeline(self):
        alignment = self.aligner.align_speech_with_script(self.audio_path, self.script_path)
        timeline = self.director.build_timeline(alignment, self.visuals_path, fps=24)

        self.assertIsInstance(timeline, MasterTimeline)
        self.assertEqual(len(timeline.scenes), 6)
        self.assertEqual(timeline.fps, 24)
        self.assertEqual(timeline.width, 1080)
        self.assertEqual(timeline.height, 1920)

        # Check scene durations
        for scene in timeline.scenes:
            self.assertGreater(scene.duration, 0)
            self.assertEqual(round(scene.end_time - scene.start_time, 2), scene.duration)
            self.assertTrue(Path(scene.image_path).exists())


if __name__ == "__main__":
    unittest.main()
