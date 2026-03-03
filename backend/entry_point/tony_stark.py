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
    print("Starting J.A.R.V.I.S frontend server in new terminal...")
    subprocess.Popen([
        "osascript", "-e",
        '''tell app "Terminal"
            activate
            do script "cd /Users/javierfriedman/Code/J.A.R.V.I.S/frontend && npm run dev"
        end tell'''
    ])
    print("Starting J.A.R.V.I.S backend server in new terminal...")
    subprocess.Popen([
        "osascript", "-e",
        '''tell app "Terminal"
            activate
            do script "/Users/javierfriedman/Code/J.A.R.V.I.S/backend/venv/bin/python /Users/javierfriedman/Code/J.A.R.V.I.S/backend/main.py"
        end tell'''
    ])

    # Poll until server is ready
    import urllib.request
    for _ in range(30):
        time.sleep(1)
        try:
            urllib.request.urlopen("http://localhost:5173/")
            subprocess.Popen(["open", "-a", "Arc", "http://localhost:5173/"])
            print("✅ Frontend ready! Opening Arc...")
            break
        except:
            pass
    else:
        print("❌ Frontend never became ready — check the Terminal window for errors.")
    
if __name__ == "__main__":
    open_spotify()
    play_saved_audio("/Users/javierfriedman/Code/J.A.R.V.I.S/backend/entry_point/welcome_home.mp3")
    time.sleep(1)
    play_saved_audio("/Users/javierfriedman/Code/J.A.R.V.I.S/backend/entry_point/open_dev.mp3")
    start_dev_server()  
