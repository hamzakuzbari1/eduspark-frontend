"""Voice transcription and teaching-style persona extraction."""

import json
import logging
from pathlib import Path

from app.ai.async_jobs import run_sync_with_timeout
from app.ai.whisper import is_whisper_available, transcribe_audio_sync
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

DEFAULT_PERSONA = """أنت معلّم سوري ودود يشرح للطلاب باللهجة السورية المبسّطة.
استخدم أمثلة من الحياة اليومية، اشرح خطوة بخطوة، وشجّع الطالب.
لا تجب إلا من محتوى الدرس المرفوع — إذا السؤال خارج المحتوى قل ذلك بلطف."""


def _transcribe_gemini_sync(path: Path) -> str:
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    uploaded = genai.upload_file(path)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    response = model.generate_content(
        [
            "انسخ هذا التسجيل الصوتي للمعلّم بالعربية. أعد النص فقط بدون تعليقات.",
            uploaded,
        ]
    )
    return (response.text or "").strip()


def _build_persona_gemini_sync(transcript: str, subject: str, grade: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(settings.GEMINI_MODEL)
    prompt = f"""حلّل أسلوب هذا المعلّم من النص الصوتي واكتب Persona Prompt بالعربية لتوجيه ذكاء اصطناعي
للشرح بنفس الأسلوب واللهجة السورية. المادة: {subject}، الصف: {grade}.

نص المعلّم:
{transcript[:3000]}

أعد JSON فقط بالشكل:
{{"persona": "..."}}"""
    response = model.generate_content(prompt)
    text = (response.text or "").strip()
    if "{" in text:
        data = json.loads(text[text.index("{") : text.rindex("}") + 1])
        return data.get("persona", DEFAULT_PERSONA)
    return DEFAULT_PERSONA


async def transcribe_audio(
    audio_path: str | Path,
    *,
    lesson_id: int | None = None,
) -> str:
    path = Path(audio_path)
    if not path.exists():
        logger.info("[voice] lesson_id=%s no audio file — skip transcribe", lesson_id)
        return ""

    timeout = float(settings.VOICE_TRANSCRIBE_TIMEOUT_SECONDS)

    if is_whisper_available():
        text = await run_sync_with_timeout(
            transcribe_audio_sync,
            path,
            "ar",
            timeout=timeout,
            label="VOICE_WHISPER_TRANSCRIBE",
            lesson_id=lesson_id,
            default="",
        )
        if isinstance(text, str) and text.strip():
            logger.info("[voice] lesson_id=%s whisper chars=%s", lesson_id, len(text))
            return text

    if settings.GEMINI_API_KEY:
        try:
            text = await run_sync_with_timeout(
                _transcribe_gemini_sync,
                path,
                timeout=timeout,
                label="VOICE_GEMINI_TRANSCRIBE",
                lesson_id=lesson_id,
                default="",
            )
            if text.strip():
                logger.info("[voice] lesson_id=%s gemini transcribe chars=%s", lesson_id, len(text))
                return text
        except Exception as exc:
            logger.warning("[voice] lesson_id=%s gemini transcribe failed: %s", lesson_id, exc)

    fallback = "مرحبا يا شباب، اليوم رح نشرح الدرس بطريقة سهلة ومبسطة مثل ما بشرح دائماً."
    logger.info("[voice] lesson_id=%s using default transcript", lesson_id)
    return fallback


async def build_persona_prompt(
    transcript: str,
    subject: str,
    grade: str,
    *,
    lesson_id: int | None = None,
) -> str:
    if settings.GEMINI_API_KEY and transcript:
        try:
            persona = await run_sync_with_timeout(
                _build_persona_gemini_sync,
                transcript,
                subject,
                grade,
                timeout=float(settings.PERSONA_BUILD_TIMEOUT_SECONDS),
                label="PERSONA_GEMINI_BUILD",
                lesson_id=lesson_id,
                default=None,
            )
            if persona:
                logger.info(
                    "[voice] lesson_id=%s persona built chars=%s",
                    lesson_id,
                    len(persona),
                )
                return persona
        except Exception as exc:
            logger.warning("[voice] lesson_id=%s persona build failed: %s", lesson_id, exc)

    persona = (
        f"{DEFAULT_PERSONA}\n\n"
        f"المادة: {subject}، الصف: {grade}.\n"
        f"عيّن أسلوب الشرح بناءً على عينة الصوت: {transcript[:500]}"
    )
    logger.info("[voice] lesson_id=%s persona default chars=%s", lesson_id, len(persona))
    return persona
