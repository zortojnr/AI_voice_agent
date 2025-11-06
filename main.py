"""
main.py

Purpose: Entry point for the MyVoice project. Loads environment variables,
connects to LiveKit using livekit-agents, and runs the Assistant session.
Supports CLI and Jupyter execution via cli.run_app.
"""

import logging
import os

from dotenv import load_dotenv
from livekit.agents import JobContext, cli
from livekit.agents.voice import Agent, AgentSession

from assistant import Assistant, AssistantConfig


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("myvoice.main")


async def entrypoint(ctx: JobContext) -> None:
    """LiveKit Agents entrypoint. Creates and runs the voice assistant in a room."""
    load_dotenv()

    gemini_key = os.getenv("GEMINI_API_KEY")
    eleven_key = os.getenv("ELEVEN_API_KEY")
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not all([gemini_key, eleven_key, livekit_url, livekit_api_key, livekit_api_secret]):
        raise RuntimeError("Missing one or more required environment variables.")

    assistant_factory = Assistant(
        gemini_api_key=gemini_key,
        eleven_api_key=eleven_key,
        config=AssistantConfig(),
    )

    # Create Agent with STT, LLM, TTS, and VAD
    # Note: VAD needs to be created after AgentSession is available
    logger.info("Creating MyVoice agent...")
    
    # Create STT and LLM with room reference for sending transcriptions and responses
    stt_instance = assistant_factory.create_stt(room=ctx.room)
    llm_instance = assistant_factory.create_llm(room=ctx.room)
    
    agent = Agent(
        instructions="You are a concise, helpful real-time voice assistant. Keep responses short and conversational.",
        stt=stt_instance,
        llm=llm_instance,
        tts=assistant_factory.create_tts(),
    )

    # Create AgentSession and initialize VAD
    session = AgentSession(
        stt=agent.stt,
        llm=agent.llm,
        tts=agent.tts,
    )
    session.vad = assistant_factory.create_vad(session)
    
    logger.info("Starting MyVoice assistant session...")
    await session.start(agent, room=ctx.room)
    logger.info("Connected to LiveKit and joined room as 'MyVoice-agent'")
    
    # Update room references in STT and LLM after session starts
    if hasattr(stt_instance, '_room'):
        stt_instance._room = ctx.room
    if hasattr(llm_instance, '_room'):
        llm_instance._room = ctx.room
    
    # Log when participants join
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant):
        logger.info(f"Participant connected: {participant.identity}")
        logger.info(f"Participant tracks: {[t.kind for t in participant.track_publications.values()]}")
    
    @ctx.room.on("track_subscribed")
    def on_track_subscribed(track, publication, participant):
        logger.info(f"Track subscribed: {track.kind} from {participant.identity}")
        if track.kind == "audio":
            logger.info(f"Audio track subscribed from {participant.identity}, sample_rate: {track.sample_rate}")
            logger.info(f"Audio track info: muted={track.is_muted}, enabled={not track.is_muted}")

    # Wait for session to complete
    await session.aclose()


if __name__ == "__main__":
    import sys
    
    # Check if user wants web interface
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        from web_interface import start_server
        logger.info("Starting web interface mode...")
        logger.info("Note: Make sure the agent is running in another terminal with: python main.py")
        start_server(open_browser=True)
    else:
        # Default: run as LiveKit agent
        # Allows both CLI execution and Jupyter-friendly run
        # cli.run_app handles worker spin-up if needed.
        cli.run_app(entrypoint)
