"""Tutoring replies: cleaned RAG context → lesson-only LLM answers."""

import logging

from app.ai.llm import (
    build_rag_prompt,
    build_system_instruction,
    generate_answer,
    is_llm_available,
)
from app.ai.rag_context import format_chunks_for_prompt
from app.core.config import get_settings

logger = logging.getLogger(__name__)

OUT_OF_SCOPE_REPLY = (
    "هالمعلومة ما موجودة بملف الدرس اللي رُفع. "
    "جرّب تسأل عن فقرة أو مفهوم محدد من نفس الدرس."
)

LLM_UNAVAILABLE_REPLY = (
    "المعلّم الذكي مو متصل. تحقق من OLLAMA_BASE_URL واسم النموذج (مثلاً gemma3:4b)."
)


async def generate_tutor_reply(
    question: str,
    context_chunks: list[str],
    persona_prompt: str,
    subject: str,
    grade: str,
    difficulty: str = "medium",
    *,
    lesson_title: str = "",
    retrieval_meta: dict | None = None,
) -> str:
    settings = get_settings()
    meta = retrieval_meta or {}
    lesson_id = meta.get("lesson_id")

    logger.info(
        "generate_tutor_reply lesson_id=%s strategy=%s chunks=%s context_chars≈%s",
        lesson_id,
        meta.get("strategy"),
        len(context_chunks),
        len(format_chunks_for_prompt(context_chunks)) if context_chunks else 0,
    )
    for i, ch in enumerate(context_chunks[:3]):
        logger.info("  llm_context[%s]=%r", i, ch[:100])

    if not context_chunks:
        if settings.RAG_DEBUG:
            return (
                f"[DEBUG] لا سياق. lesson_id={lesson_id} db={meta.get('total_in_db')} "
                f"usable={meta.get('usable_in_db')} strategy={meta.get('strategy')}"
            )
        return OUT_OF_SCOPE_REPLY

    if not is_llm_available():
        return LLM_UNAVAILABLE_REPLY if not settings.RAG_DEBUG else "[DEBUG] LLM not configured"

    system = build_system_instruction(
        persona_prompt, subject or "—", grade or "—", difficulty, lesson_title
    )
    prompt = build_rag_prompt(
        question,
        context_chunks,
        subject=subject,
        grade=grade,
        difficulty=difficulty,
        lesson_title=lesson_title,
    )

    reply = await generate_answer(prompt, system_instruction=system, lesson_id=lesson_id)
    if reply:
        return reply

    if settings.RAG_DEBUG:
        return "[DEBUG] Gemma returned empty — see prompt in server logs."

    return "تعذر توليد الجواب. جرّب إعادة صياغة السؤال."
