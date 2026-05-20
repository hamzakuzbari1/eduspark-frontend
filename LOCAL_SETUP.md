# EduSpark — Local setup checklist

Your error `password authentication failed for user "eduspark"` means PostgreSQL is running, but the **login role** in `.env` does not match your server.

The database `eduspark` can exist while the user `eduspark` does not.

## Option A — Use your existing `postgres` superuser (fastest)

1. Open project `.env` and set your real PostgreSQL password:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_ACTUAL_PASSWORD
POSTGRES_DB=eduspark
```

2. In **pgAdmin** (or any SQL tool), connect to database `eduspark` and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

3. Initialize tables and demo users:

```powershell
cd backend
.\venv\Scripts\activate
python scripts\verify_setup.py
```

4. Start API:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

5. Open http://127.0.0.1:8000/docs

## Option B — Create dedicated `eduspark` user (matches default .env)

In pgAdmin → Query Tool on database `eduspark`:

```sql
CREATE USER eduspark WITH PASSWORD 'eduspark' LOGIN;
GRANT ALL ON SCHEMA public TO eduspark;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO eduspark;
CREATE EXTENSION IF NOT EXISTS vector;
```

Keep `.env`:

```env
POSTGRES_USER=eduspark
POSTGRES_PASSWORD=eduspark
```

Then run `python scripts\verify_setup.py` and start uvicorn.

## Option C — Bootstrap script (if you know postgres password)

```env
POSTGRES_ADMIN_USER=postgres
POSTGRES_ADMIN_PASSWORD=YOUR_ACTUAL_PASSWORD
```

```powershell
cd backend
python scripts\bootstrap_db.py
python scripts\verify_setup.py
```

## Verify everything

| Step | Command / URL |
|------|----------------|
| DB connection | `python scripts\test_connection.py` |
| Tables + seed | `python scripts\verify_setup.py` |
| API health | http://127.0.0.1:8000/health |
| Swagger | http://127.0.0.1:8000/docs |
| Login test | `python scripts\test_api.py` |
| Frontend | `npm run dev` → http://localhost:5173 |

### Demo accounts (after seed)

| Email | Password | Role |
|-------|----------|------|
| teacher@eduspark.sy | teacher123 | teacher |
| student@eduspark.sy | student123 | student |

## Frontend API

Ensure root `.env` has:

```env
VITE_API_URL=http://localhost:8000
```

Vite proxies `/api` to the backend during `npm run dev`.
