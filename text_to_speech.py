import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

def convert_text_to_speech(text: str, output_path: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb", model_id: str = "eleven_v4"):
    """
    Converts given text into speech and saves it as an MP3 file.
    """
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=voice_id,  # "George" - browse voices at elevenlabs.io/app/voice-library
        model_id=model_id,
        output_format="mp3_44100_128",
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    print(f"Audio generated and saved to: {output_path}")
    return output_path

def text_to_audio(folder: str):
    """
    Reads text.txt from user_uploads/<folder> and generates audio.mp3.
    """
    print("Converting text to audio for folder: ", folder)
    text_file_path = os.path.join("user_uploads", folder, "text.txt")
    if not os.path.exists(text_file_path):
        print(f"No text.txt found in {folder}, skipping audio generation.")
        return None

    with open(text_file_path, "r", encoding="utf-8") as f:
        text_content = f.read().strip()

    if not text_content:
        print(f"text.txt is empty in {folder}, skipping audio generation.")
        return None

    audio_path = os.path.join("user_uploads", folder, "audio.mp3")
    return convert_text_to_speech(text_content, audio_path)

if __name__ == "__main__":
    # Test example
    sample_text = "The first move is what sets everything in motion."
    sample_output = "sample_audio.mp3"
    print("Testing text-to-speech with sample text...")
    convert_text_to_speech(sample_text, sample_output)
