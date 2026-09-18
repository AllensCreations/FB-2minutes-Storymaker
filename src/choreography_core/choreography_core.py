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

        # Draw translucent dark pill badge behind text
        if frame is not None and display_lines:
            line_widths = []
            for line in display_lines:
                if font and hasattr(draw, "textlength"):
                    lw = draw.textlength(line, font=font)
                elif font and hasattr(font, "getlength"):
                    lw = font.getlength(line)
                else:
                    lw = len(line) * (font_size * 0.55)
                line_widths.append(lw)

            max_lw = max(line_widths) if line_widths else 200
            pill_w = int(min(max_width + 48, max_lw + 64))
            pill_h = total_h + 36
            pill_left = x - pill_w // 2
            pill_top = y - pill_h // 2
            pill_right = pill_left + pill_w
            pill_bottom = pill_top + pill_h

            pill_overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            p_draw = ImageDraw.Draw(pill_overlay)
            p_draw.rounded_rectangle(
                [pill_left, pill_top, pill_right, pill_bottom],
                radius=24,
                fill=(10, 15, 26, 215),
                outline=(255, 255, 255, 40),
                width=2
            )
            frame.paste(pill_overlay, (0, 0), pill_overlay)
            draw = ImageDraw.Draw(frame)

        cur_y = start_y
        for line in display_lines:
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

    def render_frame(
        self,
        scene: SceneTimeline,
        scene_t: float,
        total_t: float,
        total_duration: float = 21.0,
        show_captions: bool = True
    ) -> Image.Image:
        """
        Renders a single 1080x1920 video frame with:
        - Heavy blurred background of the artwork (TikTok / Reels style)
        - 100% full uncropped image centered in the foreground (contain)
        - Subtle Ken Burns drift
        - Optional TikTok dark pill stroked subtitles
        """
        # 1. Start with blurred cover background
        frame = self.get_blurred_background(scene.image_path).copy()

        # 2. Source artwork with Contain scaling (0% cropped, 100% complete image)
        src_img = self.get_source_image(scene.image_path)
        scale, _, _ = self.compute_motion_transform(scene, scene_t)

        max_fg_w = self.width * 0.94
        max_fg_h = self.height * 0.72
        contain_ratio = min(max_fg_w / src_img.width, max_fg_h / src_img.height) * scale

        fg_w = int(src_img.width * contain_ratio)
        fg_h = int(src_img.height * contain_ratio)

        fg_img = src_img.resize((fg_w, fg_h), Image.Resampling.BICUBIC)

        fg_x = (self.width - fg_w) // 2
        # Position slightly above center to balance lower-third caption
        fg_y = (self.height - fg_h) // 2 - 40

        # Draw subtle soft drop shadow behind foreground image
        shadow_overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow_overlay)
        s_draw.rectangle([fg_x - 8, fg_y - 2, fg_x + fg_w + 8, fg_y + fg_h + 14], fill=(0, 0, 0, 110))
        frame.paste(shadow_overlay, (0, 0), shadow_overlay)

        # Paste full foreground image
        if fg_img.mode == "RGBA":
            frame.paste(fg_img, (fg_x, fg_y), fg_img)
        else:
            frame.paste(fg_img, (fg_x, fg_y))

        # 3. Optional TikTok Captions on lower third
        if show_captions and scene.text:
            draw = ImageDraw.Draw(frame)
            self._draw_text_wrapped(
                draw=draw,
                text=scene.text,
                x=self.width // 2,
                y=self.height - 240,
                max_width=self.width - 140,
                font_color=(255, 255, 255),
                stroke_color=(0, 0, 0),
                stroke_width=6,
                line_height=64,
                frame=frame
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
