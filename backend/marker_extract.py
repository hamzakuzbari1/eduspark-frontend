#!/usr/bin/env python3
"""CLI: run Marker on a PDF (uses app.ai.marker_extract)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.ai.marker_extract import extract_pdf_with_marker_document  # noqa: E402


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python marker_extract.py <file.pdf>")
        sys.exit(1)
    text, pages, meta, md_path = extract_pdf_with_marker_document(sys.argv[1])
    print(f"pages={pages} chars={len(text)} md={md_path}")
    print(text[:3000])


if __name__ == "__main__":
    main()
