import os
import subprocess
import tempfile
from typing import List, Tuple
from media_utils import get_audio_duration

def create_media_segment_ffmpeg(
    file_path: str,
    media_type: str,
    duration: float,
    output_segment_path: str,
    target_size: Tuple[int, int] = (1080, 1920),
    fps: int = 24
) -> None:
    """
    Renders an individual image or video into a normalized 1080x1920 MP4 clip.
    Preserves original aspect ratio with centered black letterboxing/pillarboxing.
    """
    width, height = target_size
    vf_filter = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,setsar=1"
    )

    if media_type == "image":
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-t", str(duration),
            "-i", file_path,
            "-vf", vf_filter,
            "-r", str(fps),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-an",
            output_segment_path
        ]
    elif media_type == "video":
        cmd = [
            "ffmpeg", "-y",
            "-t", str(duration),
            "-i", file_path,
            "-vf", vf_filter,
            "-r", str(fps),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-an",
            output_segment_path
        ]
    else:
        raise ValueError(f"Unsupported media type: {media_type}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed while processing {file_path}:\n{result.stderr}")

def concatenate_segments_ffmpeg(
    segment_paths: List[str],
    audio_path: str,
    output_reel_path: str
) -> None:
    """
    Combines pre-rendered segments with the audio track into the final reel.mp4.
    """
    temp_dir = os.path.dirname(segment_paths[0])
    concat_list_path = os.path.join(temp_dir, "concat_list.txt")

    # Write concat manifest with forward slashes for cross-platform compatibility
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for seg in segment_paths:
            normalized_path = os.path.abspath(seg).replace("\\", "/")
            f.write(f"file '{normalized_path}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_reel_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg concat failed:\n{result.stderr}")

def create_reel_ffmpeg(
    folder_path: str,
    audio_path: str,
    media_files: List[Tuple[str, str]],
    output_reel_path: str,
    target_size: Tuple[int, int] = (1080, 1920),
    fps: int = 24
) -> str:
    """
    High-performance Reel generation using direct FFmpeg CLI calls.
    Splits audio duration equally across all media files and stitches into a 9:16 reel.
    """
    total_audio_duration = get_audio_duration(audio_path)
    duration_per_clip = max(1.0, total_audio_duration / len(media_files))

    print(f"[FFmpeg] Total audio: {total_audio_duration:.2f}s | Clips: {len(media_files)} | Per clip: {duration_per_clip:.2f}s", flush=True)

    with tempfile.TemporaryDirectory(dir=folder_path) as temp_dir:
        segment_paths = []
        for idx, (media_type, file_path) in enumerate(media_files):
            segment_out = os.path.join(temp_dir, f"segment_{idx:03d}.mp4")
            print(f"[FFmpeg] Processing [{idx+1}/{len(media_files)}] ({media_type}): {os.path.basename(file_path)}", flush=True)
            create_media_segment_ffmpeg(
                file_path=file_path,
                media_type=media_type,
                duration=duration_per_clip,
                output_segment_path=segment_out,
                target_size=target_size,
                fps=fps
            )
            segment_paths.append(segment_out)

        print(f"[FFmpeg] Concatenating {len(segment_paths)} clips with audio...", flush=True)
        concatenate_segments_ffmpeg(segment_paths, audio_path, output_reel_path)

    print(f"[FFmpeg] Reel successfully rendered: {output_reel_path}", flush=True)
    return output_reel_path
