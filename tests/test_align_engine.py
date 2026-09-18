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

    def test_parse_json_script(self):
        # JSON Array format
        json_array = '[{"scene": 1, "text": "First scene narration."}, {"scene": 2, "text": "Second scene narration."}]'
        scenes = self.engine.parse_script_content(json_array)
        self.assertEqual(len(scenes), 2)
        self.assertEqual(scenes[0][1], "First scene narration.")
        self.assertEqual(scenes[1][1], "Second scene narration.")

        # Key-Value format
        json_obj = '{"Scene 1": "Opening beat", "Scene 2": "Rising action"}'
        scenes2 = self.engine.parse_script_content(json_obj)
        self.assertEqual(len(scenes2), 2)
        self.assertEqual(scenes2[0][1], "Opening beat")

    def test_parse_next_image_script(self):
        content = (
            "In a sunny grove, little Leo found a golden map.\n"
            "(Next image)\n"
            "The map pointed toward the Crystal Cave.\n"
            "(Next image)\n"
            "Inside the cave, thousands of emerald crystals sparkled."
        )
        scenes = self.engine.parse_script_content(content)
        self.assertEqual(len(scenes), 3)
        self.assertEqual(scenes[0][1], "In a sunny grove, little Leo found a golden map.")
        self.assertEqual(scenes[1][1], "The map pointed toward the Crystal Cave.")
        self.assertEqual(scenes[2][1], "Inside the cave, thousands of emerald crystals sparkled.")

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
