"""Embedding generation — disabled unless ENABLE_EMBEDDINGS=true and pgvector is available."""

import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def embed_text(text: str) -> list[float]:
    """No-op when embeddings are disabled (default for local dev without pgvector)."""
    if not settings.ENABLE_EMBEDDINGS:
        return []

    # Reserved for future pgvector-enabled deployments
    logger.warning("ENABLE_EMBEDDINGS is on but vector storage is not configured in this build")
    return []
