"""
Marker PDF extraction via `marker_single` CLI.

Returns markdown for chunking/RAG. Blocking — call from a worker thread only.
"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _marker_executable() -> str:
    """Resolve marker_single from the active venv or PATH."""
    name = "marker_single.exe" if sys.platform == "win32" else "marker_single"
    venv_bin = Path(sys.executable).resolve().parent / name
    if venv_bin.is_file():
        return str(venv_bin)
    found = shutil.which("marker_single")
    if found:
        return found
    raise FileNotFoundError(
        "marker_single not found. Install with: pip install marker-pdf"
    )


def _find_markdown_file(output_dir: Path, pdf_stem: str) -> Path | None:
    """Locate .md produced by marker_single (layout may vary slightly)."""
    candidates = [
        output_dir / pdf_stem / f"{pdf_stem}.md",
        output_dir / f"{pdf_stem}.md",
    ]
    for path in candidates:
        if path.is_file():
            return path
    for path in output_dir.rglob("*.md"):
        if path.is_file():
            return path
    return None


def _page_count_from_pdf(pdf_path: Path) -> int:
    try:
        import fitz

        doc = fitz.open(pdf_path)
        n = len(doc)
        doc.close()
        return max(1, n)
    except Exception:
        return 1


def extract_pdf_with_marker(
    pdf_path: str | Path,
    output_dir: str | Path | None = None,
) -> str:
    """
    Run marker_single and return extracted markdown text.
    Raises if Marker fails or produces no markdown file.
    """
    text, _, _, _ = extract_pdf_with_marker_document(pdf_path, output_dir=output_dir)
    return text


def extract_pdf_with_marker_document(
    pdf_path: str | Path,
    output_dir: str | Path | None = None,
) -> tuple[str, int, list[dict], str]:
    """
    Full extraction result for the lesson pipeline.

    Returns:
        (markdown_text, page_count, pages_meta, markdown_path)
    """
    settings = get_settings()
    path = Path(pdf_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")

    pdf_stem = path.stem
    t0 = time.perf_counter()
    logger.info("Marker: start file=%s", path.name)

    work_dir = Path(output_dir) if output_dir else Path(tempfile.mkdtemp(prefix="eduspark_marker_"))
    work_dir.mkdir(parents=True, exist_ok=True)

    marker_bin = _marker_executable()
    command = [
        marker_bin,
        str(path),
        "--output_dir",
        str(work_dir),
    ]
    logger.info("Marker: running marker_single output_dir=%s", work_dir)

    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()[:2000]
            stdout = (result.stdout or "").strip()[:500]
            raise RuntimeError(
                f"marker_single exited {result.returncode}: {stderr or stdout or 'no output'}"
            )
    except subprocess.SubprocessError as exc:
        raise RuntimeError(f"marker_single failed: {exc}") from exc

    md_path = _find_markdown_file(work_dir, pdf_stem)
    if not md_path:
        raise FileNotFoundError(
            f"Marker did not produce markdown under {work_dir} for {path.name}"
        )

    text = md_path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        raise ValueError(f"Marker markdown is empty: {md_path}")

    persisted_path = md_path
    if settings.MARKER_PERSIST_MD:
        dest = path.with_suffix(".md")
        try:
            shutil.copy2(md_path, dest)
            persisted_path = dest
            logger.info("Marker: saved markdown copy path=%s", dest)
        except OSError as exc:
            logger.warning("Marker: could not copy md to %s: %s", dest, exc)

    page_count = _page_count_from_pdf(path)
    pages_meta: list[dict] = [
        {
            "page": 1,
            "chars": len(text),
            "engine": "marker",
            "md_path": str(persisted_path.resolve()),
        }
    ]
    for i in range(1, min(page_count, 50)):
        pages_meta.append({"page": i + 1, "chars": 0, "engine": "marker"})

    elapsed = time.perf_counter() - t0
    logger.info(
        "Marker: done file=%s md_path=%s chars=%s pages=%s duration=%.1fs",
        path.name,
        persisted_path,
        len(text),
        page_count,
        elapsed,
    )
    return text, page_count, pages_meta, str(persisted_path.resolve())
