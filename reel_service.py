import os
from typing import Optional
from media_utils import (
    scan_media_files,
    copy_reel_to_gallery,
    get_preferred_engine,
    mark_folder_as_processed,
)
from text_to_speech import text_to_audio
from reel_ffmpeg import create_reel_ffmpeg
from reel_moviepy import create_reel_moviepy

DEFAULT_ENGINE = os.getenv("DEFAULT_REEL_ENGINE", "ffmpeg").lower()

def create_reel(
    folder: str,
    engine: Optional[str] = None,
    upload_dir: str = "user_uploads",
    static_reels_dir: str = "static/reels"
) -> Optional[str]:
    """
    Creates reel.mp4 in user_uploads/<folder> using either 'ffmpeg' or 'moviepy'.
    Copies the generated reel to static/reels/<folder>.mp4 upon completion.
    
    Args:
        folder: Subdirectory name inside upload_dir (e.g., UUID).
        engine: 'ffmpeg' or 'moviepy'. If None, auto-detected from engine.txt or DEFAULT_ENGINE.
        upload_dir: Root uploads directory.
        static_reels_dir: Target gallery directory.

    Returns:
        Path to generated reel.mp4, or None on failure.
    """
    folder_path = os.path.join(upload_dir, folder)
    audio_path = os.path.join(folder_path, "audio.mp3")
    output_reel_path = os.path.join(folder_path, "reel.mp4")

    if not os.path.exists(audio_path):
        print(f"[reel_service] Audio file not found at {audio_path}. Skipping reel creation.", flush=True)
        return None

    media_files = scan_media_files(folder_path)
    if not media_files:
        print(f"[reel_service] No images or videos found in {folder_path}. Skipping reel creation.", flush=True)
        return None

    selected_engine = engine.lower() if engine else get_preferred_engine(folder_path, default_engine=DEFAULT_ENGINE)
    print(f"[reel_service] Generating reel for '{folder}' using engine: [{selected_engine.upper()}]", flush=True)

    try:
        if selected_engine == "ffmpeg":
            create_reel_ffmpeg(
                folder_path=folder_path,
                audio_path=audio_path,
                media_files=media_files,
                output_reel_path=output_reel_path
            )
        elif selected_engine == "moviepy":
            create_reel_moviepy(
                folder_path=folder_path,
                audio_path=audio_path,
                media_files=media_files,
                output_reel_path=output_reel_path
            )
        else:
            raise ValueError(f"Unknown engine '{selected_engine}'. Supported engines: 'ffmpeg', 'moviepy'")

        # Copy to static gallery directory
        gallery_path = copy_reel_to_gallery(output_reel_path, folder, static_dir=static_reels_dir)
        print(f"[reel_service] Copied to gallery: {gallery_path}", flush=True)

        return output_reel_path

    except Exception as e:
        print(f"[reel_service] Error creating reel for '{folder}' with {selected_engine}: {e}", flush=True)
        return None

def process_folder(
    folder: str,
    engine: Optional[str] = None,
    upload_dir: str = "user_uploads",
    static_reels_dir: str = "static/reels",
    done_file: str = "done.txt"
) -> bool:
    """
    Executes the full pipeline for a folder:
    1. Generates TTS audio from text.txt (if audio.mp3 doesn't exist).
    2. Builds reel.mp4 with the chosen engine (ffmpeg or moviepy).
    3. Records folder completion in done.txt.

    Returns:
        True if reel was successfully created, False otherwise.
    """
    folder_path = os.path.join(upload_dir, folder)
    if not os.path.isdir(folder_path):
        return False

    print(f"\n==========================================", flush=True)
    print(f"Starting processing for folder: {folder}", flush=True)
    print(f"==========================================", flush=True)

    # Step 1: Generate speech audio if missing
    audio_path = os.path.join(folder_path, "audio.mp3")
    if not os.path.exists(audio_path):
        print(f"[Pipeline] Generating speech audio...", flush=True)
        text_to_audio(folder)

    # Step 2: Create reel
    reel_path = create_reel(
        folder=folder,
        engine=engine,
        upload_dir=upload_dir,
        static_reels_dir=static_reels_dir
    )

    # Step 3: Mark complete
    if reel_path and os.path.exists(reel_path):
        mark_folder_as_processed(folder, done_file=done_file)
        print(f"[Pipeline] Successfully processed folder: {folder}\n", flush=True)
        return True
    else:
        print(f"[Pipeline] Reel creation incomplete for folder: {folder}\n", flush=True)
        return False
