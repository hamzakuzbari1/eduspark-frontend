"""Text-to-speech — XTTS optional."""

import asyncio
import logging
import uuid
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_tts_model = None
_tts_device = None


def _load_tts():
    global _tts_model, _tts_device
    if _tts_model is None:
        import torch
        from TTS.api import TTS

        settings = get_settings()
        _tts_device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("Loading TTS model on %s", _tts_device)
        _tts_model = TTS(settings.TTS_MODEL).to(_tts_device)
    return _tts_model


def text_to_speech_sync(
    text: str,
    speaker_wav: str | Path,
    output_path: str | Path | None = None,
    language: str = "ar",
) -> str:
    settings = get_settings()
    if not settings.USE_LOCAL_TTS or not text.strip():
        return ""

    speaker = Path(speaker_wav)
    if not speaker.exists():
        logger.warning("Speaker reference not found: %s", speaker)
        return ""

    out = Path(output_path) if output_path else Path(settings.UPLOAD_DIR) / "tts" / f"{uuid.uuid4().hex}.wav"
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        model = _load_tts()
        model.tts_to_file(
            text=text,
            speaker_wav=str(speaker),
            language=language,
            file_path=str(out),
        )
        return str(out)
    except Exception as exc:
        logger.warning("TTS failed: %s", exc)
        return ""


async def text_to_speech(
    text: str,
    speaker_wav: str | Path,
    output_path: str | Path | None = None,
    language: str = "ar",
) -> str:
    return await asyncio.to_thread(
        text_to_speech_sync, text, speaker_wav, output_path, language
    )


def is_tts_available() -> bool:
    settings = get_settings()
    if not settings.USE_LOCAL_TTS:
        return False
    try:
        import TTS  # noqa: F401

        return True
    except ImportError:
        return False
