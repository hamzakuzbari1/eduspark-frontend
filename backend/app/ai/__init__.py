"""Modular AI pipeline (PDF → RAG → LLM → voice). Heavy deps are optional."""

from app.ai.chunking import chunk_text
from app.ai.llm import build_rag_prompt, generate_answer
from app.ai.pipeline import ingest_pdf, run_voice_qa_pipeline
from app.ai.pdf_extract import extract_text_from_document

__all__ = [
    "chunk_text",
    "extract_text_from_document",
    "ingest_pdf",
    "build_rag_prompt",
    "generate_answer",
    "run_voice_qa_pipeline",
]
