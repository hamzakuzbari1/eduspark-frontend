"""Semantic + keyword retrieval scoped strictly by lesson_id."""

import logging
from dataclasses import dataclass, field

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.rag_context import (
    chunk_quality_score,
    dedupe_chunks,
    format_chunks_for_prompt,
    is_usable_chunk,
    prepare_chunk_for_storage,
    score_chunk_relevance,
    truncate_chunk,
)
from app.ai.vector_store import build_lesson_index_async, has_lesson_index, search_lesson
from app.core.config import get_settings
from app.models.lesson import ContentChunk, Lesson

logger = logging.getLogger(__name__)

_BROAD_MARKERS = (
    "اشرح",
    "شرح",
    "لخص",
    "ملخص",
    "ما هو",
    "ما هي",
    "عن ماذا",
    "ماذا",
    "وضح",
    "فهمني",
    "شو",
    "درس",
    "explain",
    "summary",
    "about",
)


@dataclass
class RetrievalResult:
    chunks: list[str]
    lesson_id: int
    total_in_db: int = 0
    usable_in_db: int = 0
    strategy: str = ""
    top_scores: list[dict] = field(default_factory=list)
    query: str = ""
    chunk_previews: list[str] = field(default_factory=list)
    context_char_count: int = 0


def is_broad_question(query: str) -> bool:
    q = query.strip().lower()
    if not q:
        return True
    return any(m in q for m in _BROAD_MARKERS) or len(q.split()) <= 2


async def retrieve_chunks(
    db: AsyncSession,
    lesson_id: int,
    query: str,
    top_k: int | None = None,
) -> list[str]:
    return (await retrieve_chunks_detailed(db, lesson_id, query, top_k=top_k)).chunks


async def _load_db_chunks(db: AsyncSession, lesson_id: int) -> list[ContentChunk]:
    lesson_id = int(lesson_id)
    result = await db.execute(
        select(ContentChunk)
        .where(ContentChunk.lesson_id == lesson_id)
        .order_by(ContentChunk.chunk_index)
    )
    return list(result.scalars().all())


def _rows_to_clean_texts(rows: list[ContentChunk]) -> list[tuple[int, str]]:
    """(chunk_index, cleaned_text) for usable chunks only."""
    out: list[tuple[int, str]] = []
    for ch in rows:
        raw = ch.content or ""
        cleaned = prepare_chunk_for_storage(raw)
        if is_usable_chunk(cleaned):
            out.append((ch.chunk_index, cleaned))
    return out


async def _ensure_semantic_index(lesson_id: int, cleaned_texts: list[str]) -> bool:
    settings = get_settings()
    if not settings.process_embeddings_enabled or not cleaned_texts:
        return False
    if has_lesson_index(lesson_id):
        return True
    built = await build_lesson_index_async(lesson_id, cleaned_texts)
    if built:
        logger.info("[retrieval] lesson_id=%s rebuilt FAISS index (%s chunks)", lesson_id, len(cleaned_texts))
    return built


