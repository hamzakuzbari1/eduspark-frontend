"""PDF extraction: Marker markdown (primary) or PyMuPDF fallback."""

from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Literal

from app.ai.marker_extract import extract_pdf_with_marker_document
from app.core.config import get_settings

logger = logging.getLogger(__name__)

Engine = Literal["marker", "pymupdf", "pymupdf_fallback"]

_executor: ThreadPoolExecutor | None = None
_marker_semaphore: asyncio.Semaphore | None = None


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        settings = get_settings()
        workers = max(1, settings.MARKER_THREAD_WORKERS)
        _executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="pdf_extract")
    return _executor


def _get_marker_semaphore() -> asyncio.Semaphore:
    global _marker_semaphore
    if _marker_semaphore is None:
        _marker_semaphore = asyncio.Semaphore(1)
    return _marker_semaphore


def _extract_with_pymupdf(file_path: Path) -> tuple[str, int, list[dict], str | None]:
    from app.services.pdf_service import extract_text_from_pdf

    t0 = time.perf_counter()
    text, pages, meta = extract_text_from_pdf(file_path)
    logger.info(
        "PyMuPDF: done file=%s chars=%s duration=%.1fs",
        file_path.name,
        len(text),
        time.perf_counter() - t0,
    )
    return text, pages, meta, None


def _extract_job_with_fallback(
    file_path: Path,
) -> tuple[str, int, list[dict], Engine, str | None]:
    """
    Runs in thread pool. Marker markdown first; PyMuPDF only if Marker fails completely.
    """
    settings = get_settings()
    path = Path(file_path)

    if not settings.use_marker_pdf:
        text, pages, meta, _ = _extract_with_pymupdf(path)
        return text, pages, meta, "pymupdf", None

    try:
        text, pages, meta, md_path = extract_pdf_with_marker_document(path)
        if text.strip():
            return text, pages, meta, "marker", md_path
        logger.warning("Marker returned empty text for %s", path.name)
    except Exception as exc:
        logger.exception("Marker failed for %s: %s", path.name, exc)

    text, pages, meta, _ = _extract_with_pymupdf(path)
    return text, pages, meta, "pymupdf_fallback", None


async def extract_text_from_document_async(
    file_path: str | Path,
) -> tuple[str, int, list[dict], Engine, str | None]:
    """
    Non-blocking for the FastAPI event loop.
    Marker runs in a thread with timeout; PyMuPDF only when Marker fails.
    """
    path = Path(file_path)
    settings = get_settings()
    loop = asyncio.get_running_loop()

    if not settings.use_marker_pdf:
        text, pages, meta, _ = await asyncio.to_thread(_extract_with_pymupdf, path)
        return text, pages, meta, "pymupdf", None

    timeout = settings.MARKER_TIMEOUT_SECONDS
    logger.info(
        "PDF extract: Marker enabled path=%s timeout=%ss (thread pool)",
        path.name,
        timeout,
    )

    async with _get_marker_semaphore():
        t0 = time.perf_counter()
        try:
            text, pages, meta, engine, md_path = await asyncio.wait_for(
                loop.run_in_executor(_get_executor(), _extract_job_with_fallback, path),
                timeout=timeout,
            )
            logger.info(
                "[pipeline] Marker extract complete engine=%s md_path=%s chars=%s duration=%.1fs",
                engine,
                md_path,
                len(text),
                time.perf_counter() - t0,
            )
            return text, pages, meta, engine, md_path
        except asyncio.TimeoutError:
            logger.error(
                "PDF extract: Marker exceeded %ss for %s — PyMuPDF fallback",
                timeout,
                path.name,
            )
            text, pages, meta, _ = await asyncio.to_thread(_extract_with_pymupdf, path)
            return text, pages, meta, "pymupdf_fallback", None


def extract_text_from_document(file_path: str | Path) -> tuple[str, int, list[dict]]:
    """Sync API for scripts/tests."""
    path = Path(file_path)
    text, pages, meta, _, _ = _extract_job_with_fallback(path)
    return text, pages, meta
