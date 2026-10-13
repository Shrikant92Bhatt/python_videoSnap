"""
VideoSnap Reel Generator Worker
Monitors user_uploads/ for new folders and converts them into reels.
Supports both FFmpeg and MoviePy engines.
"""

import os
import time
import argparse
from typing import Optional
from media_utils import load_processed_folders
from reel_service import create_reel, process_folder

DEFAULT_UPLOAD_DIR = "user_uploads"
DEFAULT_DONE_FILE = "done.txt"
DEFAULT_INTERVAL_SECONDS = 10

def process_pending_folders(
    engine: Optional[str] = None,
    upload_dir: str = DEFAULT_UPLOAD_DIR,
    done_file: str = DEFAULT_DONE_FILE
) -> int:
    """
    Performs a single scan of upload_dir, processing all folders not yet listed in done_file.
    Returns the number of newly processed folders.
    """
    if not os.path.exists(upload_dir):
        print(f"Upload directory '{upload_dir}' does not exist.", flush=True)
        return 0

    done_folders = load_processed_folders(done_file)
    candidate_folders = sorted(os.listdir(upload_dir))
    processed_count = 0

    for folder in candidate_folders:
        folder_path = os.path.join(upload_dir, folder)
        if not os.path.isdir(folder_path):
            continue

        if folder not in done_folders:
            print(f"Found unprocessed folder: {folder}", flush=True)
            success = process_folder(
                folder=folder,
                engine=engine,
                upload_dir=upload_dir,
                done_file=done_file
            )
            if success:
                done_folders.add(folder)
                processed_count += 1

    return processed_count

def watch_folders(
    engine: Optional[str] = None,
    interval: int = DEFAULT_INTERVAL_SECONDS,
    upload_dir: str = DEFAULT_UPLOAD_DIR,
    done_file: str = DEFAULT_DONE_FILE
) -> None:
    """
    Continuously monitors the upload directory for new folders and processes them.
    """
    engine_label = engine.upper() if engine else "AUTO (engine.txt or default)"
    print("=" * 60, flush=True)
    print(f" VideoSnap Watcher Started", flush=True)
    print(f" Engine: {engine_label}", flush=True)
    print(f" Watching: {upload_dir}/", flush=True)
    print(f" Poll Interval: {interval}s", flush=True)
    print("=" * 60, flush=True)

    try:
        while True:
            print(f"Checking for new folders in {upload_dir}...", flush=True)
            processed = process_pending_folders(
                engine=engine,
                upload_dir=upload_dir,
                done_file=done_file
            )

            if processed == 0:
                print(f"No new folders found. Waiting {interval} seconds...", flush=True)

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nWatcher stopped by user. Exiting gracefully.", flush=True)

def parse_cli_arguments():
    """
    Parses command-line arguments for manual or automated runs.
    """
    parser = argparse.ArgumentParser(description="VideoSnap Reel Generation Worker")
    parser.add_argument(
        "--engine",
        type=str,
        choices=["ffmpeg", "moviepy"],
        default=None,
        help="Reel engine to use ('ffmpeg' or 'moviepy'). Default: checks engine.txt or environment."
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process current pending folders once and exit instead of running continuously."
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL_SECONDS,
        help=f"Polling interval in seconds (default: {DEFAULT_INTERVAL_SECONDS})."
    )
    return parser.parse_args()

def main():
    args = parse_cli_arguments()
    if args.once:
        print(f"Running single pass (Engine: {args.engine or 'AUTO'})...", flush=True)
        count = process_pending_folders(engine=args.engine)
        print(f"Single pass complete. Processed {count} folder(s).", flush=True)
    else:
        watch_folders(engine=args.engine, interval=args.interval)

if __name__ == "__main__":
    main()