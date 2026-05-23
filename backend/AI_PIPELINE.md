# AI Pipeline

Active stack: **Marker PDF** → chunks → PostgreSQL → **keyword / FAISS RAG** → **Ollama (qwen2.5)**.

## Architecture

```
PDF upload → marker_single → markdown → chunk → ContentChunk (DB)
                              └→ FAISS (optional, when PROCESS_MINIMAL_PIPELINE=false)

Chat → retrieve_chunks() → generate_tutor_reply() → Ollama (primary) or Gemini (fallback)
```

## Environment

See root `.env.example`. Key flags:

| Variable | Typical value |
|----------|----------------|
| `USE_MARKER_PDF` | `true` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` |
| `OLLAMA_MODEL` | `qwen2.5` |
| `PROCESS_MINIMAL_PIPELINE` | `true` while debugging; `false` for full pipeline |
| `RAG_FORCE_TOP_K` | `0` |
| `ENABLE_EMBEDDINGS` | `false` unless BGE-M3 + FAISS installed |

Install optional deps: `pip install -r backend/requirements-ai.txt`

## Debug RAG

```http
GET /api/ai/debug/lesson/{lesson_id}?q=اشرح الدرس
```

Re-process: `POST /api/teacher/lessons/{id}/process` or `POST /api/ai/lessons/{id}/process`
