import os
import shutil
import subprocess

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
IGNORED_FILES = {"reel.mp4", "audio.mp3", "text.txt", "engine.txt"}

def get_media_type(filename: str):
    """
    Determines whether a file is an image, video, or unsupported.
    Returns 'image', 'video', or None.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    elif ext in VIDEO_EXTENSIONS:
        return "video"
    return None

def scan_media_files(folder_path: str):
    """
    Scans a folder for image and video files (ignoring output/meta files).
    Returns a list of tuples: (media_type, file_path) sorted alphabetically.
    """
    if not os.path.exists(folder_path):
        return []

    media_files = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.lower() in IGNORED_FILES:
            continue
        
        media_type = get_media_type(filename)
        if media_type:
            media_files.append((media_type, os.path.join(folder_path, filename)))

    return media_files

def get_audio_duration(audio_path: str) -> float:
    """
    Retrieves audio duration in seconds using ffprobe.
    Falls back to MoviePy AudioFileClip if ffprobe fails.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at: {audio_path}")

    # Try ffprobe first (fast, minimal memory)
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        if duration > 0:
            return duration
    except Exception:
        pass

    # Fallback to MoviePy
    try:
        from moviepy import AudioFileClip
        audio = AudioFileClip(audio_path)
        duration = float(audio.duration)
        audio.close()
        return duration
    except Exception as e:
        raise RuntimeError(f"Unable to determine duration for {audio_path}: {e}")

def copy_reel_to_gallery(output_reel_path: str, folder_name: str, static_dir: str = "static/reels") -> str:
    """
    Copies the generated reel to the static gallery directory for web preview.
    """
    os.makedirs(static_dir, exist_ok=True)
    destination = os.path.join(static_dir, f"{folder_name}.mp4")
    shutil.copy2(output_reel_path, destination)
    return destination

def load_processed_folders(done_file: str = "done.txt") -> set:
    """
    Reads the list of already processed folder names from done.txt.
    """
    if not os.path.exists(done_file):
        return set()

    with open(done_file, "r", encoding="utf-8") as f:
        return {line.strip() for line in f.read().splitlines() if line.strip()}

def mark_folder_as_processed(folder_name: str, done_file: str = "done.txt"):
    """
    Appends a completed folder name to done.txt.
    """
    with open(done_file, "a", encoding="utf-8") as f:
        f.write(f"{folder_name}\n")

def get_preferred_engine(folder_path: str, default_engine: str = "ffmpeg") -> str:
    """
    Determines which engine to use ('ffmpeg' or 'moviepy').
    Checks for an engine.txt file in the folder, or falls back to default.
    """
    engine_file = os.path.join(folder_path, "engine.txt")
    if os.path.exists(engine_file):
        try:
            with open(engine_file, "r", encoding="utf-8") as f:
                choice = f.read().strip().lower()
                if choice in {"ffmpeg", "moviepy"}:
                    return choice
        except Exception:
            pass

    return default_engine.lower()
