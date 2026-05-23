"""Run blocking AI work off the event loop with timeouts and stage logs."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def run_sync_with_timeout(
    fn: Callable[..., T],
    *args,
    timeout: float,
    label: str,
    lesson_id: int | None = None,
    default: T | None = None,
) -> T:
    """
    Execute blocking callable in a thread. On timeout, return `default` if set, else raise.
    """
    lid = f" lesson_id={lesson_id}" if lesson_id is not None else ""
    t0 = time.perf_counter()
    logger.info("[pipeline]%s %s: start (timeout=%ss)", lid, label, timeout)
    try:
        result = await asyncio.wait_for(asyncio.to_thread(fn, *args), timeout=timeout)
        logger.info(
            "[pipeline]%s %s: done duration=%.1fs",
            lid,
            label,
            time.perf_counter() - t0,
        )
        return result
    except asyncio.TimeoutError:
        logger.error(
            "[pipeline]%s %s: TIMEOUT after %.1fs (limit=%ss)",
            lid,
            label,
            time.perf_counter() - t0,
            timeout,
        )
        if default is not None:
            logger.warning("[pipeline]%s %s: using fallback default", lid, label)
            return default
        raise
    except Exception as exc:
        logger.exception(
            "[pipeline]%s %s: failed after %.1fs: %s",
            lid,
            label,
            time.perf_counter() - t0,
            exc,
        )
        if default is not None:
            return default
        raise
