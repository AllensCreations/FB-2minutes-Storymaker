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

    def get_blurred_background(self, path_str: str) -> Image.Image:
        """Creates and caches a heavily blurred cover background for TikTok-style vertical framing."""
        cache_key = f"blur_{path_str}"
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        src = self.get_source_image(path_str)
        # Downscale for ultra-fast blur on mobile/Termux
        small_w, small_h = 360, 640
        h_r = small_w / src.width
        v_r = small_h / src.height
        cov_r = max(h_r, v_r)

        scaled = src.resize((int(src.width * cov_r), int(src.height * cov_r)), Image.Resampling.BILINEAR)
        left = (scaled.width - small_w) // 2
        top = (scaled.height - small_h) // 2
        cropped = scaled.crop((left, top, left + small_w, top + small_h)).convert("RGBA")

        # Apply blur and darken overlay
        blurred = cropped.filter(ImageFilter.BoxBlur(18))
        dark_overlay = Image.new("RGBA", (small_w, small_h), (0, 0, 0, 95))
        blurred.paste(dark_overlay, (0, 0), dark_overlay)

        # Scale up to full 1080x1920
        bg_full = blurred.resize((self.width, self.height), Image.Resampling.BICUBIC).convert("RGB")
        self._image_cache[cache_key] = bg_full
        return bg_full

    def _get_font(self, size: int = 50) -> ImageFont.ImageFont:
        """Loads a suitable bold TrueType font for subtitles, with fallbacks."""
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/system/fonts/Roboto-Bold.ttf",
            "/data/data/com.termux/files/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "DejaVuSans-Bold.ttf",
            "Roboto-Bold.ttf",
            "Arial.ttf"
        ]
        for path in candidates:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        try:
            return ImageFont.load_default()
        except Exception:
            return None

    def _draw_text_wrapped(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        x: int,
        y: int,
        max_width: int,
        font_color: Tuple[int, int, int] = (255, 255, 255),
        stroke_color: Tuple[int, int, int] = (0, 0, 0),
        stroke_width: int = 6,
        font_size: int = 48,
        line_height: int = 62,
        frame: Optional[Image.Image] = None
    ) -> int:
        """Draws word-wrapped stroked subtitles inside a TikTok dark pill badge."""
        font = self._get_font(font_size)
        words = text.split()
        lines: List[str] = []
        current: List[str] = []

        for word in words:
            current.append(word)
            test_line = " ".join(current)
            if font and hasattr(draw, "textlength"):
                w = draw.textlength(test_line, font=font)
            elif font and hasattr(font, "getlength"):
                w = font.getlength(test_line)
            else:
                w = len(test_line) * (font_size * 0.55)

            if w > max_width and len(current) > 1:
                lines.append(" ".join(current[:-1]))
                current = [word]

        if current:
            lines.append(" ".join(current))

        display_lines = lines[:3]
        total_h = len(display_lines) * line_height
        start_y = y - (total_h // 2) + (line_height // 2)

        cur_y = start_y
        for line in display_lines:
            # Draw subtle drop shadow
            draw.text(
                (x + 2, cur_y + 2),
                line,
                font=font,
                fill=(0, 0, 0, 180),
                stroke_width=stroke_width + 2,
                stroke_fill=(0, 0, 0, 180),
                anchor="mm"
            )
            # Draw main text with outline
            draw.text(
                (x, cur_y),
                line,
                font=font,
                fill=font_color,
                stroke_width=stroke_width,
                stroke_fill=stroke_color,
                anchor="mm"
            )
            cur_y += line_height

        return cur_y - y

    def compute_motion_transform(
        self,
        scene: SceneTimeline,
        scene_t: float
    ) -> Tuple[float, float, float]:
        """
        Computes (scale, offset_x, offset_y) for subtle Ken Burns zoom-in (1.0 -> 1.05).
        """
        duration = max(scene.duration, 0.1)
        progress = max(0.0, min(scene_t / duration, 1.0))
        scale = 1.0 + (0.05 * progress)
        return scale, 0.0, 0.0

    def _render_scene_image(self, scene: SceneTimeline, scale: float) -> Image.Image:
        """Renders the scene artwork filling the 9:16 vertical frame edge-to-edge (cover)."""
        src_img = self.get_source_image(scene.image_path)
        h_ratio = self.width / src_img.width
        v_ratio = self.height / src_img.height
        cover_ratio = max(h_ratio, v_ratio) * scale

        scaled_w = int(src_img.width * cover_ratio)
        scaled_h = int(src_img.height * cover_ratio)
        scaled_img = src_img.resize((scaled_w, scaled_h), Image.Resampling.BICUBIC)

        center_shift_x = (self.width - scaled_w) // 2
        center_shift_y = (self.height - scaled_h) // 2

        img_frame = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        if scaled_img.mode == "RGBA":
            img_frame.paste(scaled_img, (center_shift_x, center_shift_y), scaled_img)
        else:
            img_frame.paste(scaled_img, (center_shift_x, center_shift_y))
        return img_frame

    def render_frame(
        self,
        scene: SceneTimeline,
        scene_t: float,
        total_t: float,
        total_duration: float = 21.0,
        show_captions: bool = True,
        prev_scene: Optional[SceneTimeline] = None,
        transition_duration: float = 0.45
    ) -> Image.Image:
        """
        Renders a single 1080x1920 video frame with:
        - Full-bleed edge-to-edge image framing (as seen in user screenshot)
        - Smooth cinematic cross-dissolve transition between scenes
        - Subtle Ken Burns drift
        - Floating white caption directly on the video (matching user screenshot)
        """
        # 1. Render current scene image with Ken Burns motion
        scale_cur, _, _ = self.compute_motion_transform(scene, scene_t)
        cur_frame = self._render_scene_image(scene, scale_cur)

        # 2. Cinematic Cross-Dissolve Transition from previous scene
        if prev_scene is not None and scene_t < transition_duration:
            prev_dur = max(prev_scene.duration, 0.1)
            scale_prev, _, _ = self.compute_motion_transform(prev_scene, prev_dur)
            prev_frame = self._render_scene_image(prev_scene, scale_prev)
            blend_alpha = max(0.0, min(scene_t / transition_duration, 1.0))
            frame = Image.blend(prev_frame, cur_frame, blend_alpha)
        else:
            frame = cur_frame

        # 3. Clean floating white caption directly over the lower third (matching screenshot)
        if show_captions and scene.text:
            draw = ImageDraw.Draw(frame)
            self._draw_text_wrapped(
                draw=draw,
                text=scene.text,
                x=self.width // 2,
                y=int(self.height * 0.78),
                max_width=self.width - 160,
                font_color=(255, 255, 255),
                stroke_color=(0, 0, 0),
                stroke_width=4,
                font_size=42,
                line_height=56
            )

        # 4. Subtle overall story progress bar at very bottom
        draw = ImageDraw.Draw(frame)
        overall_progress = max(0.0, min(1.0, total_t / max(total_duration, 0.1)))
        overall_fill_w = int(self.width * overall_progress)
        if overall_fill_w > 0:
            draw.rectangle([0, self.height - 8, overall_fill_w, self.height], fill=(59, 130, 246))

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
