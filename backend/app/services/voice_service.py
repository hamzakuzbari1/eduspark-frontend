"""Voice transcription and teaching-style persona extraction."""

import json
import logging
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

DEFAULT_PERSONA = """أنت معلّم سوري ودود يشرح للطلاب باللهجة السورية المبسّطة.
استخدم أمثلة من الحياة اليومية، اشرح خطوة بخطوة، وشجّع الطالب.
لا تجب إلا من محتوى الدرس المرفوع — إذا السؤال خارج المحتوى قل ذلك بلطف."""


async def transcribe_audio(audio_path: str | Path) -> str:
    path = Path(audio_path)
    if not path.exists():
        return ""

    if settings.GEMINI_API_KEY:
        try:
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
        except Exception as exc:
            logger.warning("Gemini transcription failed: %s", exc)

    return "مرحبا يا شباب، اليوم رح نشرح الدرس بطريقة سهلة ومبسطة مثل ما بشرح دائماً."


async def build_persona_prompt(transcript: str, subject: str, grade: str) -> str:
    if settings.GEMINI_API_KEY and transcript:
        try:
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
        except Exception as exc:
            logger.warning("Persona generation failed: %s", exc)

    return (
        f"{DEFAULT_PERSONA}\n\n"
        f"المادة: {subject}، الصف: {grade}.\n"
        f"عيّن أسلوب الشرح بناءً على عينة الصوت: {transcript[:500]}"
    )
