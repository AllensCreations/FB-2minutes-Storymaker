"""
Final Master Video Exporter for FB 2minutes Storymaker
Pipes generated Picture-Book Motion frames to FFmpeg, multiplexing voice-over audio
into a production-quality 9:16 vertical MP4 video.
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Optional

# Add src to sys.path for direct script execution
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from choreography_core import VisualChoreographer
from duration_director import MasterTimeline, SceneTimeline


class VideoExporter:
    """
    Renders video frames and multiplexes audio using FFmpeg to export
    the final master MP4 video.
    """

    def __init__(self, fps: int = 24):
        self.fps = fps

    def find_active_scene(self, timeline: MasterTimeline, t: float) -> SceneTimeline:
        """Find the scene corresponding to timestamp t."""
        for s in timeline.scenes:
            if s.start_time <= t < s.end_time:
                return s
        return timeline.scenes[-1]

    def export_video(
        self,
        timeline: MasterTimeline,
        audio_path: Path,
        output_path: Path,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        show_captions: bool = True
    ) -> Path:
        """
        Renders the complete story video and exports it to output_path.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[Video Exporter] Starting video export to: {output_path} (captions: {'ON' if show_captions else 'OFF'})")

        choreographer = VisualChoreographer(width=timeline.width, height=timeline.height)
        fps = timeline.fps or self.fps
        total_duration = timeline.total_duration
        total_frames = max(1, int(round(total_duration * fps)))

        print(f"[Video Exporter] Total Duration: {total_duration:.2f}s | FPS: {fps} | Total Frames: {total_frames}")

        # Check FFmpeg
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except Exception:
            raise RuntimeError("FFmpeg is not installed or not found on PATH.")

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{timeline.width}x{timeline.height}",
            "-pix_fmt", "rgb24",
            "-r", str(fps),
            "-i", "-",
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            str(output_path)
        ]

        proc = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )

        start_clock = time.time()
        try:
            for frame_idx in range(total_frames):
                total_t = frame_idx / fps
                scene = self.find_active_scene(timeline, total_t)
                scene_t = total_t - scene.start_time

                frame_img = choreographer.render_frame(
                    scene=scene,
                    scene_t=scene_t,
                    total_t=total_t,
                    total_duration=total_duration,
                    show_captions=show_captions
                )

                # Write raw RGB bytes to ffmpeg stdin
                assert proc.stdin is not None
                proc.stdin.write(frame_img.tobytes())

                # Report progress
                if frame_idx % fps == 0 or frame_idx == total_frames - 1:
                    percent = (frame_idx + 1) / total_frames * 100.0
                    elapsed = time.time() - start_clock
                    fps_render = (frame_idx + 1) / max(elapsed, 0.001)
                    eta = (total_frames - (frame_idx + 1)) / max(fps_render, 0.001)
                    status_msg = f"Frame {frame_idx + 1}/{total_frames} ({percent:.1f}%) | {fps_render:.1f} fps | ETA: {eta:.1f}s"
                    print(f"  [Render] {status_msg}")
                    if progress_callback:
                        progress_callback(percent, status_msg)

            assert proc.stdin is not None
            proc.stdin.close()
            _, stderr_data = proc.communicate()

            if proc.returncode != 0:
                err_text = stderr_data.decode("utf-8", errors="replace")
                raise RuntimeError(f"FFmpeg render failed (exit code {proc.returncode}):\n{err_text}")

        except Exception as e:
            proc.kill()
            raise e

        total_elapsed = time.time() - start_clock
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"✅ Video export completed in {total_elapsed:.1f}s!")
        print(f"📁 Output: {output_path} ({file_size_mb:.2f} MB)")
        return output_path


def main():
    from align_engine import SpeechCueAlignEngine
    from duration_director import SceneDurationDirector

    audio_path = Path("assets/voice-over/narration.mp3")
    script_path = Path("assets/scripts/story.txt")
    visuals_path = Path("assets/visuals/story_visuals.zip")
    output_path = Path("assets/output/final_story.mp4")

    print("Testing Video Exporter Pipeline...")
    aligner = SpeechCueAlignEngine()
    alignment = aligner.align_speech_with_script(audio_path, script_path)

    director = SceneDurationDirector()
    timeline = director.build_timeline(alignment, visuals_path, fps=24)

    exporter = VideoExporter(fps=24)
    exporter.export_video(timeline, audio_path, output_path)


if __name__ == "__main__":
    main()
