"""Speech-to-text — local Whisper optional, Gemini fallback in voice_service."""

import asyncio
import logging
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_whisper_model = None


def _load_whisper():
    global _whisper_model
    if _whisper_model is None:
        import whisper

        settings = get_settings()
        logger.info("Loading Whisper model: %s", settings.WHISPER_MODEL)
        _whisper_model = whisper.load_model(settings.WHISPER_MODEL)
    return _whisper_model


def transcribe_audio_sync(audio_path: str | Path, language: str = "ar") -> str:
    path = Path(audio_path)
    if not path.exists():
        return ""

    settings = get_settings()
    if not settings.USE_LOCAL_WHISPER:
        return ""

    try:
        model = _load_whisper()
        result = model.transcribe(str(path), language=language, task="transcribe")
        return (result.get("text") or "").strip()
    except Exception as exc:
        logger.warning("Whisper transcription failed: %s", exc)
        return ""


async def transcribe_audio(audio_path: str | Path, language: str = "ar") -> str:
    return await asyncio.to_thread(transcribe_audio_sync, audio_path, language)


def is_whisper_available() -> bool:
    settings = get_settings()
    if not settings.USE_LOCAL_WHISPER:
        return False
    try:
        import whisper  # noqa: F401

        return True
    except ImportError:
        return False