def _apply_context_budget(chunks: list[str], top_k: int) -> list[str]:
    settings = get_settings()
    max_total = settings.RAG_MAX_CONTEXT_CHARS
    max_per = settings.RAG_MAX_CHUNK_CHARS
    per = max(200, max_total // max(top_k, 1))

    out: list[str] = []
    used = 0
    for raw in dedupe_chunks(chunks)[:top_k]:
        piece = truncate_chunk(raw, min(max_per, per))
        if not piece or len(piece) < 40:
            continue
        if used + len(piece) > max_total:
            break
        out.append(piece)
        used += len(piece)
    return out


async def retrieve_chunks_detailed(
    db: AsyncSession,
    lesson_id: int,
    query: str,
    top_k: int | None = None,
) -> RetrievalResult:
    settings = get_settings()
    top_k = min(top_k or settings.RAG_TOP_K, 3)
    min_score = settings.RAG_MIN_SCORE
    lesson_id = int(lesson_id)
    force_n = settings.RAG_FORCE_TOP_K

    out = RetrievalResult(chunks=[], lesson_id=lesson_id, query=query)
    rows = await _load_db_chunks(db, lesson_id)
    out.total_in_db = len(rows)

    usable = _rows_to_clean_texts(rows)
    out.usable_in_db = len(usable)
    cleaned_only = [t for _, t in usable]

    logger.info(
        "RAG lesson_id=%s query=%r db_chunks=%s usable_chunks=%s force_top_k=%s",
        lesson_id,
        (query or "")[:80],
        out.total_in_db,
        out.usable_in_db,
        force_n,
    )

    if not rows:
        out.strategy = "empty_db"
        return out

    if not usable:
        out.strategy = "no_usable_chunks"
        logger.warning("lesson_id=%s: chunks exist but all filtered as noise", lesson_id)
        return out

    # Debug-only: force first N (skips semantic) — keep off in .env for quality
    if force_n > 0:
        selected = _apply_context_budget(cleaned_only[:force_n], force_n)
        out.chunks = selected
        out.strategy = "force_top_k"
        _finish_result(out, query)
        return out

    await _ensure_semantic_index(lesson_id, cleaned_only)

    # 1) Semantic similarity (same lesson_id index only)
    if has_lesson_index(lesson_id):
        hits = search_lesson(lesson_id, query, top_k=top_k + 2)
        hits = [h for h in hits if is_usable_chunk(h)]
        hits = dedupe_chunks(hits)
        if hits:
            out.chunks = _apply_context_budget(hits, top_k)
            out.strategy = "semantic_faiss"
            _finish_result(out, query)
            return out

    # 2) Keyword relevance on cleaned text
    scored: list[tuple[float, str, int]] = []
    for idx, text in usable:
        sc = score_chunk_relevance(query, text)
        scored.append((sc, text, idx))
    scored.sort(key=lambda x: x[0], reverse=True)

    out.top_scores = [
        {"index": i, "score": round(sc, 3), "preview": txt[:100]}
        for sc, txt, i in scored[:6]
    ]

    picked: list[str] = []
    for sc, text, _ in scored:
        if sc >= min_score:
            picked.append(text)
        if len(picked) >= top_k:
            break

    if len(picked) < top_k and scored and scored[0][0] > 0:
        for sc, text, _ in scored:
            if text not in picked:
                picked.append(text)
            if len(picked) >= top_k:
                break
        out.strategy = "keyword_weak"
    elif picked:
        out.strategy = "keyword_match"
    elif is_broad_question(query):
        ranked = sorted(usable, key=lambda x: chunk_quality_score(x[1]), reverse=True)
        picked = [t for _, t in ranked[:top_k]]
        out.strategy = "broad_substantive"
    else:
        ranked = sorted(usable, key=lambda x: chunk_quality_score(x[1]), reverse=True)
        picked = [t for _, t in ranked[:top_k]]
        out.strategy = "substantive_fallback"

    out.chunks = _apply_context_budget(dedupe_chunks(picked), top_k)
    _finish_result(out, query)
    return out


def _finish_result(out: RetrievalResult, query: str) -> None:
    settings = get_settings()
    out.chunk_previews = [c[:120] for c in out.chunks]
    out.context_char_count = len(format_chunks_for_prompt(out.chunks))
    logger.info(
        "RAG RESULT lesson_id=%s strategy=%s selected=%s context_chars=%s query=%r",
        out.lesson_id,
        out.strategy,
        len(out.chunks),
        out.context_char_count,
        (query or "")[:50],
    )
    for i, prev in enumerate(out.chunk_previews):
        logger.info("  chunk[%s] preview=%r", i, prev)
    if settings.RAG_LOG_LLM_PROMPT and out.chunks:
        logger.info("  context_block_preview=%r", format_chunks_for_prompt(out.chunks)[:800])


async def get_lesson_rag_debug(
    db: AsyncSession,
    lesson_id: int,
    sample_query: str = "اشرح الدرس",
) -> dict:
    lesson_id = int(lesson_id)
    settings = get_settings()
    lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one_or_none()
    rows = await _load_db_chunks(db, lesson_id)
    usable = _rows_to_clean_texts(rows)
    retrieval = await retrieve_chunks_detailed(db, lesson_id, sample_query)

    return {
        "lesson_id": lesson_id,
        "lesson_found": lesson is not None,
        "status": lesson.status.value if lesson else None,
        "title": lesson.title if lesson else None,
        "pdf_path": lesson.pdf_path if lesson else None,
        "chunk_count_in_db": len(rows),
        "usable_chunk_count": len(usable),
        "has_faiss_index": has_lesson_index(lesson_id),
        "use_local_embeddings": settings.USE_LOCAL_EMBEDDINGS,
        "rag_force_top_k": settings.RAG_FORCE_TOP_K,
        "sample_query": sample_query,
        "retrieval_strategy": retrieval.strategy,
        "retrieval_selected_count": len(retrieval.chunks),
        "context_char_count": retrieval.context_char_count,
        "retrieval_top_scores": retrieval.top_scores,
        "retrieval_chunk_previews": retrieval.chunk_previews,
        "cleaned_samples": [{"index": i, "preview": t[:180]} for i, t in usable[:5]],
    }


async def get_lesson_context_text(db: AsyncSession, lesson_id: int, max_chars: int = 12000) -> str:
    rows = await _load_db_chunks(db, int(lesson_id))
    parts = [prepare_chunk_for_storage(r.content or "") for r in rows]
    parts = [p for p in parts if p]
    return "\n\n".join(parts)[:max_chars]
