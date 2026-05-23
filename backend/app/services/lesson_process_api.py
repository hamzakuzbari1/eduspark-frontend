"""Shared HTTP handlers for lesson processing (sync or background)."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.lesson import Lesson, LessonStatus
from app.schemas.teacher import ProcessResponse
from app.services.lesson_jobs import run_process_lesson_background
from app.services.lesson_processor import process_lesson

logger = logging.getLogger(__name__)


async def start_lesson_processing(
    db: AsyncSession,
    lesson: Lesson,
    teacher_id: int,
) -> ProcessResponse:
    """
    When PDF_PROCESS_IN_BACKGROUND is on, return immediately and run OCR/RAG in a task.
    Otherwise block until process_lesson completes (PyMuPDF-only setups).
    """
    settings = get_settings()

    if lesson.status == LessonStatus.processing:
        return ProcessResponse(
            lesson_id=lesson.id,
            status=LessonStatus.processing.value,
            message="المعالجة جارية بالفعل — انتظر أو راجع الحالة لاحقاً",
        )

    if settings.PDF_PROCESS_IN_BACKGROUND:
        lesson.status = LessonStatus.processing
        lesson.error_message = None
        await db.commit()
        asyncio.create_task(run_process_lesson_background(lesson.id, teacher_id))
        msg = "جاري المعالجة في الخلفية"
        if settings.USE_MARKER_PDF:
            msg += " (Marker PDF قد يستغرق عدة دقائق — يمكنك مغادرة الصفحة)"
        logger.info("Scheduled background process lesson_id=%s", lesson.id)
        return ProcessResponse(
            lesson_id=lesson.id,
            status=LessonStatus.processing.value,
            message=msg,
        )

    lesson = await process_lesson(db, lesson)
    return ProcessResponse(
        lesson_id=lesson.id,
        status=lesson.status.value,
        message=lesson.error_message or "اكتملت المعالجة بنجاح",
    )
