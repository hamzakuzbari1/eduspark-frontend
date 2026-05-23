"""Shared student chat logic for /student/chat and /ai/chat."""

import logging
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import ChatMessage
from app.models.lesson import ContentChunk, Lesson, LessonStatus
from app.models.profile import StudentProfile
from app.models.user import User
from app.schemas.student import ChatRequest, ChatResponse
from app.services.ai_service import generate_tutor_reply
from app.services.rag_service import retrieve_chunks_detailed

logger = logging.getLogger(__name__)


def _format_time(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.strftime("%H:%M")


async def handle_student_chat(
    db: AsyncSession,
    student: User,
    body: ChatRequest,
) -> ChatResponse:
    lesson_id = int(body.lesson_id)
    logger.info(
        "Chat student_id=%s lesson_id=%s message=%r",
        student.id,
        lesson_id,
        body.message[:80],
    )

    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.status == LessonStatus.processed)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        chunk_any = await db.scalar(
            select(func.count())
            .select_from(ContentChunk)
            .where(ContentChunk.lesson_id == lesson_id)
        )
        status_row = await db.execute(select(Lesson.status).where(Lesson.id == lesson_id))
        status = status_row.scalar_one_or_none()
        logger.warning(
            "Chat rejected lesson_id=%s status=%s chunks_in_db=%s",
            lesson_id,
            status,
            chunk_any,
        )
        raise ValueError("الدرس غير موجود أو لم تكتمل معالجته بعد")

    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == student.id)
    )
    profile = profile_result.scalar_one_or_none()
    difficulty = profile.difficulty if profile else "medium"

    db.add(
        ChatMessage(
            lesson_id=lesson.id,
            student_id=student.id,
            role="student",
            content=body.message,
        )
    )

    retrieval = await retrieve_chunks_detailed(db, lesson.id, body.message)
    chunks = retrieval.chunks

    retrieval_meta = {
        "lesson_id": lesson.id,
        "total_in_db": retrieval.total_in_db,
        "usable_in_db": retrieval.usable_in_db,
        "retrieval_selected_count": len(retrieval.chunks),
        "strategy": retrieval.strategy,
        "context_char_count": retrieval.context_char_count,
    }

    if not chunks:
        logger.error(
            "lesson_id=%s no chunks after retrieval (db=%s usable=%s strategy=%s) — re-process",
            lesson.id,
            retrieval.total_in_db,
            retrieval.usable_in_db,
            retrieval.strategy,
        )

    reply = await generate_tutor_reply(
        body.message,
        chunks,
        lesson.persona_prompt or "",
        lesson.subject,
        lesson.grade,
        difficulty,
        lesson_title=lesson.title or "",
        retrieval_meta=retrieval_meta,
    )

    ai_msg = ChatMessage(
        lesson_id=lesson.id,
        student_id=student.id,
        role="ai",
        content=reply,
    )
    db.add(ai_msg)
    await db.commit()
    await db.refresh(ai_msg)

    history = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.lesson_id == lesson.id, ChatMessage.student_id == student.id)
        .order_by(ChatMessage.created_at)
    )
    messages = [
        {
            "id": m.id,
            "role": m.role,
            "text": m.content,
            "time": _format_time(m.created_at),
        }
        for m in history.scalars().all()
    ]

    return ChatResponse(reply=reply, messages=messages)
