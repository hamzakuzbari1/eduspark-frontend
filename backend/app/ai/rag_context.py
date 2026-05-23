"""Clean, score, and format PDF chunks for RAG (never send raw/noisy text to the LLM)."""

import re

# Page / PDF markers
_PAGE_MARKERS = re.compile(r"\[صفحة\s*\d+\]", re.I)
# Markdown
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]+\)")
_MD_HEADERS = re.compile(r"^#{1,6}\s+", re.M)
_MD_BOLD_ITALIC = re.compile(r"(\*\*|__|\*|_)(.*?)\1")
_MD_CODE = re.compile(r"`([^`]*)`")
# Prompt / system leakage
_PROMPT_LEAK = re.compile(
    r"(?i)(مصادر الدرس|محتوى تعليمي|سؤال الطالب|اكتب شرحك|مهمتك:|قواعد إلزامية)",
)
# Cover-page / form metadata (common in internship PDFs)
_FORM_NOISE = re.compile(
    r"(?i)\b("
    r"internship\s*report|student\s*name|student\s*id|university\s*mentor|"
    r"start\s*&\s*end\s*date|table\s*of\s*contents|page\s*\d+\s*of\s*\d+|"
    r"tp\d{6,}|report\s*part\s*\d+"
    r")\b",
)
# Lines that are mostly labels (STUDENT NAME: foo)
_LABEL_LINE = re.compile(
    r"(?i)^[\s\d\-•●]*("
    r"student|internship|university|mentor|date|id|name|grade|subject"
    r")\s*[:：]",
)


def clean_chunk_text(text: str) -> str:
    """Normalize chunk: strip markdown, noise, duplicate whitespace."""
    if not text:
        return ""

    t = text.replace("\f", " ").replace("\r\n", "\n").replace("\r", "\n")
    t = _PAGE_MARKERS.sub(" ", t)
    t = _MD_LINK.sub(r"\1", t)
    t = _MD_HEADERS.sub("", t)
    t = _MD_BOLD_ITALIC.sub(r"\2", t)
    t = _MD_CODE.sub(r"\1", t)
    t = _PROMPT_LEAK.sub(" ", t)

    lines: list[str] = []
    for line in t.split("\n"):
        line = line.strip()
        if not line:
            continue
        if _LABEL_LINE.match(line) and len(line) < 120:
            continue
        lines.append(line)

    t = " ".join(lines) if lines else t
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def prepare_chunk_for_storage(text: str) -> str:
    """Clean before saving to ContentChunk."""
    return clean_chunk_text(text)


def is_usable_chunk(text: str, *, min_chars: int = 80, min_words: int = 12) -> bool:
    """Drop cover pages, empty lines, and metadata-only fragments."""
    clean = clean_chunk_text(text)
    if len(clean) < min_chars:
        return False

    words = re.findall(r"[\w\u0600-\u06FF]+", clean)
    if len(words) < min_words:
        return False

    # Mostly form labels / headers
    noise_hits = len(_FORM_NOISE.findall(clean))
    if noise_hits >= 3 and len(words) < 60:
        return False

    letters = [c for c in clean if c.isalpha()]
    if not letters:
        return False
    upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    if upper_ratio > 0.45 and len(words) < 50:
        return False

    return True


def chunk_quality_score(text: str) -> float:
    """Higher = more substantive body text (use when ranking)."""
    clean = clean_chunk_text(text)
    if not clean:
        return 0.0
    words = re.findall(r"[\w\u0600-\u06FF]+", clean)
    score = min(1.0, len(words) / 80)
    score -= 0.15 * len(_FORM_NOISE.findall(clean))
    letters = [c for c in clean if c.isalpha()]
    if letters:
        upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        if upper_ratio > 0.4:
            score *= 0.5
    return max(0.0, score)


def truncate_chunk(text: str, max_chars: int) -> str:
    clean = clean_chunk_text(text)
    if not clean:
        return ""
    if len(clean) <= max_chars:
        return clean
    cut = clean[:max_chars]
    last_space = cut.rfind(" ")
    if last_space > max_chars // 2:
        cut = cut[:last_space]
    return cut.rstrip() + "…"


def dedupe_chunks(chunks: list[str], *, prefix_len: int = 100) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in chunks:
        clean = clean_chunk_text(raw)
        if not clean:
            continue
        key = clean[:prefix_len].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(clean)
    return out


def format_chunks_for_prompt(
    chunks: list[str],
    *,
    max_per_chunk: int = 500,
    max_total: int = 1500,
) -> str:
    """Compact lesson excerpts for the model (no «مصدر» markers)."""
    if not chunks:
        return ""

    parts: list[str] = []
    total = 0
    for i, raw in enumerate(chunks, start=1):
        excerpt = truncate_chunk(raw, max_per_chunk)
        if not excerpt or len(excerpt) < 40:
            continue
        block = f"[{i}] {excerpt}"
        if total + len(block) > max_total:
            break
        parts.append(block)
        total += len(block) + 2

    return "\n".join(parts)


def tokenize_query(text: str) -> set[str]:
    tokens = re.findall(r"[\w\u0600-\u06FF]{2,}", text.lower())
    return {t for t in tokens if len(t) > 1}


def score_chunk_relevance(query: str, content: str) -> float:
    """Relevance of cleaned chunk to student question."""
    q_tokens = tokenize_query(query)
    if not q_tokens:
        return 0.0

    clean = clean_chunk_text(content).lower()
    if not clean or not is_usable_chunk(content, min_chars=40, min_words=5):
        return 0.0

    c_tokens = tokenize_query(clean)
    if not c_tokens:
        return 0.0

    overlap = len(q_tokens & c_tokens) / len(q_tokens)

    phrase_boost = 0.0
    q_norm = query.strip().lower()
    if len(q_norm) >= 6 and q_norm in clean:
        phrase_boost = 0.3

    quality = chunk_quality_score(content) * 0.2
    noise_penalty = 0.1 * min(3, len(_FORM_NOISE.findall(clean)))

    return min(1.0, max(0.0, overlap + phrase_boost + quality - noise_penalty))
