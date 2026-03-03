import subprocess
import time
import sys
TRACK_URI = "spotify:track:39shmbIHICJ2Wxnk1fPSdz"
SPOTIFY_VOLUME = 40  # 0–100 — low enough so J.A.R.V.I.S. is heard over the music

def set_spotify_volume(volume: int):
    """Set Spotify's volume via AppleScript (macOS only)."""
    subprocess.run([
        "osascript", "-e",
        f'tell application "Spotify" to set sound volume to {volume}'
    ])

def open_spotify():
    if sys.platform == "darwin":  # macOS
        # Open Spotify with the track URI
        subprocess.Popen(["open", TRACK_URI])
        set_spotify_volume(100)

    print("Opening Spotify and playing 'Should I Stay or Should I Go' by The Clash...")


def play_saved_audio(filepath):
    """Play an MP3 file using macOS's built-in afplay command. Skips empty/missing files."""
    import os
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        print(f"⚠️  Skipping {os.path.basename(filepath)} (missing or empty)")
        return
    subprocess.run(["afplay", filepath])

def start_dev_server():
    print("Starting J.A.R.V.I.S backend server in new terminal...")
    subprocess.Popen([
        "osascript", "-e",
        '''tell app "Terminal"
            activate
            do script "/Users/javierfriedman/Code/J.A.R.V.I.S/backend/venv/bin/python /Users/javierfriedman/Code/J.A.R.V.I.S/backend/main.py"
        end tell'''
    ])

    subprocess.Popen([
        "osascript", "-e",
        '''tell app "Terminal"
            activate
            do script "cd /Users/javierfriedman/Code/J.A.R.V.I.S/frontend && npm run dev"
        end tell'''
    ])

    # Poll until both servers are ready
    import urllib.request, urllib.error
    backend_up = False
    frontend_up = False

    for attempt in range(30):
        time.sleep(1)

        if not backend_up:
            try:
                urllib.request.urlopen("http://localhost:8000")
                backend_up = True
            except urllib.error.HTTPError:
                # 404 etc. means the server IS responding — it's up
                backend_up = True
            except Exception as e:
                print(f"  ⏳ Waiting for backend... (attempt {attempt+1}, {e.__class__.__name__})")

        if backend_up and not frontend_up:
            try:
                urllib.request.urlopen("http://127.0.0.1:5173")
                frontend_up = True
            except urllib.error.HTTPError:
                frontend_up = True
            except Exception as e:
                print(f"  ⏳ Waiting for frontend... (attempt {attempt+1}, {e.__class__.__name__})")

        if backend_up:
            print("✅ Backend ready!")
        if frontend_up:
            print("✅ Frontend ready!")

        if backend_up and frontend_up:
            print("🚀 Opening Arc...")
            subprocess.Popen(["open", "-a", "Arc", "http://127.0.0.1:5173"])
            set_spotify_volume(30)
            break
    else:
        print("❌ Servers never became ready — check the Terminal windows for errors.")
    
if __name__ == "__main__":
    open_spotify()
    time.sleep(3)
    play_saved_audio("/Users/javierfriedman/Code/J.A.R.V.I.S/backend/entry_point/welcome_home.mp3")
    time.sleep(1)
    play_saved_audio("/Users/javierfriedman/Code/J.A.R.V.I.S/backend/entry_point/open_dev.mp3")
    start_dev_server()  
