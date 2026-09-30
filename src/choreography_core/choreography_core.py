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
        """Creates and caches a heavily blurred cover background for ambient glow framing."""
        cache_key = f"blur_{path_str}_{self.width}_{self.height}"
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        src = self.get_source_image(path_str)
        # Downscale for ultra-fast blur on mobile/Termux
        small_w = 360
        small_h = int(360 * (self.height / self.width))
        h_r = small_w / src.width
        v_r = small_h / src.height
        cov_r = max(h_r, v_r)

        scaled = src.resize((int(src.width * cov_r), int(src.height * cov_r)), Image.Resampling.BILINEAR)
        left = (scaled.width - small_w) // 2
        top = (scaled.height - small_h) // 2
        cropped = scaled.crop((left, top, left + small_w, top + small_h)).convert("RGBA")

        # Apply blur and darken overlay for ambient glow
        blurred = cropped.filter(ImageFilter.BoxBlur(18))
        dark_overlay = Image.new("RGBA", (small_w, small_h), (0, 0, 0, 110))
        blurred.paste(dark_overlay, (0, 0), dark_overlay)

        # Scale up to full canvas dimensions
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
        Computes (scale, offset_x, offset_y) for subtle micro-motion push-in.
        Scale: 1.00 -> 1.03 with smoothstep easing, centered so the artwork stays
        crisp and within margins without horizontal overflow/crop.
        """
        duration = max(scene.duration, 0.1)
        progress = max(0.0, scene_t / duration)
        p = min(progress, 1.15)
        if p <= 1.0:
            eased = p * p * (3.0 - 2.0 * p)
        else:
            eased = 1.0 + (p - 1.0) * 0.2
        scale = 1.0 + (0.03 * eased)
        offset_x = 0.0
        offset_y = 0.0
        return scale, offset_x, offset_y

    def _get_vignette_overlay(self) -> Image.Image:
        """Creates and caches a subtle top/bottom ambient vignette overlay matching browser canvas."""
        if hasattr(self, "_vignette_overlay") and self._vignette_overlay is not None:
            return self._vignette_overlay

        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        h = self.height
        p20 = int(h * 0.20)
        p80 = int(h * 0.80)

        # Top gradient: 0% -> alpha 153 (0.60), 20% -> alpha 38 (0.15)
        for y in range(p20):
            ratio = y / max(p20, 1)
            alpha = int(153 * (1.0 - ratio) + 38 * ratio)
            draw.line([(0, y), (self.width, y)], fill=(0, 0, 0, alpha))

        # Middle: 20% to 80% -> alpha 38 (0.15)
        draw.rectangle([0, p20, self.width, p80], fill=(0, 0, 0, 38))

        # Bottom gradient: 80% -> alpha 38 (0.15), 100% -> alpha 166 (0.65)
        for y in range(p80, h):
            ratio = (y - p80) / max(h - p80, 1)
            alpha = int(38 * (1.0 - ratio) + 166 * ratio)
            draw.line([(0, y), (self.width, y)], fill=(0, 0, 0, alpha))

        self._vignette_overlay = img
        return self._vignette_overlay

    def _draw_drop_shadow(self, base_img: Image.Image, x: int, y: int, w: int, h: int, radius: int = 16, offset_y: int = 4) -> None:
        """Applies a fast bounded drop shadow behind the centered artwork."""
        pad = radius * 2
        bx = max(0, x - pad)
        by = max(0, y + offset_y - pad)
        bw = min(self.width - bx, w + pad * 2)
        bh = min(self.height - by, h + pad * 2)
        if bw <= 0 or bh <= 0:
            return

        shadow_box = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow_box)
        rx0 = x - bx
        ry0 = (y + offset_y) - by
        sdraw.rectangle([rx0, ry0, rx0 + w, ry0 + h], fill=(0, 0, 0, 160))
        blurred = shadow_box.filter(ImageFilter.BoxBlur(radius // 2))
        base_img.paste(blurred, (bx, by), blurred)

    def _render_scene_image(
        self,
        scene: SceneTimeline,
        scale: float,
        offset_x: float = 0.0,
        offset_y: float = 0.0
    ) -> Image.Image:
        """
        Renders the scene artwork auto-fitting the canvas width with ambient glow background,
        cinematic vignette gradient, and soft drop shadow. Does NOT crop horizontally.
        """
        src_img = self.get_source_image(scene.image_path)
        fit_ratio = (self.width / src_img.width) * scale
        scaled_w = int(src_img.width * fit_ratio)
        scaled_h = int(src_img.height * fit_ratio)
        scaled_img = src_img.resize((scaled_w, scaled_h), Image.Resampling.BILINEAR)

        # 1. Ambient glow background sampled from the scene image
        bg = self.get_blurred_background(scene.image_path).copy().convert("RGBA")

        # 2. Subtle Vignette gradient top/bottom
        vignette = self._get_vignette_overlay()
        bg.paste(vignette, (0, 0), vignette)

        # 3. Centered Width-Fitted Image with soft drop shadow
        final_x = int((self.width - scaled_w) // 2 + offset_x)
        final_y = int((self.height - scaled_h) // 2 + offset_y)
        self._draw_drop_shadow(bg, final_x, final_y, scaled_w, scaled_h, radius=16, offset_y=4)

        if scaled_img.mode == "RGBA":
            bg.paste(scaled_img, (final_x, final_y), scaled_img)
        else:
            bg.paste(scaled_img, (final_x, final_y))
        return bg.convert("RGB")

    CAPTION_PRESETS = {
        "gold": {
            "font_color": (255, 230, 0),       # #FFE600 Bold Hormozi Yellow
            "stroke_color": (0, 0, 0),
            "stroke_width": 8,
            "shadow_color": (0, 0, 0, 230),
            "font_size": 52
        },
        "mint": {
            "font_color": (0, 255, 157),       # #00FF9D Cyber Neon Mint
            "stroke_color": (0, 0, 0),
            "stroke_width": 8,
            "shadow_color": (0, 0, 0, 230),
            "font_size": 52
        },
        "cyan": {
            "font_color": (0, 229, 255),       # #00E5FF Electric Ice Cyan
            "stroke_color": (0, 0, 0),
            "stroke_width": 8,
            "shadow_color": (0, 0, 0, 230),
            "font_size": 52
        },
        "white": {
            "font_color": (255, 255, 255),     # Classic White
            "stroke_color": (0, 0, 0),
            "stroke_width": 7,
            "shadow_color": (0, 0, 0, 230),
            "font_size": 50
        }
    }

    @staticmethod
    def get_timed_caption_chunk(text: str, scene_t: float, duration: float, words_per_chunk: int = 7) -> str:
        """
        Legacy phrase chunking for backwards compatibility (uppercased).
        """
        words = text.strip().split()
        if len(words) <= words_per_chunk:
            return text.strip().upper()

        chunks = []
        for i in range(0, len(words), words_per_chunk):
            chunks.append(" ".join(words[i:i + words_per_chunk]))

        prog = max(0.0, min(scene_t / max(duration, 0.1), 0.999))
        chunk_idx = min(int(prog * len(chunks)), len(chunks) - 1)
        return chunks[chunk_idx].upper()

    @staticmethod
    def get_hormozi_caption_chunk(
        text: str,
        scene_t: float,
        duration: float,
        words_per_chunk: int = 5
    ) -> Tuple[str, float]:
        """
        Splits scene text into 5-10 word caption chunks with character-weighted timing.
        Returns: (active_chunk_text in UPPERCASE, scale_multiplier_for_spring_pop)
        """
        words = [w for w in text.strip().split() if w]
        if not words:
            return "", 1.0

        words_per_chunk = max(5, min(10, int(words_per_chunk)))
        chunks = [
            " ".join(words[i:i + words_per_chunk])
            for i in range(0, len(words), words_per_chunk)
        ]

        # Calculate character-based weights with pause for punctuation
        weights = []
        for ch in chunks:
            w = len(ch)
            if ch.endswith((",", ";", ":")):
                w += 2
            elif ch.endswith((".", "!", "?")):
                w += 4
            weights.append(max(w, 2))

        total_weight = sum(weights)
        dur = max(duration, 0.1)

        # Allocate time ranges
        time_ranges = []
        cur_t = 0.0
        for idx, ch in enumerate(chunks):
            ch_dur = (weights[idx] / total_weight) * dur
            time_ranges.append((ch, cur_t, cur_t + ch_dur))
            cur_t += ch_dur

        # Find active chunk at scene_t
        active_chunk = chunks[-1]
        active_start = time_ranges[-1][1]
        for ch, start_t, end_t in time_ranges:
            if start_t <= scene_t < end_t:
                active_chunk = ch
                active_start = start_t
                break

        # Calculate punchy spring pop animation (1.25x -> 1.0x over first 130ms)
        elapsed = max(0.0, scene_t - active_start)
        pop_duration = 0.13
        if elapsed < pop_duration:
            prog = elapsed / pop_duration
            scale = 1.0 + 0.25 * math.cos(prog * math.pi * 0.5) * (1.0 - prog)
        else:
            scale = 1.0

        return active_chunk.upper(), scale

    def _draw_hormozi_caption(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        scale: float,
        style_key: str = "gold"
    ):
        """Draws 1-2 word punchy caption at lower third (~72% down) with outline & shadow in UPPERCASE."""
        if not text:
            return
        text = str(text).upper()
        style = self.CAPTION_PRESETS.get(style_key, self.CAPTION_PRESETS["gold"])
        font_size = int(style["font_size"] * scale)
        font = self._get_font(font_size)
        while font_size > 24 and draw.textbbox((0, 0), text, font=font)[2] > self.width * 0.9:
            font_size -= 2
            font = self._get_font(font_size)
        x = self.width // 2
        y = int(self.height * 0.72)
        stroke_w = max(2, int(style["stroke_width"] * scale))
        shadow_offset = max(2, int(4 * scale))

        # 1. Soft drop shadow
        draw.text(
            (x + shadow_offset, y + shadow_offset),
            text,
            font=font,
            fill=style["shadow_color"],
            stroke_width=stroke_w + 2,
            stroke_fill=style["shadow_color"],
            anchor="mm"
        )
        # 2. Main stroke and font fill
        draw.text(
            (x, y),
            text,
            font=font,
            fill=style["font_color"],
            stroke_width=stroke_w,
            stroke_fill=style["stroke_color"],
            anchor="mm"
        )

    def render_frame(
        self,
        scene: SceneTimeline,
        scene_t: float,
        total_t: float,
        total_duration: float = 21.0,
        show_captions: bool = True,
        prev_scene: Optional[SceneTimeline] = None,
        transition_duration: float = 0.45,
        caption_style: str = "gold",
        caption_words_per_chunk: int = 5,
        retro_flicker: bool = False
    ) -> Image.Image:
        """
        Renders a single video frame matching HTML5 canvas:
        - Full-bleed edge-to-edge ambient glow backdrop
        - Top/bottom vignette gradient
        - Smooth cinematic cross-dissolve transition between scenes with continuous motion
        - Subtle Ken Burns push-in
        - Timed 5-10 word Hormozi Spring Pop captions directly over lower third (72% down)
        - 6px blue story progress bar at very bottom
        """
        # 1. Render current scene image with Ken Burns push-in & drift
        scale_cur, off_x_cur, off_y_cur = self.compute_motion_transform(scene, scene_t)
        cur_frame = self._render_scene_image(scene, scale_cur, off_x_cur, off_y_cur)

        # 2. Cinematic Cross-Dissolve Transition from previous scene (continuous motion)
        if prev_scene is not None and scene_t < transition_duration:
            prev_dur = max(prev_scene.duration, 0.1)
            scale_prev, off_x_prev, off_y_prev = self.compute_motion_transform(prev_scene, prev_dur + scene_t)
            prev_frame = self._render_scene_image(prev_scene, scale_prev, off_x_prev, off_y_prev)
            blend_alpha = max(0.0, min(scene_t / transition_duration, 1.0))
            frame = Image.blend(prev_frame, cur_frame, blend_alpha)
        else:
            frame = cur_frame

        # 3. 1-2 Word Punchy Spring Pop Caption directly over lower third (72% down)
        if show_captions and scene.text:
            draw = ImageDraw.Draw(frame)
            active_chunk, pop_scale = self.get_hormozi_caption_chunk(
                scene.text, scene_t, scene.duration, caption_words_per_chunk
            )
            self._draw_hormozi_caption(
                draw=draw,
                text=active_chunk,
                scale=pop_scale,
                style_key=caption_style
            )

        # 4. Subtle overall story progress bar at very bottom (matching 6px canvas progress bar)
        draw = ImageDraw.Draw(frame)
        overall_progress = max(0.0, min(1.0, total_t / max(total_duration, 0.1)))
        overall_fill_w = int(self.width * overall_progress)
        if overall_fill_w > 0:
            draw.rectangle([0, self.height - 6, overall_fill_w, self.height], fill=(59, 130, 246))

        if retro_flicker:
            alpha = 0.075 + 0.025 * math.sin(total_t * 2 * math.pi * 8)
            warm_overlay = Image.new("RGB", frame.size, (255, 220, 160))
            frame = Image.blend(frame, warm_overlay, alpha)

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
