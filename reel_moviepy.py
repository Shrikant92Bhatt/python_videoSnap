import os
from typing import List, Tuple
from moviepy import ImageClip, VideoFileClip, AudioFileClip, concatenate_videoclips

def build_moviepy_clip(
    file_path: str,
    media_type: str,
    duration: float,
    target_size: Tuple[int, int] = (1080, 1920)
):
    """
    Constructs a MoviePy clip (ImageClip or VideoFileClip) scaled to target_size
    and adjusted to the requested duration.
    """
    if media_type == "image":
        return ImageClip(file_path).with_duration(duration).resized(target_size)
    elif media_type == "video":
        clip = VideoFileClip(file_path).resized(target_size)
        if clip.duration > duration:
            return clip.subclipped(0, duration)
        else:
            return clip.with_duration(duration)
    else:
        raise ValueError(f"Unsupported media type: {media_type}")

def create_reel_moviepy(
    folder_path: str,
    audio_path: str,
    media_files: List[Tuple[str, str]],
    output_reel_path: str,
    target_size: Tuple[int, int] = (1080, 1920),
    fps: int = 24
) -> str:
    """
    Reel generation using MoviePy.
    Loads audio and media clips, stitches them sequentially, and encodes to MP4.
    """
    audio = None
    clips = []
    final_video = None

    try:
        audio = AudioFileClip(audio_path)
        total_audio_duration = audio.duration
        duration_per_clip = max(1.0, total_audio_duration / len(media_files))

        print(f"[MoviePy] Total audio: {total_audio_duration:.2f}s | Clips: {len(media_files)} | Per clip: {duration_per_clip:.2f}s", flush=True)

        for idx, (media_type, file_path) in enumerate(media_files):
            print(f"[MoviePy] Processing [{idx+1}/{len(media_files)}] ({media_type}): {os.path.basename(file_path)}", flush=True)
            clip = build_moviepy_clip(file_path, media_type, duration_per_clip, target_size)
            clips.append(clip)

        if not clips:
            raise RuntimeError("No valid clips could be processed.")

        print(f"[MoviePy] Concatenating {len(clips)} clips and attaching audio...", flush=True)
        final_video = concatenate_videoclips(clips, method="compose").with_audio(audio)

        final_video.write_videofile(
            output_reel_path,
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile_path=folder_path,
            remove_temp=True,
            logger=None
        )

        print(f"[MoviePy] Reel successfully rendered: {output_reel_path}", flush=True)
        return output_reel_path

    finally:
        # Guarantee all clip references are released
        for clip in clips:
            try:
                clip.close()
            except Exception:
                pass

        if final_video:
            try:
                final_video.close()
            except Exception:
                pass

        if audio:
            try:
                audio.close()
            except Exception:
                pass
