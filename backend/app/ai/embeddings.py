"""Optional BGE-M3 + FAISS vector search per lesson."""

import logging
import time
from typing import TYPE_CHECKING

import numpy as np

from app.core.config import get_settings

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import faiss
    from sentence_transformers import SentenceTransformer

_embedder: "SentenceTransformer | None" = None
_embedder_loading = False


def _get_embedder():
    global _embedder, _embedder_loading
    settings = get_settings()
    if _embedder is not None:
        return _embedder
    if _embedder_loading:
        raise RuntimeError("Embedding model is already loading on another thread")

    from sentence_transformers import SentenceTransformer

    _embedder_loading = True
    t0 = time.perf_counter()
    logger.info("[embeddings] loading model=%s (first use)", settings.EMBEDDING_MODEL)
    try:
        _embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("[embeddings] model ready in %.1fs", time.perf_counter() - t0)
        return _embedder
    finally:
        _embedder_loading = False


class LessonVectorStore:
    """In-memory FAISS index for one lesson's chunks."""

    def __init__(self) -> None:
        self.chunks: list[str] = []
        self._index = None

    def build(self, chunks: list[str]) -> None:
        import faiss

        if not chunks:
            self.chunks = []
            self._index = None
            logger.info("[embeddings] build skipped (no chunks)")
            return

        t0 = time.perf_counter()
        logger.info("[embeddings] encode start chunk_count=%s", len(chunks))
        embedder = _get_embedder()
        embeddings = embedder.encode(chunks, show_progress_bar=False, normalize_embeddings=True)
        logger.info(
            "[embeddings] encode done vectors=%s duration=%.1fs",
            len(chunks),
            time.perf_counter() - t0,
        )

        t1 = time.perf_counter()
        vectors = np.array(embeddings, dtype="float32")
        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(vectors)
        self.chunks = chunks
        self._index = index
        logger.info(
            "[embeddings] FAISS index built chunks=%s dim=%s duration=%.1fs",
            len(chunks),
            dim,
            time.perf_counter() - t1,
        )

    def search(self, query: str, top_k: int = 5) -> list[str]:
        if not self._index or not self.chunks:
            return []
        import faiss

        embedder = _get_embedder()
        query_vec = embedder.encode([query], normalize_embeddings=True)
        query_vec = np.array(query_vec, dtype="float32")
        k = min(top_k, len(self.chunks))
        _, indices = self._index.search(query_vec, k)
        return [self.chunks[i] for i in indices[0] if 0 <= i < len(self.chunks)]


def is_local_embeddings_available() -> bool:
    settings = get_settings()
    if not settings.USE_LOCAL_EMBEDDINGS:
        return False
    try:
        import faiss  # noqa: F401
        import sentence_transformers  # noqa: F401

        return True
    except ImportError:
        return False
