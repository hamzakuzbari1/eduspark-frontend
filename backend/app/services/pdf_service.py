"""PDF text extraction with PyMuPDF and optional Arabic OCR."""

import logging
import re
from pathlib import Path

import fitz  # PyMuPDF

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def extract_text_from_pdf(pdf_path: str | Path) -> tuple[str, int, list[dict]]:
    """
    Returns (full_text, page_count, metadata_list per page).
    Uses OCR when a page has little extractable text.
    """
    path = Path(pdf_path)
    doc = fitz.open(path)
    pages_meta: list[dict] = []
    parts: list[str] = []

    for i, page in enumerate(doc):
        text = page.get_text("text") or ""
        text = _normalize_arabic_text(text)
        if len(text.strip()) < 40:
            text = _ocr_page(page) or text
        pages_meta.append({"page": i + 1, "chars": len(text)})
        if text.strip():
            parts.append(f"[صفحة {i + 1}]\n{text}")

    doc.close()
    full = "\n\n".join(parts).strip()
    return full, len(pages_meta), pages_meta


def _normalize_arabic_text(text: str) -> str:
    from app.ai.text_normalize import normalize_arabic_educational_text

    return normalize_arabic_educational_text(re.sub(r"[ \t]+", " ", text))


def _ocr_page(page: fitz.Page) -> str:
    try:
        import pytesseract
        from PIL import Image
        import io

        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(img, lang="ara+eng") or ""
    except Exception as exc:
        logger.debug("OCR skipped for page: %s", exc)
        return ""


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP
    if not text:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}".strip() if current else para
        else:
            if current:
                chunks.append(current)
            if len(para) <= chunk_size:
                current = para
            else:
                # Split long paragraph by sentences
                sentences = re.split(r"(?<=[.!?؟。])\s+", para)
                current = ""
                for sent in sentences:
                    if len(current) + len(sent) + 1 <= chunk_size:
                        current = f"{current} {sent}".strip()
                    else:
                        if current:
                            chunks.append(current)
                        current = sent
                if current:
                    chunks.append(current)
                current = ""

    if current:
        chunks.append(current)

    # Apply overlap by prepending tail of previous chunk
    if overlap > 0 and len(chunks) > 1:
        overlapped: list[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-overlap:]
            overlapped.append(f"{prev_tail}\n{chunks[i]}".strip())
        chunks = overlapped

    return chunks
