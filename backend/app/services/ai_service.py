"""Gemini tutoring with PDF-scoped RAG context."""

import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

OUT_OF_SCOPE_REPLY = (
    "عذراً، هذا السؤال خارج محتوى الدرس المرفوع. "
    "راجع ملف PDF أو اسألني عن جزء موجود بالدرس."
)


async def generate_tutor_reply(
    question: str,
    context_chunks: list[str],
    persona_prompt: str,
    subject: str,
    grade: str,
    difficulty: str = "medium",
) -> str:
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else ""

    if not context.strip():
        return OUT_OF_SCOPE_REPLY

    system = f"""{persona_prompt}

قواعد صارمة:
- أجب بالعربية السورية المبسّطة فقط.
- استخدم فقط المعلومات من «محتوى الدرس» أدناه.
- إذا الإجابة غير موجودة في المحتوى، قل أن السؤال خارج الدرس.
- المادة: {subject}، الصف: {grade}، مستوى الطالب: {difficulty}.
"""

    user_prompt = f"""محتوى الدرس:
{context[:12000]}

سؤال الطالب:
{question}
"""

    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(
                settings.GEMINI_MODEL,
                system_instruction=system,
            )
            response = model.generate_content(user_prompt)
            reply = (response.text or "").strip()
            if reply:
                return reply
        except Exception as exc:
            logger.warning("Gemini chat failed: %s", exc)

    # Fallback: simple extractive answer
    snippet = context_chunks[0][:400] if context_chunks else ""
    return (
        f"باختصار من الدرس: {snippet}...\n\n"
        "إذا بدك تفصيل أكثر، اسألني عن نقطة محددة من الدرس."
    )
