import sys
import unittest
from pathlib import Path

# Add src to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from choreography_core import VisualChoreographer
from duration_director import SceneTimeline


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


if __name__ == "__main__":
    unittest.main()
