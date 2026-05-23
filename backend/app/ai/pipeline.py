"""Orchestration: document ingest and voice Q&A."""

import logging
import time
from pathlib import Path

from app.ai.chunking import chunk_text
from app.ai.pdf_extract import extract_text_from_document_async
from app.ai.tts import text_to_speech
from app.ai.vector_store import build_lesson_index_async, search_lesson
from app.ai.whisper import transcribe_audio
from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def ingest_pdf(
    pdf_path: str | Path,
    lesson_id: int | None = None,
) -> tuple[str, list[str], int, list[dict]]:
    """
    Extract text, chunk, optionally build FAISS index.
    Returns (full_text, chunks, page_count, pages_meta).
    """
    settings = get_settings()
    t0 = time.perf_counter()

    full_text, page_count, pages_meta, engine, md_path = await extract_text_from_document_async(
        pdf_path
    )
    logger.info(
        "ingest_pdf path=%s engine=%s md_path=%s extracted_text_len=%s extract_sec=%.1f",
        pdf_path,
        engine,
        md_path,
        len(full_text),
        time.perf_counter() - t0,
    )

    from app.ai.rag_context import is_usable_chunk, prepare_chunk_for_storage

    chunks = chunk_text(full_text)
    if not chunks and full_text.strip():
        from app.services.pdf_service import chunk_text as paragraph_chunk

        chunks = paragraph_chunk(full_text)
        logger.info("ingest_pdf paragraph chunking fallback chunk_count=%s", len(chunks))

    chunks = [prepare_chunk_for_storage(c) for c in chunks]
    chunks = [c for c in chunks if is_usable_chunk(c)]
    logger.info(
        "ingest_pdf chunk_count=%s lesson_id=%s engine=%s text_len=%s",
        len(chunks),
        lesson_id,
        engine,
        len(full_text),
    )

    if lesson_id is not None and chunks and settings.process_embeddings_enabled:
        logger.info(
            "[pipeline] lesson_id=%s retrieval/embeddings phase start chunk_count=%s",
            lesson_id,
            len(chunks),
        )
        built = await build_lesson_index_async(lesson_id, chunks)
        logger.info(
            "[pipeline] lesson_id=%s retrieval/embeddings phase end built=%s",
            lesson_id,
            built,
        )

    return full_text, chunks, page_count, pages_meta


async def answer_from_lesson(
    lesson_id: int,
    question: str,
    context_chunks: list[str] | None = None,
    *,
    persona_prompt: str = "",
    subject: str = "",
    grade: str = "",
    top_k: int | None = None,
) -> str:
    settings = get_settings()
    top_k = top_k or settings.RAG_TOP_K

    if context_chunks is None:
        from app.ai.vector_store import has_lesson_index

        if has_lesson_index(lesson_id):
            context_chunks = search_lesson(lesson_id, question, top_k=top_k)
        else:
            context_chunks = []

    if not context_chunks:
        return (
            "عذراً، هذا السؤال خارج محتوى الدرس المرفوع. "
            "راجع ملف PDF أو اسألني عن جزء موجود بالدرس."
        )

    from app.services.ai_service import generate_tutor_reply

    return await generate_tutor_reply(
        question,
        context_chunks,
        persona_prompt,
        subject,
        grade,
    )


async def run_voice_qa_pipeline(
    document_path: str | Path,
    question_audio_path: str | Path,
    speaker_wav_path: str | Path,
    *,
    lesson_id: int | None = None,
    output_audio_path: str | Path | None = None,
) -> dict:
    full_text, chunks, _, _ = await ingest_pdf(document_path, lesson_id=lesson_id)
    question = await transcribe_audio(question_audio_path)
    if not question:
        question = "اشرحلي الدرس"

    ctx = search_lesson(lesson_id, question) if lesson_id else chunks[:3]
    reply = await answer_from_lesson(
        lesson_id or 0,
        question,
        context_chunks=ctx,
    )

    audio_out = ""
    if Path(speaker_wav_path).exists():
        audio_out = await text_to_speech(reply, speaker_wav_path, output_audio_path)

    return {
        "question": question,
        "answer": reply,
        "audio_path": audio_out,
        "chunks_count": len(chunks),
        "text_length": len(full_text),
    }
