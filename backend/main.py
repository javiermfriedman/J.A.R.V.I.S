"""
The main file to run the FastAPI server and handle the WebRTC connection.
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection
from pipecat.transports.smallwebrtc.request_handler import (
    SmallWebRTCRequest, SmallWebRTCPatchRequest, SmallWebRTCRequestHandler
)
from pipecat.runner.types import SmallWebRTCRunnerArguments
import bot  # your bot.py

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

handler = SmallWebRTCRequestHandler()

@app.post("/api/offer")
async def offer(request: SmallWebRTCRequest, background_tasks: BackgroundTasks):
    async def on_connection(connection: SmallWebRTCConnection):
        runner_args = SmallWebRTCRunnerArguments(webrtc_connection=connection)
        background_tasks.add_task(bot.bot, runner_args)
    return await handler.handle_web_request(request, on_connection)

@app.patch("/api/offer")
async def ice(request: SmallWebRTCPatchRequest):
    await handler.handle_patch_request(request)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)  # your port here