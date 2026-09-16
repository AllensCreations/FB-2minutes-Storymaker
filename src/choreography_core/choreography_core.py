"""
Visual Choreography Core for FB 2minutes Storymaker
Implements "Picture-Book Motion" aesthetics:
- Canvas as a Page (warm editorial parchment & ambient lighting)
- Spring-Pop & Cross-Dissolve entrances
- Subtle Life Micro-Drift (slow intentional push & breathing oscillation)
- Upper-region centered artwork with lower-third typography cards
"""

import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add src to sys.path for direct script execution
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from duration_director import SceneTimeline


class VisualChoreographer:
    """
    Renders video frames applying Picture-Book Motion choreographic rules.
    """

    def __init__(self, width: int = 1080, height: int = 1920):
        self.width = width
        self.height = height
        self._image_cache: Dict[str, Image.Image] = {}

    def get_source_image(self, path_str: str) -> Image.Image:
        """Loads and caches source artwork in RGBA format."""
        if path_str not in self._image_cache:
            img = Image.open(path_str).convert("RGBA")
            self._image_cache[path_str] = img
        return self._image_cache[path_str]

    def _draw_text_wrapped(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        x: int,
        y: int,
        max_width: int,
        font_color: Tuple[int, int, int],
        line_height: int = 42
    ) -> int:
        """Draws word-wrapped text, centered at x, and returns total height."""
        words = text.split()
        lines: List[str] = []
        current: List[str] = []

        # Approximate character width based on average font spacing
        char_limit = max_width // 13

        for word in words:
            current.append(word)
            if len(" ".join(current)) > char_limit:
                lines.append(" ".join(current[:-1]))
                current = [word]
        if current:
            lines.append(" ".join(current))

        cur_y = y
        for line in lines[:4]:  # Limit to 4 lines for clean lower-third layout
            draw.text((x, cur_y), line, fill=font_color, anchor="mm")
            cur_y += line_height

        return cur_y - y

    def compute_motion_transform(
        self,
        scene: SceneTimeline,
        scene_t: float
    ) -> Tuple[float, float, float]:
        """
        Computes (scale, offset_x, offset_y) for Picture-Book Motion.
        Includes Spring Pop entrance and Slow Intentional Push micro-drift.
        """
        duration = max(scene.duration, 0.1)
        t_clamped = max(0.0, min(scene_t, duration))

        # 1. Entrance Pop: first 0.35s
        entrance_scale = 1.0
        if scene.transition_in == "spring_pop" and t_clamped < 0.4:
            norm_t = t_clamped / 0.4
            # Damped spring equation: starts at 0.90, peaks at ~1.02, settles to 1.0
            entrance_scale = 1.0 - 0.10 * math.exp(-5.0 * norm_t) * math.cos(math.pi * 3.5 * norm_t)

        # 2. Slow Intentional Push (3-4% zoom over the full scene)
        push_progress = t_clamped / duration
        push_scale = 1.0 + (0.04 * push_progress)

        final_scale = entrance_scale * push_scale

        # 3. Breathing Drift (1-2px vertical harmonic oscillation at 0.75 Hz)
        oscillation_y = 2.5 * math.sin(2.0 * math.pi * 0.75 * t_clamped)

        return final_scale, 0.0, oscillation_y

    def render_frame(
        self,
        scene: SceneTimeline,
        scene_t: float,
        total_t: float,
        total_duration: float = 21.0
    ) -> Image.Image:
        """
        Renders a single 1080x1920 video frame for the given scene and timestamp.
        """
        # Canvas initialization: Editorial warm parchment page
        frame = Image.new("RGB", (self.width, self.height), (248, 245, 238))
        draw = ImageDraw.Draw(frame)

        # 1. Subtle top and bottom page vignette
        for y_step in range(0, 160, 4):
            alpha = int(25 * (1.0 - (y_step / 160)))
            draw.line([(0, y_step), (self.width, y_step)], fill=(240 - alpha // 3, 236 - alpha // 3, 228 - alpha // 3))

        # 2. Top Header Brand Pill & Divider
        badge_y = 90
        draw.rounded_rectangle(
            [self.width // 2 - 170, badge_y - 24, self.width // 2 + 170, badge_y + 24],
            radius=18,
            fill=(235, 230, 220),
            outline=(210, 202, 190),
            width=2
        )
        draw.text(
            (self.width // 2, badge_y),
            "PICTURE-BOOK MOTION",
            fill=(100, 95, 90),
            anchor="mm"
        )

        # 3. Center Artwork Card with Motion
        src_img = self.get_source_image(scene.image_path)
        base_size = 860
        scale, offset_x, offset_y = self.compute_motion_transform(scene, scene_t)

        current_size = int(base_size * scale)
        # Resize artwork
        scaled_img = src_img.resize((current_size, current_size), Image.Resampling.BICUBIC)

        # Calculate placement (Upper Center region: centered horizontally, y ~ 620)
        center_target_x = self.width // 2 + int(offset_x)
        center_target_y = 660 + int(offset_y)

        box_left = center_target_x - current_size // 2
        box_top = center_target_y - current_size // 2

        # Soft shadow behind artwork card
        shadow_margin = 16
        shadow_box = [
            self.width // 2 - base_size // 2 + 6,
            660 - base_size // 2 + 12,
            self.width // 2 + base_size // 2 + 6,
            660 + base_size // 2 + 12
        ]
        draw.rounded_rectangle(shadow_box, radius=32, fill=(215, 210, 200))

        # Paste artwork onto canvas with alpha composite
        frame.paste(scaled_img, (box_left, box_top), scaled_img if scaled_img.mode == "RGBA" else None)

        # Outer decorative frame border around base artwork
        frame_box = [
            self.width // 2 - base_size // 2 - 4,
            660 - base_size // 2 - 4,
            self.width // 2 + base_size // 2 + 4,
            660 + base_size // 2 + 4
        ]
        draw.rounded_rectangle(frame_box, radius=32, outline=(220, 212, 198), width=4)

        # 4. Lower-Third Caption Card (y = 1200 to 1750)
        card_margin = 80
        card_top = 1180
        card_bottom = 1760
        card_rect = [card_margin, card_top, self.width - card_margin, card_bottom]

        # Dark aesthetic slate card
        draw.rounded_rectangle(card_rect, radius=40, fill=(32, 34, 42), outline=(50, 54, 66), width=3)

        # Inner decorative highlight line
        draw.line([card_margin + 40, card_top + 3, self.width - card_margin - 40, card_top + 3], fill=(70, 75, 90), width=2)

        # Scene index badge
        badge_rect = [self.width // 2 - 130, card_top + 50, self.width // 2 + 130, card_top + 96]
        draw.rounded_rectangle(badge_rect, radius=20, fill=(235, 140, 60))
        scene_badge_text = f"SCENE {scene.scene_index + 1}"
        draw.text((self.width // 2, card_top + 73), scene_badge_text, fill=(255, 255, 255), anchor="mm")

        # Scene title
        draw.text((self.width // 2, card_top + 145), scene.title, fill=(245, 245, 250), anchor="mm")

        # Subtitle / narration script text
        self._draw_text_wrapped(
            draw=draw,
            text=scene.text,
            x=self.width // 2,
            y=card_top + 230,
            max_width=self.width - (card_margin * 2) - 80,
            font_color=(220, 222, 230),
            line_height=46
        )

        # Scene progress indicator bar inside caption card
        bar_w = self.width - (card_margin * 2) - 160
        bar_left = (self.width - bar_w) // 2
        bar_y = card_bottom - 70
        bar_h = 8
        draw.rounded_rectangle([bar_left, bar_y, bar_left + bar_w, bar_y + bar_h], radius=4, fill=(60, 64, 76))

        scene_progress = max(0.0, min(1.0, scene_t / max(scene.duration, 0.1)))
        progress_fill_w = int(bar_w * scene_progress)
        if progress_fill_w > 4:
            draw.rounded_rectangle([bar_left, bar_y, bar_left + progress_fill_w, bar_y + bar_h], radius=4, fill=(235, 140, 60))

        # Overall Story Progress at very bottom of screen
        overall_progress = max(0.0, min(1.0, total_t / max(total_duration, 0.1)))
        overall_fill_w = int(self.width * overall_progress)
        if overall_fill_w > 0:
            draw.rectangle([0, self.height - 10, overall_fill_w, self.height], fill=(212, 107, 60))

        return frame


def main():
    from duration_director import SceneTimeline

    scene = SceneTimeline(
        scene_index=0,
        title="Scene 1: Introduction",
        text="In a quiet village nestled between rolling hills, a young baker named Elsa begins her day before sunrise.",
        image_path="assets/visuals/raw_frames/scene_1.png",
        start_time=0.0,
        end_time=4.0,
        duration=4.0
    )

    choreographer = VisualChoreographer()
    test_frame = choreographer.render_frame(scene, scene_t=1.2, total_t=1.2, total_duration=21.0)
    out_dir = Path("assets/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_preview = out_dir / "test_frame_preview.png"
    test_frame.save(out_preview)
    print(f"✅ Rendered test frame: {out_preview}")


if __name__ == "__main__":
    main()
