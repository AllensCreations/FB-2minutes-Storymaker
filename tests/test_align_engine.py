import sys
import unittest
from pathlib import Path

# Add src to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from align_engine import AlignmentResult, SpeechCueAlignEngine, SpeechSegment


class TestAlignEngine(unittest.TestCase):

    def setUp(self):
        self.engine = SpeechCueAlignEngine()
        self.script_path = REPO_ROOT / "assets" / "scripts" / "story.txt"
        self.audio_path = REPO_ROOT / "assets" / "voice-over" / "narration.mp3"

    def test_parse_script(self):
        scenes = self.engine.parse_script(self.script_path)
        self.assertEqual(len(scenes), 6)
        self.assertTrue(scenes[0][0].startswith("Scene 1"))
        self.assertIn("Elsa", scenes[0][1])

    def test_audio_duration(self):
        duration = self.engine.get_audio_duration(self.audio_path)
        self.assertGreater(duration, 0)
        self.assertAlmostEqual(duration, 21.0, delta=1.0)

    def test_align_speech_with_script(self):
        result = self.engine.align_speech_with_script(self.audio_path, self.script_path)
        self.assertIsInstance(result, AlignmentResult)
        self.assertEqual(len(result.segments), 6)
        self.assertEqual(result.segments[0].start_time, 0.0)
        self.assertAlmostEqual(result.segments[-1].end_time, result.total_duration, delta=0.5)


if __name__ == "__main__":
    unittest.main()
