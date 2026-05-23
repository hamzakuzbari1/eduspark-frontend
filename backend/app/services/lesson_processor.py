"""Full lesson processing: PDF → chunks → DB (optional embeddings / voice / quiz)."""

import json
import logging
import time

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.pipeline import ingest_pdf
from app.ai.rag_context import is_usable_chunk, prepare_chunk_for_storage
from app.ai.vector_store import clear_lesson_index
from app.core.config import get_settings
from app.models.lesson import ContentChunk, Lesson, LessonStatus
from app.models.quiz import QuizQuestion
from app.services.voice_service import DEFAULT_PERSONA

logger = logging.getLogger(__name__)


def _log_stage(lesson_id: int, stage: str, **extra: object) -> None:
    parts = " ".join(f"{k}={v}" for k, v in extra.items())
    suffix = f" {parts}" if parts else ""
    logger.info("[process] lesson_id=%s stage=%s%s", lesson_id, stage, suffix)


async def process_lesson(db: AsyncSession, lesson: Lesson) -> Lesson:
    settings = get_settings()
    lesson_id = lesson.id
    t0 = time.perf_counter()
    _log_stage(
        lesson_id,
        "START",
        marker=settings.USE_MARKER_PDF,
        minimal=settings.PROCESS_MINIMAL_PIPELINE,
        embeddings=settings.process_embeddings_enabled,
        voice=settings.process_voice_persona_enabled,
        quiz=settings.process_quiz_enabled,
    )

    lesson.status = LessonStatus.processing
    lesson.error_message = None
    await db.commit()

    try:
        if not lesson.pdf_path:
            raise ValueError("ملف PDF غير مرفوع")

        clear_lesson_index(lesson_id)

        _log_stage(lesson_id, "MARKER_INGEST_START", pdf=lesson.pdf_path)
        t_ingest = time.perf_counter()
        build_index = (
            lesson_id if settings.process_embeddings_enabled else None
        )
        full_text, text_chunks, page_count, pages_meta = await ingest_pdf(
            lesson.pdf_path,
            lesson_id=build_index,
        )
        _log_stage(
            lesson_id,
            "MARKER_INGEST_DONE",
            elapsed_sec=round(time.perf_counter() - t_ingest, 1),
            text_len=len(full_text),
            chunk_count=len(text_chunks),
            pages=page_count,
        )

        if not full_text.strip():
            raise ValueError("تعذر استخراج نص من PDF — جرّب ملفاً آخر")

        if not text_chunks:
            raise ValueError(
                f"لم يُنشأ أي مقطع من النص (طول النص: {len(full_text)}) — راجع إعدادات CHUNK_SIZE"
            )

        _log_stage(lesson_id, "CHUNK_CLEAN_START", raw_chunks=len(text_chunks))
        cleaned_chunks: list[str] = []
        for raw in text_chunks:
            c = prepare_chunk_for_storage(raw)
            if is_usable_chunk(c):
                cleaned_chunks.append(c)
        _log_stage(
            lesson_id,
            "CHUNK_CLEAN_DONE",
            usable_chunks=len(cleaned_chunks),
        )
        if not cleaned_chunks:
            raise ValueError("كل المقاطع كانت ضوضاء/غلاف PDF — جرّب ملفاً بمحتوى أوضح")
        text_chunks = cleaned_chunks

        lesson.page_count = page_count
        lesson.preview = full_text[:280] + ("…" if len(full_text) > 280 else "")
        if lesson.title == "درس جديد" or not lesson.title:
            lesson.title = _guess_title(full_text, lesson.subject)

        if settings.process_voice_persona_enabled:
            from app.services.voice_service import build_persona_prompt, transcribe_audio

            transcript = ""
            if lesson.voice_path:
                _log_stage(lesson_id, "VOICE_TRANSCRIBE_START", path=lesson.voice_path)
                t_voice = time.perf_counter()
                transcript = await transcribe_audio(lesson.voice_path, lesson_id=lesson_id)
                _log_stage(
                    lesson_id,
                    "VOICE_TRANSCRIBE_DONE",
                    elapsed_sec=round(time.perf_counter() - t_voice, 1),
                    transcript_len=len(transcript),
                )

                _log_stage(lesson_id, "PERSONA_BUILD_START")
                t_persona = time.perf_counter()
                lesson.persona_prompt = await build_persona_prompt(
                    transcript,
                    lesson.subject,
                    lesson.grade,
                    lesson_id=lesson_id,
                )
                _log_stage(
                    lesson_id,
                    "PERSONA_BUILD_DONE",
                    elapsed_sec=round(time.perf_counter() - t_persona, 1),
                    persona_len=len(lesson.persona_prompt or ""),
                )
            else:
                lesson.persona_prompt = DEFAULT_PERSONA
                _log_stage(lesson_id, "PERSONA_SKIP", reason="no_voice_sample")
        else:
            lesson.persona_prompt = DEFAULT_PERSONA
            _log_stage(lesson_id, "VOICE_PERSONA_DISABLED", reason="PROCESS_MINIMAL_PIPELINE")

        _log_stage(lesson_id, "DB_CHUNKS_SAVE_START", chunk_count=len(text_chunks))
        await db.execute(delete(ContentChunk).where(ContentChunk.lesson_id == lesson_id))
        md_path = (pages_meta[0].get("md_path") if pages_meta else None) or None
        for idx, content in enumerate(text_chunks):
            page_hint = pages_meta[min(idx, len(pages_meta) - 1)] if pages_meta else {}
            meta = json.dumps(
                {
                    "page_hint": page_hint,
                    "md_path": md_path,
                    "extract_engine": page_hint.get("engine", "unknown"),
                },
                ensure_ascii=False,
            )
            db.add(
                ContentChunk(
                    lesson_id=lesson_id,
                    chunk_index=idx,
                    content=content,
                    metadata_json=meta,
                )
            )

        await db.flush()

        saved = await db.scalar(
            select(func.count()).select_from(ContentChunk).where(ContentChunk.lesson_id == lesson_id)
        )
        _log_stage(lesson_id, "DB_CHUNKS_SAVE_DONE", saved_chunks=saved)

        if not saved:
            raise ValueError("فشل حفظ مقاطع الدرس في قاعدة البيانات")

        if settings.process_quiz_enabled:
            from app.services.quiz_service import generate_quiz_questions

            _log_stage(lesson_id, "QUIZ_GENERATE_START")
            t_quiz = time.perf_counter()
            await db.execute(delete(QuizQuestion).where(QuizQuestion.lesson_id == lesson_id))
            quiz_items = await generate_quiz_questions(
                full_text,
                lesson.subject,
                lesson.grade,
                lesson_id=lesson_id,
            )
            for i, q in enumerate(quiz_items):
                db.add(
                    QuizQuestion(
                        lesson_id=lesson_id,
                        question=q["question"],
                        options_json=json.dumps(q["options"], ensure_ascii=False),
                        correct_index=q["correct_index"],
                        hint=q.get("hint"),
                        sort_order=i,
                    )
                )
            _log_stage(
                lesson_id,
                "QUIZ_GENERATE_DONE",
                elapsed_sec=round(time.perf_counter() - t_quiz, 1),
                questions=len(quiz_items),
            )
        else:
            await db.execute(delete(QuizQuestion).where(QuizQuestion.lesson_id == lesson_id))
            _log_stage(lesson_id, "QUIZ_DISABLED", reason="PROCESS_MINIMAL_PIPELINE")

        lesson.status = LessonStatus.processed
        lesson.error_message = None
        _log_stage(
            lesson_id,
            "COMPLETE",
            total_sec=round(time.perf_counter() - t0, 1),
            status="processed",
            rag_mode="keyword_db_chunks",
        )
    except Exception as exc:
        logger.exception("[process] lesson_id=%s stage=FAILED: %s", lesson_id, exc)
        lesson.status = LessonStatus.error
        lesson.error_message = str(exc)[:500]
        clear_lesson_index(lesson_id)

    await db.commit()
    await db.refresh(lesson)
    return lesson


def _guess_title(text: str, subject: str) -> str:
    first_line = text.split("\n", 1)[0].strip()[:80]
    if len(first_line) > 10:
        return first_line
    return f"درس {subject}"
