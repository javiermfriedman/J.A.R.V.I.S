from services import generate_audio
import subprocess
text_to_download = "Test Test"
audio_file_name = "/Users/javierfriedman/Code/J.A.R.V.I.S/backend/entry_point/open_dev.mp3"

def download_audio(audio, filename=audio_file_name):
    with open(filename, "wb") as f:
        for chunk in audio:
            f.write(chunk)

def play_saved_audio(filepath):
    """Play an MP3 file using macOS's built-in afplay command."""
    subprocess.run(["afplay", filepath])


if __name__ == "__main__":
    while True:
        print(f"Downloading {audio_file_name}...")
        fresh_audio = generate_audio(text_to_download)  # generate again!
        download_audio(fresh_audio, audio_file_name)
        play_saved_audio(audio_file_name)
        key = input("keep[1], don't keep[2]: ")
        if key == "1":
            break
        else:
            continue