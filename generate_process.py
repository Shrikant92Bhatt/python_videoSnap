# This file look for new folders inside user_upload folder, and convert them to reel if they are not already converted 

import os
from text_to_speech import text_to_audio
import time

import shutil
from moviepy import ImageClip, VideoFileClip, AudioFileClip, concatenate_videoclips

def create_reel(folder):
    """
    Creates reel.mp4 in user_uploads/<folder> using uploaded images/videos and audio.mp3.
    Also copies the finished reel to static/reels/<folder>.mp4 for gallery preview.
    """
    print(f"Creating reel for folder: {folder}", flush=True)
    folder_path = os.path.join("user_uploads", folder)
    audio_path = os.path.join(folder_path, "audio.mp3")

    if not os.path.exists(audio_path):
        print(f"Audio file not found at {audio_path}, skipping reel creation.", flush=True)
        return None

    image_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

    # Find media files inside the folder (exclude output files)
    media_files = []
    for file in sorted(os.listdir(folder_path)):
        if file.lower() in {"reel.mp4", "audio.mp3", "text.txt"}:
            continue
        ext = os.path.splitext(file)[1].lower()
        if ext in image_exts or ext in video_exts:
            media_files.append((ext, os.path.join(folder_path, file)))

    if not media_files:
        print(f"No image or video files found in {folder_path}, skipping reel creation.", flush=True)
        return None

    try:
        audio = AudioFileClip(audio_path)
        total_audio_duration = audio.duration
        duration_per_clip = max(1.0, total_audio_duration / len(media_files))

        clips = []
        target_size = (1080, 1920)  # Standard 9:16 vertical reel resolution

        for ext, file_path in media_files:
            try:
                if ext in image_exts:
                    clip = ImageClip(file_path).with_duration(duration_per_clip).resized(target_size)
                else:
                    clip = VideoFileClip(file_path).resized(target_size)
                    if clip.duration > duration_per_clip:
                        clip = clip.subclipped(0, duration_per_clip)
                    else:
                        clip = clip.with_duration(duration_per_clip)
                clips.append(clip)
            except Exception as e:
                print(f"Error loading clip {file_path}: {e}", flush=True)

        if not clips:
            print("No valid clips could be processed.", flush=True)
            audio.close()
            return None

        final_video = concatenate_videoclips(clips, method="compose").with_audio(audio)
        output_reel_path = os.path.join(folder_path, "reel.mp4")

        # Render reel.mp4 directly inside the UUID folder
        final_video.write_videofile(
            output_reel_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile_path=folder_path,
            remove_temp=True,
            logger=None
        )

        # Clean up clip memory
        for clip in clips:
            clip.close()
        final_video.close()
        audio.close()

        # Copy to static/reels for gallery display
        os.makedirs(os.path.join("static", "reels"), exist_ok=True)
        static_dest = os.path.join("static", "reels", f"{folder}.mp4")
        shutil.copy2(output_reel_path, static_dest)

        print(f"Reel saved to: {output_reel_path}", flush=True)
        print(f"Copied to gallery: {static_dest}", flush=True)
        return output_reel_path

    except Exception as e:
        print(f"Error creating reel for {folder}: {e}", flush=True)
        return None

if __name__ == "__main__":
    while True:
        print("Checking for new folders in user_uploads...", flush=True)
        done_folders = []
        if os.path.exists("done.txt"):
            with open("done.txt", "r") as f:
                done_folders = [line.strip() for line in f.read().splitlines() if line.strip()]

        folders = os.listdir("user_uploads")
        found_new = False

        for folder in folders:
            folder_path = os.path.join("user_uploads", folder)
            if not os.path.isdir(folder_path):
                continue

            if folder not in done_folders:
                found_new = True
                print(f"Processing new folder: {folder}", flush=True)
                text_to_audio(folder)  # generate audio .mp3 file from text file.
                create_reel(folder)    # create reel.mp4 file from video clips and audio file.
                done_folders.append(folder)
                with open("done.txt", "a") as f:
                    f.write(folder + "\n")

        if not found_new:
            print("No new folders found. Waiting 10 seconds...", flush=True)

        time.sleep(10)