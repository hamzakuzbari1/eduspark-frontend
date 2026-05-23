"""Background lesson processing (Marker/OCR must not block HTTP handlers)."""

import logging

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.lesson import Lesson, LessonStatus
from app.services.lesson_processor import process_lesson

logger = logging.getLogger(__name__)

# Track in-flight jobs to avoid duplicate tasks per lesson
_running: set[int] = set()


async def run_process_lesson_background(lesson_id: int, teacher_id: int) -> None:
    if lesson_id in _running:
        logger.info("lesson_id=%s already processing in background", lesson_id)
        return

    _running.add(lesson_id)
    logger.info("Background process started lesson_id=%s teacher_id=%s", lesson_id, teacher_id)

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Lesson).where(
                    Lesson.id == lesson_id,
                    Lesson.teacher_id == teacher_id,
                )
            )
            lesson = result.scalar_one_or_none()
            if not lesson:
                logger.error("Background process: lesson_id=%s not found", lesson_id)
                return
            if not lesson.pdf_path:
                lesson.status = LessonStatus.error
                lesson.error_message = "ملف PDF غير مرفوع"
                await db.commit()
                return

            await process_lesson(db, lesson)
    except Exception as exc:
        logger.exception("Background process failed lesson_id=%s: %s", lesson_id, exc)
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
                lesson = result.scalar_one_or_none()
                if lesson:
                    lesson.status = LessonStatus.error
                    lesson.error_message = str(exc)[:500]
                    await db.commit()
        except Exception:
            logger.exception("Failed to persist error status for lesson_id=%s", lesson_id)
    finally:
        _running.discard(lesson_id)
        logger.info("Background process finished lesson_id=%s", lesson_id)
