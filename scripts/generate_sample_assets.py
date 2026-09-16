#!/usr/bin/env python3
"""
Sample Asset Generator for FB 2minutes Storymaker
Creates complete, realistic sample assets for local testing:
- 6 themed scene illustration cards (Pillow)
- Visuals zip bundle (assets/visuals/story_visuals.zip)
- Story narration audio (synthesized tones & melodic voice-over track)
- Scene script (assets/scripts/story.txt)
"""

import math
import os
import struct
import subprocess
import wave
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets"
SCRIPTS_DIR = ASSETS_DIR / "scripts"
VOICE_DIR = ASSETS_DIR / "voice-over"
VISUALS_DIR = ASSETS_DIR / "visuals"
OUTPUT_DIR = ASSETS_DIR / "output"
PROCESSED_DIR = ASSETS_DIR / "processed"


SCENES = [
    {
        "num": 1,
        "title": "Scene 1: Introduction",
        "script": "In a quiet village nestled between rolling hills, a young baker named Elsa begins her day before sunrise.",
        "bg_top": (255, 238, 217),
        "bg_bot": (245, 198, 165),
        "card_color": (255, 252, 245),
        "accent": (212, 107, 60),
        "symbol": "🥐",
        "tag": "DAWN AT THE BAKERY",
    },
    {
        "num": 2,
        "title": "Scene 2: The Problem",
        "script": "But today, the magical yeast that makes her bread rise has gone missing from her pantry.",
        "bg_top": (230, 235, 245),
        "bg_bot": (180, 195, 220),
        "card_color": (250, 252, 255),
        "accent": (70, 95, 150),
        "symbol": "✨",
        "tag": "EMPTY PANTRY JAR",
    },
    {
        "num": 3,
        "title": "Scene 3: The Journey",
        "script": "Elsa must venture into the Enchanted Forest to find the legendary Golden Yeast.",
        "bg_top": (215, 235, 220),
        "bg_bot": (145, 190, 160),
        "card_color": (248, 255, 250),
        "accent": (45, 120, 80),
        "symbol": "🌲",
        "tag": "THE ENCHANTED FOREST",
    },
    {
        "num": 4,
        "title": "Scene 4: The Discovery",
        "script": "Deep in the forest, she discovers the yeast guarded by a friendly forest spirit.",
        "bg_top": (245, 225, 245),
        "bg_bot": (195, 160, 210),
        "card_color": (254, 250, 255),
        "accent": (140, 60, 150),
        "symbol": "🦌",
        "tag": "THE FOREST SPIRIT",
    },
    {
        "num": 5,
        "title": "Scene 5: The Return",
        "script": "With the Golden Yeast restored, Elsa bakes the most magnificent bread the village has ever seen.",
        "bg_top": (255, 240, 205),
        "bg_bot": (240, 195, 110),
        "card_color": (255, 253, 245),
        "accent": (190, 115, 20),
        "symbol": "🍞",
        "tag": "THE GOLDEN LOAF",
    },
    {
        "num": 6,
        "title": "Scene 6: Celebration",
        "script": "The village celebrates with a feast, and Elsa's fame as the finest baker spreads throughout the land.",
        "bg_top": (255, 228, 225),
        "bg_bot": (235, 160, 165),
        "card_color": (255, 250, 250),
        "accent": (195, 60, 80),
        "symbol": "🎉",
        "tag": "FEAST & CELEBRATION",
    },
]


