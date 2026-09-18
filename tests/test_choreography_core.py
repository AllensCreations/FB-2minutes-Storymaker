import sys
import unittest
from pathlib import Path

# Add src to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from choreography_core import VisualChoreographer
    HAS_CHOREOGRAPHER = True
except ImportError:
    HAS_CHOREOGRAPHER = False

from duration_director import SceneTimeline


@unittest.skipUnless(HAS_CHOREOGRAPHER, "Pillow is required for VisualChoreographer tests (run: pkg install python-pillow or pip install Pillow)")
class TestChoreographyCore(unittest.TestCase):

    def setUp(self):
        self.choreographer = VisualChoreographer(width=1080, height=1920)
        img_path = REPO_ROOT / "assets" / "visuals" / "raw_frames" / "scene_1.png"
        self.scene = SceneTimeline(
            scene_index=0,
            title="Scene 1: Introduction",
            text="In a quiet village nestled between rolling hills, a young baker named Elsa begins her day before sunrise.",
            image_path=str(img_path),
            start_time=0.0,
            end_time=3.5,
            duration=3.5,
            transition_in="spring_pop"
        )

    def test_motion_transform(self):
        # Test entrance pop
        scale_early, _, _ = self.choreographer.compute_motion_transform(self.scene, scene_t=0.05)
        scale_mid, _, _ = self.choreographer.compute_motion_transform(self.scene, scene_t=1.5)

        self.assertGreater(scale_mid, 1.0)  # Slow intentional push zoom
        self.assertNotEqual(scale_early, scale_mid)

    def test_render_frame_dimensions(self):
        frame = self.choreographer.render_frame(self.scene, scene_t=1.0, total_t=1.0, total_duration=21.0)
        self.assertEqual(frame.size, (1080, 1920))
        self.assertEqual(frame.mode, "RGB")

    def test_render_frame_caption_toggle(self):
        frame_with_captions = self.choreographer.render_frame(
            self.scene, scene_t=1.0, total_t=1.0, total_duration=21.0, show_captions=True
        )
        frame_without_captions = self.choreographer.render_frame(
            self.scene, scene_t=1.0, total_t=1.0, total_duration=21.0, show_captions=False
        )

        self.assertEqual(frame_with_captions.size, (1080, 1920))
        self.assertEqual(frame_without_captions.size, (1080, 1920))

        # Pixel data in caption area (around center, lower third y=1680) should differ
        crop_with = frame_with_captions.crop((440, 1650, 640, 1720)).tobytes()
        crop_without = frame_without_captions.crop((440, 1650, 640, 1720)).tobytes()
        self.assertNotEqual(crop_with, crop_without, "Frame with captions should differ from frame without captions in the caption area.")


if __name__ == "__main__":
    unittest.main()
