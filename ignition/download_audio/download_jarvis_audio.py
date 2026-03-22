from download_audio.eleven_client import generate_audio
import subprocess
text_to_download = "Very Good Sir. Initiating dev server on port five-thousand seven-hundred forty-one"
audio_file_name = "test_audio.mp3"

Titan_voice_id = "wyWA56cQNU2KqUW4eCsI"
George_voice_id = "JBFqnCBsd6RMkjVDRZzb"
Jamal_voice_id = "G17SuINrv2H9FC6nvetn"

def download_audio(audio, filename=audio_file_name):
    with open(filename, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    print(f"Downloaded {filename}...")

def play_saved_audio(filepath):
    """Play an MP3 file using macOS's built-in afplay command."""
    subprocess.run(["afplay", filepath])

if __name__ == "__main__":

    print("Available voices:")
    print("1. George")
    print("2. Jamal")
    print("3. Titan")
    voice_id = input("Enter the voice ID: ")
    if voice_id == "1":
        voice_id = George_voice_id
    elif voice_id == "2":
        voice_id = Jamal_voice_id
    elif voice_id == "3":
        voice_id = Titan_voice_id
    else:
        print("Invalid voice ID")
        exit(1)
    fresh_audio = generate_audio(text_to_download, voice_id)  # generate again!
    download_audio(fresh_audio, audio_file_name)
    play_saved_audio(audio_file_name)
