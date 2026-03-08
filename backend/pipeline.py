"""J.A.R.V.I.S. AI Bot Pipeline.

The core logic to run the JARVIS AI bot, using the Pipecat framework.
"""

import os

from dotenv import load_dotenv
import sys
from loguru import logger

# THIS removes pipecat logging from terminal
logger.remove()  
logger.add(
    sys.stderr,
    level="DEBUG",
    filter=lambda record: not record["name"].startswith("pipecat")
)

# Your own logging
my_logger = logger.bind(name="jarvis")

my_logger.info("Starting up Jarvis AI...")
my_logger.info("Loading Silero VAD model...")
from pipecat.audio.vad.silero import SileroVADAnalyzer
my_logger.info("Silero VAD model loaded")
from pipecat.frames.frames import TTSSpeakFrame

my_logger.info("Loading pipeline components...")
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.turns.user_mute import FunctionCallUserMuteStrategy
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport


from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams

my_logger.info("Loading tools...")

from services import (
    get_gmail_emails, 
    send_gmail_email, 
    get_calender_events,
    schedule_event, 
    fetch_all_known_contacts,
    get_contact_information,
)
from core import JARVIS_SYSTEM_PROMPT, tools
my_logger.info("All components loaded successfully!")

load_dotenv(override=True)

async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    my_logger.info(f"Starting bot")

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="JBFqnCBsd6RMkjVDRZzb"
    )

    # run_in_parallel=False avoids race conditions and duplicate tool execution
    # (see Pipecat issue #3273 and similar)
    llm = OpenAILLMService(
        api_key=os.getenv("OPENAI_API_KEY"),
        run_in_parallel=False,
    )

    llm.register_function("get_calender_events", get_calender_events)
    llm.register_function("schedule_event", schedule_event)
    llm.register_function("get_gmail_emails", get_gmail_emails)
    llm.register_function("send_gmail_email", send_gmail_email)
    llm.register_function("get_contact_information", get_contact_information)
    llm.register_function("fetch_all_known_contacts", fetch_all_known_contacts)
    messages = [
        {
            "role": "system",
            "content": JARVIS_SYSTEM_PROMPT,
        },
    ]   

    context = LLMContext(messages=messages, tools=tools, tool_choice="auto")
    
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(),
            user_mute_strategies=[FunctionCallUserMuteStrategy()],
        ),
    )

    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    pipeline = Pipeline(
        [
            transport.input(),  # Transport user input
            rtvi,
            stt,
            user_aggregator,  # User responses
            llm,  # LLM
            tts,  # TTS
            transport.output(),  # Transport bot output
            assistant_aggregator,  # Assistant spoken responses
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        my_logger.info(f"Client connected")
        # Speak the exact greeting — bypasses LLM, goes straight to TTS.
        await task.queue_frames([TTSSpeakFrame(text="Hello Sir. All systems are online and await your command.")])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        my_logger.info(f"Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)

    try:
        await runner.run(task)
    except Exception as e:
        my_logger.error(f"Pipeline error: {e}")
        # Categorize the error
        error_str = str(e).lower()
        if "credit" in error_str or "quota" in error_str or "billing" in error_str:
            my_logger.error("💳 Out of credits on one of the API services")
        elif "401" in error_str or "unauthorized" in error_str or "api key" in error_str:
            my_logger.error("🔑 Invalid API key — check OPENAI / DEEPGRAM / ELEVENLABS keys")
        elif "429" in error_str or "rate limit" in error_str:
            my_logger.error("⏱️ Rate limited by an API service")
        elif "timeout" in error_str:
            my_logger.error("⏰ Service timed out")
        else:
            my_logger.error(f"❓ Unknown error: {e}")
        raise


async def bot(runner_args: RunnerArguments):
    """Main bot entry point for the bot starter."""

    transport_params = {
        "daily": lambda: DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
        ),
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
        ),
    }

    transport = await create_transport(runner_args, transport_params)

    print(f"Transport layer: {type(transport).__name__}")

    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
