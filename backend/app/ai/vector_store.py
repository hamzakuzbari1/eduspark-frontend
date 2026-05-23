"""Registry of per-lesson FAISS indexes."""

import logging

from app.ai.async_jobs import run_sync_with_timeout
from app.ai.embeddings import LessonVectorStore, is_local_embeddings_available
from app.core.config import get_settings

logger = logging.getLogger(__name__)

_indexes: dict[int, LessonVectorStore] = {}


def build_lesson_index(lesson_id: int, chunks: list[str]) -> bool:
    """Sync build — prefer build_lesson_index_async from async code."""
    if not is_local_embeddings_available() or not chunks:
        return False
    store = LessonVectorStore()
    store.build(chunks)
    _indexes[lesson_id] = store
    logger.info("[retrieval] lesson_id=%s index registered chunks=%s", lesson_id, len(chunks))
    return True


async def build_lesson_index_async(lesson_id: int, chunks: list[str]) -> bool:
    """Non-blocking index build with timeout (does not block FastAPI event loop)."""
    settings = get_settings()
    if not is_local_embeddings_available() or not chunks:
        logger.info(
            "[retrieval] lesson_id=%s skip embeddings (enabled=%s chunks=%s)",
            lesson_id,
            settings.USE_LOCAL_EMBEDDINGS,
            len(chunks),
        )
        return False

    logger.info("[retrieval] lesson_id=%s FAISS init start chunk_count=%s", lesson_id, len(chunks))

    def _build() -> bool:
        store = LessonVectorStore()
        store.build(chunks)
        _indexes[lesson_id] = store
        return True

    try:
        ok = await run_sync_with_timeout(
            _build,
            timeout=float(settings.EMBEDDING_BUILD_TIMEOUT_SECONDS),
            label="EMBEDDING_INDEX_BUILD",
            lesson_id=lesson_id,
            default=False,
        )
        if ok:
            logger.info("[retrieval] lesson_id=%s FAISS init complete", lesson_id)
        else:
            logger.warning(
                "[retrieval] lesson_id=%s FAISS init skipped — keyword RAG will be used",
                lesson_id,
            )
        return bool(ok)
    except Exception:
        logger.warning(
            "[retrieval] lesson_id=%s FAISS init failed — keyword RAG will be used",
            lesson_id,
        )
        return False


def search_lesson(lesson_id: int, query: str, top_k: int = 5) -> list[str]:
    store = _indexes.get(lesson_id)
    if not store:
        return []
    return store.search(query, top_k=top_k)


def clear_lesson_index(lesson_id: int) -> None:
    _indexes.pop(lesson_id, None)


def has_lesson_index(lesson_id: int) -> bool:
    return lesson_id in _indexes
