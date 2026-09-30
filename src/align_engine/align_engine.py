"""
Speech-Cue Align Engine for FB 2minutes Storymaker
Implements audio analysis and script alignment for Picture-Book Motion storytelling.
"""

import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class SpeechSegment:
    """Represents a segment of speech with timing information."""
    start_time: float  # Start time in seconds
    end_time: float    # End time in seconds
    text: str          # The spoken text for this segment
    scene_title: str = ""
    confidence: float = 0.95


@dataclass
class AlignmentResult:
    """Result of aligning speech segments with visual scenes."""
    segments: List[SpeechSegment]
    scene_mapping: Dict[int, SpeechSegment]  # scene_index -> SpeechSegment
    total_duration: float


class SpeechCueAlignEngine:
    """
    Analyzes voice-over audio and aligns it with scene scripts to determine
    optimal cut points for visual transitions following Picture-Book Motion principles.
    """

    def __init__(self, min_silence_duration: float = 0.25):
        self.min_silence_duration = min_silence_duration

    def get_audio_duration(self, audio_path: Path) -> float:
        """Get exact duration of audio file in seconds via ffprobe or wave/fallback."""
        if not audio_path.exists():
            return 21.0

        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(audio_path)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration = float(res.stdout.strip())
            if duration > 0:
                return duration
        except Exception:
            pass

        # Fallback based on file size if MP3 ~192kbps
        try:
            size = os.path.getsize(audio_path)
            # 192kbps is 24000 bytes/sec
            return max(5.0, size / 24000.0)
        except Exception:
            return 21.0

    def parse_script_content(self, content: str) -> List[Tuple[str, str]]:
        """
        Parses script content string into structured [(scene_title, scene_text)] entries.
        Supports:
        - Universal JSON formats (arrays of scene objects, key-value objects, nested lists)
        - (Next image) or [Next image] split tags
        - [Scene N: Title] blocks
        - Standard paragraph blocks
        """
        content = content.strip()
        if not content:
            return []

        # 1. Try parsing as JSON
        if (content.startswith("[") and content.endswith("]")) or (content.startswith("{") and content.endswith("}")):
            try:
                data = json.loads(content)
                scenes = []
                if isinstance(data, list):
                    for idx, item in enumerate(data, 1):
                        if isinstance(item, str) and item.strip():
                            scenes.append((f"Scene {idx}", item.strip()))
                        elif isinstance(item, dict):
                            title = item.get("title") or item.get("scene_title") or f"Scene {item.get('scene', idx)}"
                            text = item.get("text") or item.get("narration") or item.get("script") or item.get("caption") or ""
                            if text:
                                scenes.append((str(title), str(text).strip()))
                    if scenes:
                        return scenes
                elif isinstance(data, dict):
                    nested = data.get("scenes") or data.get("story") or data.get("script")
                    if isinstance(nested, list):
                        for idx, item in enumerate(nested, 1):
                            if isinstance(item, str) and item.strip():
                                scenes.append((f"Scene {idx}", item.strip()))
                            elif isinstance(item, dict):
                                title = item.get("title") or item.get("scene_title") or f"Scene {item.get('scene', idx)}"
                                text = item.get("text") or item.get("narration") or item.get("script") or item.get("caption") or ""
                                if text:
                                    scenes.append((str(title), str(text).strip()))
                        if scenes:
                            return scenes
                    else:
                        for idx, (k, v) in enumerate(data.items(), 1):
                            if isinstance(v, str) and v.strip():
                                scenes.append((str(k), v.strip()))
                            elif isinstance(v, dict):
                                txt = v.get("text") or v.get("narration") or str(v)
                                scenes.append((str(k), str(txt).strip()))
                        if scenes:
                            return scenes
            except Exception:
                pass

        # 2. Try splitting by (Next image) / [Next image] / (next scene)
        next_img_pattern = re.compile(r"(?:\(|\[)\s*next\s*(?:image|scene|frame)?\s*(?:\)|\])", re.IGNORECASE)
        if next_img_pattern.search(content):
            parts = next_img_pattern.split(content)
            scenes = []
            for idx, part in enumerate(parts, 1):
                clean = " ".join(part.strip().split())
                if clean:
                    scenes.append((f"Scene {idx}", clean))
            if scenes:
                return scenes

        # 3. Try [Scene ...: ...] blocks
        pattern = re.compile(r"\[(Scene\s*[^\]]+)\]\s*\n([^\[]+)", re.MULTILINE)
        matches = pattern.findall(content)
        if matches:
            scenes = []
            for title, text in matches:
                clean_text = " ".join(text.strip().split())
                if clean_text:
                    scenes.append((title.strip(), clean_text))
            if scenes:
                return scenes

        # 4. Fallback: split by double newlines or non-empty lines
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        scenes = []
        for idx, p in enumerate(paragraphs, 1):
            clean_text = " ".join(p.split())
            if clean_text:
                scenes.append((f"Scene {idx}", clean_text))

        return scenes

    def parse_script(self, script_path: Path) -> List[Tuple[str, str]]:
        """
        Parse script file into structured [(scene_title, scene_text)] entries.
        """
        print(f"[Speech-Cue Align Engine] Parsing script: {script_path}")
        if not script_path.exists():
            raise FileNotFoundError(f"Script file not found: {script_path}")

        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        return self.parse_script_content(content)

    def detect_silence_pauses(self, audio_path: Path, noise_db: int = -22, min_dur: float = 0.18) -> List[Tuple[float, float]]:
        """
        Detect silence intervals in audio using FFmpeg silencedetect.
        Returns a list of (start_time, end_time) pause tuples.
        """
        if not audio_path.exists():
            return []
        try:
            cmd = [
                "ffmpeg", "-i", str(audio_path),
                "-af", f"silencedetect=noise={noise_db}dB:d={min_dur}",
                "-f", "null", "-"
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            pauses: List[Tuple[float, float]] = []
            cur_start = None
            for line in res.stderr.splitlines():
                if "silence_start:" in line:
                    parts = line.split("silence_start:")
                    try:
                        cur_start = float(parts[1].split()[0])
                    except (IndexError, ValueError):
                        cur_start = None
                elif "silence_end:" in line and cur_start is not None:
                    parts = line.split("silence_end:")
                    try:
                        end_t = float(parts[1].split()[0])
                        pauses.append((cur_start, end_t))
                    except (IndexError, ValueError):
                        pass
                    cur_start = None
            return pauses
        except Exception:
            return []

    def align_speech_with_script(self, audio_path: Path, script_path: Path) -> AlignmentResult:
        """
        Align speech segments from audio with script scenes based on narrative cadence.
        Allocates start and end times according to narrative weight/length and waveform silence pauses.
        """
        print("[Speech-Cue Align Engine] Starting speech-script alignment...")
        total_duration = self.get_audio_duration(audio_path)
        print(f"[Speech-Cue Align Engine] Audio duration detected: {total_duration:.2f}s")

        parsed_scenes = self.parse_script(script_path)
        if not parsed_scenes:
            raise ValueError(f"No scenes found in script: {script_path}")

        print(f"[Speech-Cue Align Engine] Parsed {len(parsed_scenes)} scene blocks")

        # Length-based duration allocation (character length + word count)
        char_counts = [max(1, len(text.strip())) for _, text in parsed_scenes]
        word_counts = [max(1, len(text.strip().split())) for _, text in parsed_scenes]
        total_chars = sum(char_counts)
        total_words = sum(word_counts)

        # Combined weight: character count (55%) reflects syllable length, word count (45%) reflects rhythm
        weights = [
            0.55 * (c / total_chars) + 0.45 * (w / total_words)
            for c, w in zip(char_counts, word_counts)
        ]

        n_scenes = len(parsed_scenes)
        min_scene_dur = min(1.8, total_duration / max(n_scenes * 1.5, 1))
        allocatable = total_duration - (n_scenes * min_scene_dur)

        if allocatable > 0:
            target_durations = [min_scene_dur + (w * allocatable) for w in weights]
        else:
            target_durations = [w * total_duration for w in weights]

        # Calculate nominal cut timestamps
        nominal_cuts = [0.0]
        cur = 0.0
        for dur in target_durations[:-1]:
            cur += dur
            nominal_cuts.append(cur)
        nominal_cuts.append(total_duration)

        # Waveform Silence Snapping: snap inner cuts to speech pause midpoints
        silence_pauses = self.detect_silence_pauses(audio_path)
        snapped_cuts = [0.0]

        for i in range(1, n_scenes):
            target_cut = nominal_cuts[i]
            min_boundary = snapped_cuts[-1] + min_scene_dur
            max_boundary = total_duration - ((n_scenes - i) * min_scene_dur)

            best_cut = target_cut
            best_dist = float("inf")

            search_radius = min(1.4, target_durations[i - 1] * 0.4, target_durations[i] * 0.4)
            for p_start, p_end in silence_pauses:
                p_mid = (p_start + p_end) / 2.0
                dist = abs(p_mid - target_cut)
                if dist <= search_radius and dist < best_dist:
                    if min_boundary <= p_mid <= max_boundary:
                        best_cut = p_mid
                        best_dist = dist

            best_cut = max(min_boundary, min(best_cut, max_boundary))
            snapped_cuts.append(round(best_cut, 2))

        snapped_cuts.append(round(total_duration, 2))

        aligned_segments: List[SpeechSegment] = []
        for i, (title, text) in enumerate(parsed_scenes):
            start_t = snapped_cuts[i]
            end_t = snapped_cuts[i + 1]
            aligned_segments.append(
                SpeechSegment(
                    start_time=start_t,
                    end_time=end_t,
                    text=text,
                    scene_title=title,
                    confidence=0.98 if silence_pauses else 0.95
                )
            )

        scene_mapping = {i: seg for i, seg in enumerate(aligned_segments)}
        result = AlignmentResult(
            segments=aligned_segments,
            scene_mapping=scene_mapping,
            total_duration=round(total_duration, 2)
        )

        print(f"[Speech-Cue Align Engine] Alignment complete. Total duration: {total_duration:.2f}s")
        print(f"[Speech-Cue Align Engine] Aligned {len(aligned_segments)} scenes.")
        return result

    def export_alignment(self, result: AlignmentResult, output_path: Path) -> None:
        """Export alignment to both human-readable text and JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[Speech-Cue Align Engine] Exporting alignment to: {output_path}")

        # Human-readable export
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# FB 2minutes Storymaker - Speech Alignment Export\n")
            f.write(f"# Total Duration: {result.total_duration:.2f} seconds\n")
            f.write(f"# Number of Segments: {len(result.segments)}\n\n")

            for i, seg in enumerate(result.segments):
                f.write(f"Scene {i + 1} [{seg.scene_title}]:\n")
                f.write(f"  Time: {seg.start_time:.2f}s - {seg.end_time:.2f}s (duration: {seg.end_time - seg.start_time:.2f}s)\n")
                f.write(f"  Text: {seg.text}\n")
                f.write(f"  Confidence: {seg.confidence:.2f}\n\n")

        # JSON export for downstream modules
        json_path = output_path.with_suffix(".json")
        data = {
            "total_duration": result.total_duration,
            "segment_count": len(result.segments),
            "segments": [asdict(s) for s in result.segments]
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Speech-Cue Align Engine")
    parser.add_argument("--audio", type=str, default="assets/voice-over/narration.mp3")
    parser.add_argument("--script", type=str, default="assets/scripts/story.txt")
    parser.add_argument("--output", type=str, default="assets/processed/alignment.txt")
    args = parser.parse_args()

    engine = SpeechCueAlignEngine()
    result = engine.align_speech_with_script(Path(args.audio), Path(args.script))
    engine.export_alignment(result, Path(args.output))
    print("✅ Alignment completed.")


if __name__ == "__main__":
    main()