def create_gradient(draw, width, height, top_color, bot_color):
    """Draw vertical linear gradient."""
    for y in range(height):
        ratio = y / max(height - 1, 1)
        r = int(top_color[0] * (1 - ratio) + bot_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bot_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bot_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def generate_scene_image(scene_info: dict, out_path: Path):
    """Generate a high-resolution 1080x1080 scene illustration card."""
    width, height = 1080, 1080
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient
    create_gradient(draw, width, height, scene_info["bg_top"], scene_info["bg_bot"])

    # Draw decorative circular vignette in background
    accent = scene_info["accent"]
    for radius, alpha_step in [(420, 20), (360, 30), (300, 45)]:
        cx, cy = width // 2, height // 2 - 20
        bbox = [cx - radius, cy - radius, cx + radius, cy + radius]
        draw.ellipse(bbox, outline=(accent[0], accent[1], accent[2]), width=2)

    # Storybook decorative framed panel
    margin = 80
    panel_box = [margin, margin, width - margin, height - margin]
    draw.rounded_rectangle(panel_box, radius=40, fill=scene_info["card_color"], outline=accent, width=5)

    # Inner thin border
    inner_m = margin + 18
    draw.rounded_rectangle([inner_m, inner_m, width - inner_m, height - inner_m], radius=28, outline=(accent[0], accent[1], accent[2]), width=2)

    # Corner florets / accents
    corner_size = 24
    for cx, cy in [(inner_m + 20, inner_m + 20), (width - inner_m - 20, inner_m + 20),
                   (inner_m + 20, height - inner_m - 20), (width - inner_m - 20, height - inner_m - 20)]:
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=accent)

    # Tag Badge
    tag = scene_info["tag"]
    draw.rounded_rectangle([width // 2 - 190, margin + 45, width // 2 + 190, margin + 95], radius=25, fill=accent)
    draw.text((width // 2, margin + 70), tag, fill=(255, 255, 255), anchor="mm")

    # Center Illustration / Symbol Artwork
    center_y = height // 2 - 40
    # Central artistic circle
    draw.ellipse([width // 2 - 170, center_y - 170, width // 2 + 170, center_y + 170],
                 fill=(255, 255, 255), outline=accent, width=4)
    # Symbol text
    draw.text((width // 2, center_y), scene_info["symbol"], fill=accent, anchor="mm")

    # Scene Title
    draw.text((width // 2, height - margin - 220), scene_info["title"], fill=accent, anchor="mm")

    # Script excerpt snippet on card
    script_text = scene_info["script"]
    words = script_text.split()
    lines = []
    cur = []
    for w in words:
        cur.append(w)
        if len(" ".join(cur)) > 42:
            lines.append(" ".join(cur[:-1]))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))

    text_y = height - margin - 150
    for line in lines[:3]:
        draw.text((width // 2, text_y), line, fill=(60, 60, 65), anchor="mm")
        text_y += 36

    img.save(out_path, format="PNG", quality=95)


def generate_audio_voiceover(out_mp3_path: Path, scene_duration_sec: float = 3.5):
    """
    Synthesizes a pleasant multi-tone chime & narration track matching the 6 scenes.
    Uses Python wave module and FFmpeg to output clean MP3 audio.
    Total duration: ~21 seconds (3.5s per scene).
    """
    total_scenes = len(SCENES)
    total_duration = total_scenes * scene_duration_sec
    sample_rate = 44100
    total_samples = int(total_duration * sample_rate)

    wav_temp = out_mp3_path.with_suffix(".wav")

    # Pentatonic base frequencies for peaceful storybook chimes (C4, D4, E4, G4, A4, C5)
    scene_base_freqs = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25]

    with wave.open(str(wav_temp), "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        raw_data = bytearray()
        samples_per_scene = int(scene_duration_sec * sample_rate)

        for s_idx in range(total_scenes):
            base_f = scene_base_freqs[s_idx % len(scene_base_freqs)]
            harmonics = [
                (base_f, 0.45),
                (base_f * 2, 0.25),
                (base_f * 3, 0.12),
                (base_f * 1.5, 0.18),
            ]

            for i in range(samples_per_scene):
                t = i / sample_rate
                # Envelope: attack over 0.15s, gentle sustain, soft decay near end of scene
                attack = min(1.0, t / 0.15)
                decay = max(0.0, 1.0 - (t / scene_duration_sec) ** 1.8)
                # Gentle warm breathing vibrato (3 Hz)
                vibrato = 1.0 + 0.015 * math.sin(2 * math.pi * 3.0 * t)

                sample_val = 0.0
                for freq, amp in harmonics:
                    sample_val += amp * math.sin(2 * math.pi * (freq * vibrato) * t)

                # Add soft narrative breath/rhythm pulse (simulating speech cadence at 1.8 Hz)
                speech_cadence = 0.85 + 0.15 * math.sin(2 * math.pi * 1.8 * t)
                final_val = sample_val * attack * decay * speech_cadence

                # Clip and pack 16-bit signed integer
                int_val = int(max(-32767, min(32767, final_val * 24000)))
                raw_data.extend(struct.pack("<h", int_val))

        wav_file.writeframes(raw_data)

    # Convert WAV to MP3 using ffmpeg
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(wav_temp),
                "-b:a", "192k",
                str(out_mp3_path)
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        wav_temp.unlink(missing_ok=True)
    except Exception:
        # If ffmpeg fails, keep WAV or rename
        if wav_temp.exists():
            wav_temp.replace(out_mp3_path.with_suffix(".wav"))


def generate_all_sample_assets():
    """Generates all sample assets in their respective directories."""
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    VISUALS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print("🎨 Generating Sample Assets for FB-2minutes-Storymaker")
    print("==================================================")

    # 1. Generate story.txt
    story_path = SCRIPTS_DIR / "story.txt"
    with open(story_path, "w", encoding="utf-8") as f:
        for s in SCENES:
            f.write(f"[{s['title']}]\n")
            f.write(f"{s['script']}\n\n")
    print(f"✓ Story script created: {story_path}")

    # 2. Generate Scene Images & Visuals Zip
    temp_img_dir = VISUALS_DIR / "raw_frames"
    temp_img_dir.mkdir(exist_ok=True)
    zip_path = VISUALS_DIR / "story_visuals.zip"

    with zipfile.ZipFile(zip_path, "w") as zf:
        for s in SCENES:
            img_filename = f"scene_{s['num']}.png"
            img_path = temp_img_dir / img_filename
            generate_scene_image(s, img_path)
            zf.write(img_path, arcname=img_filename)
            print(f"  • Generated {img_filename} ({s['title']})")

    print(f"✓ Visuals archive packaged: {zip_path}")

    # 3. Generate Narration Audio
    mp3_path = VOICE_DIR / "narration.mp3"
    print("✓ Generating melodic narration audio track (~21s)...")
    generate_audio_voiceover(mp3_path, scene_duration_sec=3.5)
    print(f"✓ Narration audio saved: {mp3_path}")

    print("\n🎉 Sample assets successfully generated and ready to run!\n")


if __name__ == "__main__":
    generate_all_sample_assets()
