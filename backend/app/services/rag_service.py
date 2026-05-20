"""Retrieve relevant lesson chunks (keyword search; optional vectors when enabled)."""

import logging
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.lesson import ContentChunk

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[\w\u0600-\u06FF]+", text.lower())
    return {t for t in tokens if len(t) > 1}


def _keyword_score(query: str, content: str) -> float:
    q_tokens = _tokenize(query)
    if not q_tokens:
        return 0.0
    c_lower = content.lower()
    hits = sum(1 for t in q_tokens if t in c_lower)
    return hits / len(q_tokens)


async def retrieve_chunks(
    db: AsyncSession,
    lesson_id: int,
    query: str,
    top_k: int = 5,
) -> list[str]:
    settings = get_settings()
    top_k = top_k or settings.RAG_TOP_K

    result = await db.execute(
        select(ContentChunk)
        .where(ContentChunk.lesson_id == lesson_id)
        .order_by(ContentChunk.chunk_index)
    )
    chunks = result.scalars().all()
    if not chunks:
        return []

    # Vector search path only when pgvector + embeddings are enabled (future)
    if settings.ENABLE_PGVECTOR and settings.ENABLE_EMBEDDINGS:
        try:
            return await _retrieve_chunks_vector(db, lesson_id, query, chunks, top_k)
        except Exception as exc:
            logger.warning("Vector retrieval failed, using keywords: %s", exc)

    scored = [( _keyword_score(query, ch.content), ch.content) for ch in chunks]
    scored.sort(key=lambda x: x[0], reverse=True)
    if scored[0][0] > 0:
        return [text for _, text in scored[:top_k]]

    return [ch.content for ch in chunks[:top_k]]


async def _retrieve_chunks_vector(
    db: AsyncSession,
    lesson_id: int,
    query: str,
    chunks: list[ContentChunk],
    top_k: int,
) -> list[str]:
    """Placeholder for when pgvector is re-enabled."""
    del db, lesson_id, query, chunks, top_k
    return []


async def get_lesson_context_text(db: AsyncSession, lesson_id: int, max_chars: int = 12000) -> str:
    result = await db.execute(
        select(ContentChunk)
        .where(ContentChunk.lesson_id == lesson_id)
        .order_by(ContentChunk.chunk_index)
    )
    parts = [c.content for c in result.scalars().all()]
    text = "\n\n".join(parts)
    return text[:max_chars]
