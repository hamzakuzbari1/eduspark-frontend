"""LLM answers — Ollama (Gemma) primary, Gemini fallback."""

import logging
import time

import httpx

from app.ai.rag_context import format_chunks_for_prompt
from app.core.config import get_settings

logger = logging.getLogger(__name__)

_PLACEHOLDER_KEYS = frozenset(
    {"", "your-gemini-api-key-here", "changeme", "change-me"}
)


def is_llm_available() -> bool:
    settings = get_settings()
    key = (settings.GEMINI_API_KEY or "").strip().lower()
    if key and key not in _PLACEHOLDER_KEYS and "your-gemini" not in key:
        return True
    return bool((settings.OLLAMA_BASE_URL or "").strip())


def build_rag_prompt(
    question: str,
    context_chunks: list[str],
    *,
    subject: str = "",
    grade: str = "",
    difficulty: str = "medium",
    lesson_title: str = "",
) -> str:
    settings = get_settings()
    context_block = format_chunks_for_prompt(
        context_chunks,
        max_per_chunk=settings.RAG_MAX_CHUNK_CHARS,
        max_total=settings.RAG_MAX_CONTEXT_CHARS,
    )

    if not context_block.strip():
        context_block = "(لا يوجد نص درس متاح في السياق.)"

    title_line = f"عنوان الدرس: {lesson_title}\n" if lesson_title else ""
    meta = f"المادة: {subject or '—'} | الصف: {grade or '—'} | المستوى: {difficulty}"

    return f"""أنت معلّم سوري. لديك مقتطفات من درس واحد فقط (مرقمة [1] [2] [3]).

{title_line}{meta}

مقتطفات الدرس (المصدر الوحيد المسموح):
{context_block}

سؤال الطالب:
{question}

اكتب الجواب باللهجة السورية المبسّطة (3–6 جمل):
- استخدم فقط معلومات المقتطفات أعلاه.
- ممنوع المعرفة العامة أو شرح مواضيع غير موجودة في المقتطفات.
- إذا المقتطفات لا تجيب على السؤال، قل بوضوح: «هالمعلومة مو موجودة بملف الدرس» واقترح سؤالاً أدق.
- لا تنسخ النص حرفياً ولا تذكر أرقام المقتطفات في جوابك."""


def build_system_instruction(
    persona_prompt: str,
    subject: str,
    grade: str,
    difficulty: str,
    lesson_title: str = "",
) -> str:
    base = (persona_prompt or "").strip()
    if not base:
        base = "أنت معلّم سوري صبور."
    title = lesson_title or "الدرس"
    return f"""{base}

قواعد صارمة:
- مصدرك الوحيد هو مقتطفات ملف الدرس «{title}» المرسلة مع السؤال.
- لا تستخدم معلومات خارج الدرس ولا تقدّم شروحات عامة عن موضوعات أخرى.
- إذا السياق لا يكفي، اعترف بذلك بصراحة بدل التخمين.
المادة: {subject} | الصف: {grade} | المستوى: {difficulty}."""


def _log_llm_prompt(prompt: str, system_instruction: str | None, lesson_id: int | None = None) -> None:
    settings = get_settings()
    if not settings.RAG_LOG_LLM_PROMPT:
        return
    sep = "=" * 60
    logger.info("%s GEMMA PROMPT lesson_id=%s %s", sep, lesson_id, sep)
    if system_instruction:
        logger.info("SYSTEM (%s chars):\n%s", len(system_instruction), system_instruction[:500])
    logger.info("USER PROMPT (%s chars):\n%s", len(prompt), prompt)
    logger.info("%s END PROMPT %s", sep, sep)


async def generate_answer(
    prompt: str,
    *,
    system_instruction: str | None = None,
    lesson_id: int | None = None,
) -> str:
    settings = get_settings()
    skip_dump = settings.RAG_DEBUG

    if (settings.OLLAMA_BASE_URL or "").strip():
        _log_llm_prompt(prompt, system_instruction, lesson_id)
        try:
            logger.info(
                "[ollama] request start model=%s lesson_id=%s prompt_chars=%s",
                settings.OLLAMA_MODEL,
                lesson_id,
                len(prompt),
            )
            t0 = time.perf_counter()
            text = await _ollama_generate(
                prompt,
                settings.OLLAMA_MODEL,
                settings.OLLAMA_BASE_URL,
                system_instruction,
                timeout=float(settings.OLLAMA_TIMEOUT_SECONDS),
            )
            logger.info(
                "[ollama] request done lesson_id=%s duration=%.1fs response_len=%s preview=%r",
                lesson_id,
                time.perf_counter() - t0,
                len(text or ""),
                (text or "")[:180],
            )
            if text and (skip_dump or not _looks_like_raw_dump(text)):
                return text
        except Exception as exc:
            logger.exception("Ollama failed: %s", exc)

    key = (settings.GEMINI_API_KEY or "").strip()
    if key and key.lower() not in _PLACEHOLDER_KEYS and "your-gemini" not in key.lower():
        _log_llm_prompt(prompt, system_instruction, lesson_id)
        try:
            text = await _gemini_generate(prompt, system_instruction or "")
            if text and (skip_dump or not _looks_like_raw_dump(text)):
                return text
        except Exception as exc:
            logger.warning("Gemini failed: %s", exc)

    return ""


def _looks_like_raw_dump(text: str) -> bool:
    if len(text) < 80:
        return False
    if any(m in text for m in ("[1]", "[2]", "مقتطفات الدرس", "[صفحة")):
        return True
    return len(text) > 900 and text.count(".") + text.count("؟") < 3


async def _gemini_generate(prompt: str, system_instruction: str) -> str:
    import google.generativeai as genai

    settings = get_settings()
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        settings.GEMINI_MODEL,
        system_instruction=system_instruction or None,
        generation_config={"temperature": 0.4, "top_p": 0.85, "max_output_tokens": 768},
    )
    response = model.generate_content(prompt)
    return (response.text or "").strip()


async def _ollama_generate(
    prompt: str,
    model: str,
    base_url: str,
    system_instruction: str | None,
    timeout: float = 180.0,
) -> str:
    url = base_url.rstrip("/") + "/api/chat"
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})
    payload = {"model": model, "messages": messages, "stream": False}
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return (response.json().get("message", {}).get("content") or "").strip()
