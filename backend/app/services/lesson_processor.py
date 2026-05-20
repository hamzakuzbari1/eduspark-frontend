"""Full lesson processing pipeline: PDF → chunks → voice → quiz (embeddings optional)."""

import json
import logging

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.lesson import ContentChunk, Lesson, LessonStatus
from app.models.quiz import QuizQuestion
from app.services.pdf_service import chunk_text, extract_text_from_pdf
from app.services.quiz_service import generate_quiz_questions
from app.services.voice_service import build_persona_prompt, transcribe_audio

logger = logging.getLogger(__name__)


async def process_lesson(db: AsyncSession, lesson: Lesson) -> Lesson:
    settings = get_settings()
    lesson.status = LessonStatus.processing
    await db.commit()

    try:
        if not lesson.pdf_path:
            raise ValueError("ملف PDF غير مرفوع")

        full_text, page_count, pages_meta = extract_text_from_pdf(lesson.pdf_path)
        if not full_text.strip():
            raise ValueError("تعذر استخراج نص من PDF — جرّب ملفاً آخر")

        lesson.page_count = page_count
        lesson.preview = full_text[:280] + ("…" if len(full_text) > 280 else "")
        if lesson.title == "درس جديد" or not lesson.title:
            lesson.title = _guess_title(full_text, lesson.subject)

        transcript = ""
        if lesson.voice_path:
            transcript = await transcribe_audio(lesson.voice_path)
        lesson.persona_prompt = await build_persona_prompt(
            transcript, lesson.subject, lesson.grade
        )

        await db.execute(delete(ContentChunk).where(ContentChunk.lesson_id == lesson.id))
        text_chunks = chunk_text(full_text)
        for idx, content in enumerate(text_chunks):
            meta = json.dumps(
                {"page_hint": pages_meta[min(idx, len(pages_meta) - 1)]},
                ensure_ascii=False,
            )
            db.add(
                ContentChunk(
                    lesson_id=lesson.id,
                    chunk_index=idx,
                    content=content,
                    metadata_json=meta,
                )
            )

        if settings.ENABLE_EMBEDDINGS:
            logger.info("Embedding generation skipped or disabled (pgvector off)")

        await db.execute(delete(QuizQuestion).where(QuizQuestion.lesson_id == lesson.id))
        quiz_items = await generate_quiz_questions(full_text, lesson.subject, lesson.grade)
        for i, q in enumerate(quiz_items):
            db.add(
                QuizQuestion(
                    lesson_id=lesson.id,
                    question=q["question"],
                    options_json=json.dumps(q["options"], ensure_ascii=False),
                    correct_index=q["correct_index"],
                    hint=q.get("hint"),
                    sort_order=i,
                )
            )

        lesson.status = LessonStatus.processed
        lesson.error_message = None
    except Exception as exc:
        logger.exception("Lesson processing failed: %s", exc)
        lesson.status = LessonStatus.error
        lesson.error_message = str(exc)

    await db.commit()
    await db.refresh(lesson)
    return lesson


def _guess_title(text: str, subject: str) -> str:
    first_line = text.split("\n", 1)[0].strip()[:80]
    if len(first_line) > 10:
        return first_line
    return f"درس {subject}"
