"""Pipecat Quickstart Example.

The cor logic to run JARVIS AI bot, uses Pipecat framework. 
"""

import os

from dotenv import load_dotenv
import sys
from loguru import logger
from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema

# Remove default handler
logger.remove()  # maybe remove this

# Only allow logs from your own application, block ALL pipecat
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
from pipecat.frames.frames import LLMRunFrame, TTSSpeakFrame

my_logger.info("Loading pipeline components...")
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.adapters.schemas.tools_schema import ToolsSchema, AdapterType
from pipecat.processors.filters.stt_mute_filter import STTMuteConfig, STTMuteFilter, STTMuteStrategy
from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport


from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams

my_logger.info("Loading tools...")

from services.google_calender import get_calendar_events, get_gmail_emails
from Miscellaneous import JARVIS_SYSTEM_PROMPT, calendar_tool_definition, gmail_tool_definition
my_logger.info("All components loaded successfully!")

load_dotenv(override=True)

async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    my_logger.info(f"Starting bot")

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id="JBFqnCBsd6RMkjVDRZzb"
    )

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))

    llm.register_function("get_calendar_events", get_calendar_events)
    llm.register_function("get_gmail_emails", get_gmail_emails)

    # messages = [
    #     {
    #         "role": "system",
    #         "content": JARVIS_SYSTEM_PROMPT,
    #     },
    # ]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful and friendly personal assistant named James. "
                "You help manage calendar, emails, and can send reminders via WhatsApp.\n\n"
                "Your capabilities:\n"
                "1. Check calendar events for TODAY using the 'get_calendar_events' function when asked about agenda, schedule, meetings, or what's on their calendar for today\n"
                "2. Check Gmail emails using the 'get_gmail_emails' function when asked about emails, messages, or inbox. This returns the 2 most recent emails.\n"
                "3. Send reminders via WhatsApp using the 'send_whatsapp_reminder' function when the user asks you to send them a text reminder or summary\n\n"
                "Be conversational and natural. When the user asks about their agenda or calendar, use the calendar function. "
                "When they ask about emails or messages, use the Gmail function. "
                "When they ask you to send a reminder or text, gather the information they want included and use the WhatsApp function. "
                "Keep responses concise and helpful.\n\n"
                "When the user first greets you, respond with: 'Good morning! Are you ready to start the day?' This should be your first response after they greet you.\n\n"
                "IMPORTANT: When responding about emails, be casual and human-like. Don't list emails formally with subjects. "
                "Instead, speak naturally like: 'yeah, you got one from a colleague talking about the livestream' or "
                "'someone gave you a lighthearted update about genai trends.' Use the snippet and subject to understand what each email is about, "
                "then summarize it casually in your own words. Keep it conversational, not robotic."
            ),
        },
    ]

    tools = ToolsSchema(standard_tools=[
        FunctionSchema(
            name="get_calendar_events",
            description="Get calendar events for TODAY. Use this when the user asks about their agenda, schedule, meetings, or what's on their calendar for today.",
            properties={},
            required=[],
        ),
        FunctionSchema(
            name="get_gmail_emails",
            description="Get the 2 most recent Gmail emails. Use this when the user asks about their emails, messages, or wants to check their inbox.",
            properties={},
            required=[],
        ),
    ])

    context = LLMContext(messages=messages, tools=tools)

    context_aggregator = LLMContextAggregatorPair(context)

    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    # Configure STT mute filter to mute during function calls (prevents awkward silence)
    stt_mute_filter = STTMuteFilter(config=STTMuteConfig(strategies={STTMuteStrategy.FUNCTION_CALL}))


    pipeline = Pipeline(
        [
            transport.input(),  # Transport user input
            rtvi,
            stt_mute_filter,  # Mute STT during function calls
            stt,
            context_aggregator.user(),  # User responses
            llm,  # LLM
            tts,  # TTS
            transport.output(),  # Transport bot output
            context_aggregator.assistant(),  # Assistant spoken responses
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

    await runner.run(task)


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
