"""Arabic / markdown text normalization for PDF chunks and RAG."""

from __future__ import annotations

import re
import unicodedata

_TATWEEL = "\u0640"
_ZW_CHARS = re.compile(r"[\u200b-\u200f\u202a-\u202e\ufeff]")
_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_MULTI_NL = re.compile(r"\n{3,}")


def normalize_arabic_educational_text(text: str) -> str:
    """Normalize extracted text for Syrian Arabic / educational RAG chunking."""
    if not text:
        return ""
    t = unicodedata.normalize("NFC", text)
    t = t.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")
    t = t.replace(_TATWEEL, "")
    t = _ZW_CHARS.sub("", t)
    t = _MULTI_NL.sub("\n\n", t)
    t = _MULTI_SPACE.sub(" ", t)
    lines = [ln.strip() for ln in t.split("\n")]
    return "\n".join(ln for ln in lines if ln).strip()
