# EduSpark Backend

FastAPI + PostgreSQL (local) + pgvector + optional Gemini.

## Local run (no Docker)

```bash
# 1. PostgreSQL running on localhost with pgvector
psql -U postgres -f scripts/setup_local_db.sql

# 2. From backend/
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Docs: http://127.0.0.1:8000/docs

Loads `.env` from project root (`../.env`).

## API

- `POST /api/auth/register` · `POST /api/auth/login`
- Teacher upload/process · Student lessons/chat/quiz/profile

Demo: `teacher@eduspark.sy` / `teacher123`
