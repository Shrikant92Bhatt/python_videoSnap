# This file look for new folders inside user_upload folder, and convert them to reel if they are not already converted 

import os

def text_to_audio(folder):
    print("Converting text to audio for folder: ", folder)
    pass

def create_reel(folder):
    print("Creating reel for folder: ", folder)
    pass

if __name__ == "__main__":
    done_folders = []
    if os.path.exists("done.txt"):
        with open("done.txt", "r") as f:
            done_folders = f.read().splitlines()

    folders = os.listdir("user_uploads")

    for folder in folders:
        folder_path = os.path.join("user_uploads", folder)
        if not os.path.isdir(folder_path):
            continue

        if folder not in done_folders:
            text_to_audio(folder)  # generate audio .mp3 file from text file.
            create_reel(folder)    # create reel.mp4 file from video clips and audio file.
            done_folders.append(folder)
            with open("done.txt", "a") as f:
                f.write(folder + "\n")