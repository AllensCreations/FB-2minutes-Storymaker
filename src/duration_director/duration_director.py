"""
Scene Duration Director for FB 2minutes Storymaker
Maps Scene[N] -> Img[N], allocates start/end times, and prepares timeline manifest.
"""

import json
import re
import zipfile
from dataclasses import asdict, dataclass
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Add src to sys.path for direct script execution
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from align_engine import AlignmentResult, SpeechSegment


@dataclass
class SceneTimeline:
    """Represents a scheduled scene in the master video timeline."""
    scene_index: int
    title: str
    text: str
    image_path: str
    start_time: float
    end_time: float
    duration: float
    transition_in: str = "spring_pop"  # spring_pop | cross_dissolve | cut
    transition_duration: float = 0.3


@dataclass
class MasterTimeline:
    """Complete master timeline manifest."""
    total_duration: float
    scenes: List[SceneTimeline]
    fps: int = 24
    width: int = 1080
    height: int = 1920


class SceneDurationDirector:
    """
    Directs scene duration allocation and pairs visual assets with aligned speech cues.
    """

    def __init__(self, extract_dir: Optional[Path] = None):
        self.extract_dir = extract_dir

    def resolve_visual_assets(self, visuals_source: Path) -> List[Path]:
        """
        Locate and order image files from a zip archive or directory.
        Orders by numeric pattern in filenames (e.g. scene_1.png, 1.png).
        """
        if not visuals_source.exists():
            raise FileNotFoundError(f"Visual assets source not found: {visuals_source}")

        target_dir: Path
        if visuals_source.is_file() and visuals_source.suffix.lower() == ".zip":
            if self.extract_dir is None:
                self.extract_dir = visuals_source.parent.parent / "processed" / "extracted_visuals"
            self.extract_dir.mkdir(parents=True, exist_ok=True)

            print(f"[Scene Duration Director] Extracting visuals from {visuals_source.name}...")
            with zipfile.ZipFile(visuals_source, "r") as zf:
                zf.extractall(self.extract_dir)
            target_dir = self.extract_dir
        elif visuals_source.is_dir():
            target_dir = visuals_source
        else:
            raise ValueError(f"Invalid visual assets source: {visuals_source}")

        valid_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
        images = [p for p in target_dir.rglob("*") if p.is_file() and p.suffix.lower() in valid_exts]

        if not images:
            raise FileNotFoundError(f"No image files (.png, .jpg, .webp) found in {visuals_source}")

        # Natural sort helper by extracting numbers
        def sort_key(p: Path):
            numbers = re.findall(r"\d+", p.stem)
            if numbers:
                return (0, int(numbers[0]), p.name)
            return (1, 0, p.name)

        images.sort(key=sort_key)
        print(f"[Scene Duration Director] Located {len(images)} visual asset(s)")
        return images

    def detect_aspect_ratio(self, images: List[Path]) -> Tuple[int, int, str]:
        """
        Detects aspect ratio from input images.
        If images are square (1:1), automatically returns 4:5 dimensions (1080, 1350).
        Otherwise defaults to 9:16 vertical (1080, 1920).
        """
        if not images:
            return 1080, 1920, "9:16"

        try:
            from PIL import Image
            for img_path in images[:3]:  # Check sample of first images
                if img_path.is_file():
                    with Image.open(img_path) as im:
                        w, h = im.size
                        if h > 0:
                            ratio = w / h
                            # If ratio is between 0.85 and 1.15, detect as 1:1 Square -> 4:5
                            if 0.85 <= ratio <= 1.15:
                                return 1080, 1350, "4:5"
        except Exception:
            pass

        return 1080, 1920, "9:16"

    def build_timeline(
        self,
        alignment: AlignmentResult,
        visuals_source: Path,
        fps: int = 24,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> MasterTimeline:
        """
        Builds the MasterTimeline combining speech alignment segments with visual assets.
        Auto-adapts output dimensions: 1:1 square images -> 4:5 (1080x1350), vertical images -> 9:16 (1080x1920).
        """
        print("[Scene Duration Director] Building master story timeline...")
        images = self.resolve_visual_assets(visuals_source)

        if width is None or height is None:
            auto_w, auto_h, ar_name = self.detect_aspect_ratio(images)
            width = width if width is not None else auto_w
            height = height if height is not None else auto_h
            print(f"[Scene Duration Director] Aspect Ratio: {ar_name} ({width}x{height})")

        scenes: List[SceneTimeline] = []
        num_segments = len(alignment.segments)

        for idx, segment in enumerate(alignment.segments):
            # Select matching image; if fewer images than segments, cycle or clamp to last
            img_path = images[idx % len(images)]
            duration = round(segment.end_time - segment.start_time, 2)

            # Alternate transitions between spring_pop and cross_dissolve
            transition = "spring_pop" if idx % 2 == 0 else "cross_dissolve"

            scene_entry = SceneTimeline(
                scene_index=idx,
                title=segment.scene_title or f"Scene {idx + 1}",
                text=segment.text,
                image_path=str(img_path.resolve()),
                start_time=segment.start_time,
                end_time=segment.end_time,
                duration=duration,
                transition_in=transition,
                transition_duration=0.3
            )
            scenes.append(scene_entry)
            print(f"  • Mapped {scene_entry.title}: {segment.start_time}s - {segment.end_time}s -> {img_path.name}")

        timeline = MasterTimeline(
            total_duration=alignment.total_duration,
            scenes=scenes,
            fps=fps,
            width=width,
            height=height
        )
        return timeline

    def export_timeline(self, timeline: MasterTimeline, output_path: Path) -> None:
        """Export timeline manifest to JSON for visual choreographer and exporter."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[Scene Duration Director] Exporting timeline manifest to: {output_path}")

        data = {
            "total_duration": timeline.total_duration,
            "scene_count": len(timeline.scenes),
            "fps": timeline.fps,
            "resolution": {"width": timeline.width, "height": timeline.height},
            "scenes": [asdict(s) for s in timeline.scenes]
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"✓ Master timeline exported: {output_path}")


def main():
    from align_engine import SpeechCueAlignEngine

    audio_path = Path("assets/voice-over/narration.mp3")
    script_path = Path("assets/scripts/story.txt")
    visuals_path = Path("assets/visuals/story_visuals.zip")
    output_path = Path("assets/processed/timeline.json")

    aligner = SpeechCueAlignEngine()
    alignment = aligner.align_speech_with_script(audio_path, script_path)

    director = SceneDurationDirector()
    timeline = director.build_timeline(alignment, visuals_path)
    director.export_timeline(timeline, output_path)
    print("✅ Duration Director test passed.")


if __name__ == "__main__":
    main()
