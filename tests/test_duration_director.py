import sys
import io
import json
import tempfile
import unittest
import wave
import zipfile
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
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        self.script_path = root / "story.txt"
        self.script_path.write_text(
            "\n".join(f"[Scene {i}: Test]\nScene {i} narration." for i in range(1, 7)),
            encoding="utf-8",
        )
        self.audio_path = root / "narration.wav"
        with wave.open(str(self.audio_path), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(8000)
            audio.writeframes(b"\0\0" * 8000 * 21)

        from PIL import Image
        self.visuals_path = root / "visuals.zip"
        with zipfile.ZipFile(self.visuals_path, "w") as archive:
            for index in range(1, 7):
                image = Image.new("RGB", (64, 64), (index * 20, 80, 120))
                image_bytes = io.BytesIO()
                image.save(image_bytes, format="PNG")
                archive.writestr(f"scene_{index}.png", image_bytes.getvalue())

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_build_timeline(self):
        alignment = self.aligner.align_speech_with_script(self.audio_path, self.script_path)
        # 1. Auto-detected 4:5 ratio for 1:1 square images
        timeline = self.director.build_timeline(alignment, self.visuals_path, fps=24)

        self.assertIsInstance(timeline, MasterTimeline)
        self.assertEqual(len(timeline.scenes), 6)
        self.assertEqual(timeline.fps, 24)
        self.assertEqual(timeline.width, 1080)
        self.assertEqual(timeline.height, 1350)  # Auto-detected 4:5 for 1:1 images

        # Check scene durations
        for scene in timeline.scenes:
            self.assertGreater(scene.duration, 0)
            self.assertEqual(round(scene.end_time - scene.start_time, 2), scene.duration)
            self.assertTrue(Path(scene.image_path).exists())

        # 2. Explicit dimensions override
        forced_timeline = self.director.build_timeline(alignment, self.visuals_path, fps=24, width=1080, height=1920)
        self.assertEqual(forced_timeline.width, 1080)
        self.assertEqual(forced_timeline.height, 1920)


if __name__ == "__main__":
    unittest.main()
