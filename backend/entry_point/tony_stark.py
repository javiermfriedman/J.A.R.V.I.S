import subprocess
import time
import sys
TRACK_URI = "spotify:track:39shmbIHICJ2Wxnk1fPSdz"

def open_spotify():
    if sys.platform == "darwin":  # macOS
        # Open Spotify with the track URI
        subprocess.Popen(["open", TRACK_URI])

    print("Opening Spotify and playing 'Should I Stay or Should I Go' by The Clash...")
    time.sleep(3)
    print("Done! Check Spotify.")


def play_saved_audio(filepath):
    """Play an MP3 file using macOS's built-in afplay command."""
    subprocess.run(["afplay", filepath])

def start_dev_server():
    subprocess.Popen([
        "osascript", "-e",
        '''tell app "Terminal"
            activate
            do script "/Users/javierfriedman/Code/J.A.R.V.I.S/backend/venv/bin/python /Users/javierfriedman/Code/J.A.R.V.I.S/backend/bot.py"
        end tell'''
    ])
    print("Starting J.A.R.V.I.S server in new terminal...")

    # Poll until server is ready
    import urllib.request
    for _ in range(10):  # try for up to 60 seconds
        time.sleep(1)
        try:
            urllib.request.urlopen("http://localhost:7860/client")
            subprocess.Popen(["open", "-a", "Safari", "http://localhost:7860/client"])
            print("✅ Server ready! Opening browser...")
            break
        except:
            pass
    
if __name__ == "__main__":
    open_spotify()
    play_saved_audio("/Users/javierfriedman/Code/J.A.R.V.I.S/backend/entry_point/welcome_home.mp3")
    time.sleep(1)
    play_saved_audio("/Users/javierfriedman/Code/J.A.R.V.I.S/backend/entry_point/open_dev.mp3")
    start_dev_server()  