# EduSpark — Docker

Run the full stack (Vue + FastAPI + PostgreSQL) with hot reload for frontend and backend.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose v2)
- Optional: copy env template

```bash
cp .env.docker.example .env
# Edit GEMINI_API_KEY, JWT_SECRET, POSTGRES_PUBLISH_PORT if needed
```

## Quick start

From the **project root**:

```bash
docker compose up --build
```

| Service   | URL |
|-----------|-----|
| Frontend  | http://localhost:5173 |
| API       | http://localhost:8000 |
| Swagger   | http://localhost:8000/docs |
| PostgreSQL| `localhost:${POSTGRES_PUBLISH_PORT:-5432}` (user/db from `.env`, default `eduspark`) |

### Demo accounts

| Role    | Email                 | Password    |
|---------|-----------------------|-------------|
| Teacher | teacher@eduspark.sy   | teacher123  |
| Student | student@eduspark.sy   | student123  |

## How it works

- **PostgreSQL** — `postgres:16-alpine`, data in volume `pgdata`
- **Backend** — waits for DB healthcheck, then starts with `uvicorn --reload`
- **Frontend** — Vite dev server; `/api` proxied to `http://backend:8000`
- **Uploads** — persisted in `./backend/uploads` on the host

## Environment variables

Compose sets `DOCKER_COMPOSE=1` and `POSTGRES_HOST=db` for the API container.  
Your root `.env` is loaded when present (`env_file`, not required).

| Variable | Docker default | Local dev (no Docker) |
|----------|----------------|------------------------|
| `POSTGRES_HOST` | `db` (via compose) | `localhost` |
| `VITE_API_URL` | `http://backend:8000` (in container) | `http://127.0.0.1:8000` |
| `UPLOAD_DIR` | `/app/uploads` | `backend/uploads` |

## Port conflict with local PostgreSQL

If port **5432** is already in use on your machine:

```env
POSTGRES_PUBLISH_PORT=5433
```

Then connect tools to `localhost:5433`.

## Commands

```bash
# Detached
docker compose up --build -d

# Logs
docker compose logs -f backend

# Stop and remove containers (keeps DB volume)
docker compose down

# Stop and remove DB volume
docker compose down -v

# Rebuild one service
docker compose up --build backend
```

## Local development without Docker

Unchanged — see [README.md](./README.md) and [LOCAL_SETUP.md](./LOCAL_SETUP.md):

```bash
# Terminal 1 — backend
cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — frontend
npm run dev
```

Use `POSTGRES_HOST=localhost` in `.env` (not `db`).

## Image notes

- **Excluded from images:** `node_modules/`, `backend/venv/`, uploads, `.env`
- **Frontend:** `node:20-alpine` + `npm ci`; source mounted for HMR
- **Backend:** `python:3.11-slim` + OCR deps; `app/` mounted for `--reload`
- **pgvector:** disabled by default (`ENABLE_PGVECTOR=false`). Use a pgvector image and enable flags when needed.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `port is already allocated` (5432) | Set `POSTGRES_PUBLISH_PORT=5433` |
| Frontend cannot reach API | Ensure backend is healthy; open http://localhost:5173 (not only network IP) |
| Backend `connection refused` to DB | Wait for healthcheck; run `docker compose ps` |
| Changes to `package.json` | Rebuild frontend: `docker compose up --build frontend` |
| Changes to `requirements.txt` | Rebuild backend: `docker compose up --build backend` |
