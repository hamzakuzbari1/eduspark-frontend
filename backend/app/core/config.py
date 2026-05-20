"""Application settings — local PostgreSQL by default."""

from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _backend_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _project_root() -> Path:
    return _backend_dir().parent


def _discover_env_files() -> tuple[str, ...]:
    candidates = [
        _project_root() / ".env",
        _backend_dir() / ".env",
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
    ]
    found = [str(p) for p in candidates if p.is_file()]
    return tuple(found) if found else (str(_project_root() / ".env"),)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_discover_env_files(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "EduSpark API"
    API_PREFIX: str = "/api"
    DEBUG: bool = True

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "eduspark"
    POSTGRES_PASSWORD: str = "eduspark"
    POSTGRES_DB: str = "eduspark"

    DATABASE_URL: str = ""
    DATABASE_URL_SYNC: str = ""

    # pgvector / embeddings (off by default for local Windows Postgres)
    ENABLE_PGVECTOR: bool = False
    ENABLE_EMBEDDINGS: bool = False

    JWT_SECRET: str = "change-me-in-production-eduspark-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_EMBED_MODEL: str = "models/text-embedding-004"

    UPLOAD_DIR: str = ""
    MAX_PDF_BYTES: int = 50 * 1024 * 1024
    MAX_AUDIO_BYTES: int = 10 * 1024 * 1024

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120
    RAG_TOP_K: int = 5
    QUIZ_COUNT: int = 3

    DB_CONNECT_TIMEOUT: int = 10

    @model_validator(mode="after")
    def apply_local_defaults(self) -> Self:
        host = (self.POSTGRES_HOST or "localhost").strip()
        if host in ("db", "postgres"):
            host = "localhost"

        if not self.DATABASE_URL.strip():
            self.DATABASE_URL = self._build_async_url(host)
        else:
            self.DATABASE_URL = self._ensure_localhost(self.DATABASE_URL)

        if not self.DATABASE_URL_SYNC.strip():
            self.DATABASE_URL_SYNC = self._build_sync_url(host)
        else:
            self.DATABASE_URL_SYNC = self._ensure_localhost(self.DATABASE_URL_SYNC)

        if not self.UPLOAD_DIR.strip() or self.UPLOAD_DIR.startswith("/app/"):
            self.UPLOAD_DIR = str(_backend_dir() / "uploads")

        self.POSTGRES_HOST = host
        # Embeddings require pgvector in DB
        if not self.ENABLE_PGVECTOR:
            self.ENABLE_EMBEDDINGS = False
        return self

    def _build_async_url(self, host: str) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{host}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def _build_sync_url(self, host: str) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{host}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @staticmethod
    def _ensure_localhost(url: str) -> str:
        return (
            url.replace("@db:", "@localhost:")
            .replace("@db/", "@localhost/")
            .replace("@postgres:", "@localhost:")
        )

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def database_display(self) -> str:
        return f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
