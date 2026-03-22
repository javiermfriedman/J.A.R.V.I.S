import asyncio
import os
import subprocess
from pathlib import Path
import sys
import tempfile
from time import sleep

from loguru import logger
from pipecat.frames.frames import TTSSpeakFrame
from pipecat.services.llm_service import FunctionCallParams

# Repo: ignition/jarvis_audio/ (sibling of backend/)
_SHUTDOWN_MP3 = (
    Path(__file__).resolve().parents[3] / "ignition" / "jarvis_audio" / "shutdown.mp3"
)


async def shutdown_system(params: FunctionCallParams):
    logger.info("Initiating shutdown sequence for J.A.R.V.I.S...")

    await params.llm.push_frame(TTSSpeakFrame("Powering down all systems, sir."))

    await asyncio.sleep(2)

    if sys.platform == "darwin":
        try:
            subprocess.Popen(["afplay", str(_SHUTDOWN_MP3)])

            shutdown_terminal_sequence()

            sleep(2)
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    'tell application "Arc" to quit',
                ],
                check=False,
            )
            logger.info("Arc closed.")
            sleep(1)

            subprocess.run(["osascript", "-e", 'tell application "Spotify" to set sound volume to 0'], check=False)
            logger.info("Spotify volume set to 0.")
            subprocess.run(["osascript", "-e", 'tell application "Spotify" to pause'], check=False)
            logger.info("Spotify paused.")
            subprocess.run(["osascript", "-e", 'tell application "Spotify" to quit'], check=False)
            logger.info("Spotify, Arc, and Spotify faded out and closed.")
            sleep(1)
            subprocess.run(
                ["killall", "Terminal"],
                check=False,
            )
        except Exception as e:
            logger.error(f"Failed to shut down systems: {e}")

def shutdown_terminal_sequence():
    """Open a new Terminal window with a cinematic shutdown log sequence (macOS only)."""
    if sys.platform != "darwin":
        return
    lines = [
        "[SYS]     Flushing final logs .................................. OK",
        "[AI]      Saving conversational context ........................ OK",
        "[AUDIO]   Releasing audio interfaces .......................... OK",
        "[WEBRTC]  Tearing down peer connections ....................... OK",
        "[VITE]    Stopping frontend dev server :5741 ................. OK",
        "[WEB]     Stopping backend API server :8000 .................. OK",
        "[SEC]     Revoking Stark Industries uplink ................... OK",
        "[HW]      Detaching arc reactor control bus .................. OK",
        "[DIAG]    Final diagnostics ................................... CLEAN",
        "[SYS]     Powering down non-critical subsystems .............. OK",
        "[SYS]     J.A.R.V.I.S core shutdown complete. Goodbye, sir.",
    ]
    script = "#!/bin/bash\nclear\n"
    for line in lines:
        script += "sleep 0.25\n"
        script += f"echo '{line}'\n"
    script += 'sleep 0.75\n'
    script += 'rm -- "$0"\n'
    fd, path = tempfile.mkstemp(suffix=".sh")
    with os.fdopen(fd, "w") as f:
        f.write(script)
    os.chmod(path, 0o755)
    subprocess.Popen(
        [
            "osascript",
            "-e",
            f'''tell application "Terminal"
                    activate
                    do script "{path}"
                end tell''',
        ]
    )
