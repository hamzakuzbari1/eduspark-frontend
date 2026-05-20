-- Run as PostgreSQL superuser (adjust if your superuser is different):
--   psql -U postgres -f backend/scripts/setup_local_db.sql
--
-- Creates role + database for EduSpark when you only had an empty "eduspark" DB.

-- Role (skip errors if already exists)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'eduspark') THEN
    CREATE USER eduspark WITH PASSWORD 'eduspark' LOGIN;
  ELSE
    ALTER USER eduspark WITH PASSWORD 'eduspark';
  END IF;
END
$$;

-- Database (skip if you already created it manually)
SELECT 'CREATE DATABASE eduspark OWNER eduspark'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'eduspark')\gexec

GRANT ALL PRIVILEGES ON DATABASE eduspark TO eduspark;

\c eduspark

-- pgvector (install extension on server first — see README)
CREATE EXTENSION IF NOT EXISTS vector;

GRANT ALL ON SCHEMA public TO eduspark;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO eduspark;
