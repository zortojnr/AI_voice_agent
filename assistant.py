"""
assistant.py

Purpose: Defines the Assistant class for the MyVoice project.
Handles: audio VAD, transcription with Gemini, text generation with Gemini,
and TTS via ElevenLabs, streaming audio back through LiveKit AgentSession.
"""

import asyncio
import base64
import io
import logging
import wave
from dataclasses import dataclass
from typing import Optional

import google.generativeai as genai
from livekit.agents import llm, stt, vad
from livekit.plugins.silero import VAD as SileroVAD
from livekit.plugins.elevenlabs import TTS as ElevenLabsTTS
from livekit.agents.utils import audio as audio_utils


logger = logging.getLogger("myvoice.assistant")
logger.setLevel(logging.DEBUG)  # Increased logging for debugging


@dataclass
class AssistantConfig:
    gemini_model: str = "models/gemini-1.5-flash"
    elevenlabs_voice: Optional[str] = None  # Use default if None
    sample_rate_hz: int = 16000
    num_channels: int = 1


class GeminiSTT(stt.STT):
    """Speech-to-Text using Google Gemini's multimodal API."""

    def __init__(self, *, api_key: str, model: str = "models/gemini-1.5-flash", room=None):
        super().__init__()
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)
        self._sample_rate = 16000
        self._num_channels = 1
        self._room = room  # Store room reference for sending data messages

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @property
    def num_channels(self) -> int:
        return self._num_channels

    async def transcribe(self, *, buffer: audio_utils.AudioBuffer) -> stt.SpeechEvent:
        """Transcribe audio buffer using Gemini."""
        logger.debug(f"Transcribing audio buffer: {len(buffer.data)} samples, {buffer.sample_rate}Hz, {buffer.num_channels} channels")
        
        # Convert AudioBuffer to WAV bytes
        pcm_data = buffer.data.tobytes() if hasattr(buffer.data, 'tobytes') else bytes(buffer.data)
        logger.debug(f"Converted to PCM bytes: {len(pcm_data)} bytes")
        
        wav_bytes = _pcm16_to_wav_bytes(pcm_data, buffer.sample_rate, buffer.num_channels)
        logger.debug(f"Converted to WAV: {len(wav_bytes)} bytes")

        b64_audio = base64.b64encode(wav_bytes).decode("ascii")
        logger.debug(f"Sending to Gemini API: {len(b64_audio)} base64 chars")

        # Call Gemini API
        try:
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(
                None,
                lambda: self._model.generate_content([
                    {"mime_type": "audio/wav", "data": b64_audio},
                    {"text": "Transcribe this audio to text. Reply with only the transcript, no additional text."},
                ])
            )

            text = (resp.text or "").strip() if resp else ""
            logger.info(f"Transcribed: '{text}'")
            
            if not text:
                logger.warning("Empty transcription received from Gemini")
            else:
                # Send transcription as data message to room if available
                if self._room:
                    try:
                        import asyncio
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.create_task(self._send_transcription(text))
                        else:
                            loop.run_until_complete(self._send_transcription(text))
                    except Exception as e:
                        logger.error(f"Error sending transcription to room: {e}")

        except Exception as e:
            logger.error(f"Error during transcription: {e}", exc_info=True)
            text = ""

        return stt.SpeechEvent(
            type=stt.SpeechEventType.FINAL_TRANSCRIPT,
            alternatives=[stt.SpeechData(text=text, language="en")],
        )
    
    async def _send_transcription(self, text: str):
        """Send transcription as data message to room."""
        if self._room and self._room.local_participant:
            try:
                await self._room.local_participant.publish_data(
                    text.encode('utf-8'),
                    topic="transcription",
                    reliable=True
                )
                logger.debug(f"Sent transcription to room: {text}")
            except Exception as e:
                logger.error(f"Failed to send transcription: {e}")


class GeminiLLM(llm.LLM):
    """Language Model using Google Gemini."""

    def __init__(self, *, api_key: str, model: str = "models/gemini-1.5-flash", room=None):
        super().__init__()
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)
        self._room = room  # Store room reference for sending data messages

    async def chat(
        self,
        *,
        chat_ctx: llm.ChatContext,
        **kwargs,
    ) -> "llm.LLMStream":
        """Generate response using Gemini."""
        messages = []
        for item in chat_ctx.messages:
            if item.role == llm.ChatRole.USER:
                messages.append({"role": "user", "parts": [{"text": item.content}]})
            elif item.role == llm.ChatRole.ASSISTANT:
                messages.append({"role": "model", "parts": [{"text": item.content}]})

        system_prompt = (
            "You are a concise, helpful real-time voice assistant. "
            "Keep responses short and conversational."
        )

        class GeminiStream(llm.LLMStream):
            def __init__(self, model, messages, system_prompt, room):
                self._model = model
                self._messages = messages
                self._system_prompt = system_prompt
                self._room = room

            async def __aiter__(self):
                # For simplicity, generate all at once
                loop = asyncio.get_event_loop()
                full_prompt = system_prompt + "\n\n"
                for msg in messages:
                    full_prompt += f"{msg['role']}: {msg['parts'][0]['text']}\n"
                full_prompt += "Assistant:"

                resp = await loop.run_in_executor(
                    None,
                    lambda: self._model.generate_content(full_prompt)
                )

                text = (resp.text or "").strip() if resp else ""
                
                # Send response as data message if room is available
                if text and self._room:
                    try:
                        if self._room.local_participant:
                            await self._room.local_participant.publish_data(
                                text.encode('utf-8'),
                                topic="assistant-response",
                                reliable=True
                            )
                            logger.info(f"Sent assistant response to room: {text}")
                    except Exception as e:
                        logger.error(f"Failed to send assistant response: {e}")
                
                yield llm.ChatChunk(
                    id="gemini-response",
                    delta=llm.ChoiceDelta(content=text),
                )

        return GeminiStream(self._model, messages, system_prompt, self._room)


class Assistant:
    """Real-time AI voice assistant orchestrating VAD, STT, LLM, and TTS."""

    def __init__(
        self,
        *,
        gemini_api_key: str,
        eleven_api_key: str,
        config: Optional[AssistantConfig] = None,
    ) -> None:
        self._config = config or AssistantConfig()
        # Store API keys for creating STT/LLM/TTS
        self._gemini_api_key = gemini_api_key
        self._eleven_api_key = eleven_api_key

    def create_stt(self, room=None) -> stt.STT:
        """Create Gemini-based STT."""
        return GeminiSTT(api_key=self._gemini_api_key, model=self._config.gemini_model, room=room)

    def create_llm(self, room=None) -> llm.LLM:
        """Create Gemini-based LLM."""
        return GeminiLLM(api_key=self._gemini_api_key, model=self._config.gemini_model, room=room)

    def create_vad(self, session) -> vad.VAD:
        """Create Silero VAD."""
        return SileroVAD(
            session=session,
            opts=SileroVAD.Options(sample_rate=self._config.sample_rate_hz),
        )

    def create_tts(self) -> "ElevenLabsTTS":
        """Create ElevenLabs TTS."""
        return ElevenLabsTTS(
            api_key=self._eleven_api_key,
            voice_id=self._config.elevenlabs_voice,
        )


def _pcm16_to_wav_bytes(pcm_bytes: bytes, sample_rate: int, channels: int) -> bytes:
    """Convert PCM16 bytes to WAV format."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()
