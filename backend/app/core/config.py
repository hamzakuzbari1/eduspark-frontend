"""Application settings — local PostgreSQL by default."""

import os
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

    # Optional local AI stack (Colab pipeline)
    USE_MARKER_PDF: bool = False
    MARKER_TIMEOUT_SECONDS: int = 600
    MARKER_THREAD_WORKERS: int = 1
    MARKER_PERSIST_MD: bool = True
    # Return immediately from /process — Marker can take several minutes
    PDF_PROCESS_IN_BACKGROUND: bool = True
    # True = PDF → Marker → chunk → DB only (skip embeddings, voice persona, quiz)
    PROCESS_MINIMAL_PIPELINE: bool = True
    USE_LOCAL_EMBEDDINGS: bool = False
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_BUILD_TIMEOUT_SECONDS: int = 300
    VOICE_TRANSCRIBE_TIMEOUT_SECONDS: int = 120
    PERSONA_BUILD_TIMEOUT_SECONDS: int = 90
    QUIZ_GENERATION_TIMEOUT_SECONDS: int = 90
    OLLAMA_TIMEOUT_SECONDS: int = 180
    USE_LOCAL_WHISPER: bool = False
    WHISPER_MODEL: str = "turbo"
    USE_LOCAL_TTS: bool = False
    TTS_MODEL: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    OLLAMA_BASE_URL: str = ""
    OLLAMA_MODEL: str = "qwen2.5"

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
    RAG_TOP_K: int = 3
    RAG_MIN_SCORE: float = 0.08
    RAG_MAX_CHUNK_CHARS: int = 500
    RAG_MAX_CONTEXT_CHARS: int = 1500
    # 0 = semantic/keyword only. >0 forces first N chunks (noisy — debug only).
    RAG_FORCE_TOP_K: int = 0
    RAG_DEBUG: bool = False
    RAG_LOG_LLM_PROMPT: bool = False
    QUIZ_COUNT: int = 3

    DB_CONNECT_TIMEOUT: int = 10

    @model_validator(mode="after")
    def apply_local_defaults(self) -> Self:
        in_docker = os.getenv("DOCKER_COMPOSE", "").lower() in ("1", "true", "yes")
        host = (self.POSTGRES_HOST or "localhost").strip()
        # Outside Docker, map compose service names to localhost for local Postgres
        if not in_docker and host in ("db", "postgres"):
            host = "localhost"

        if not self.DATABASE_URL.strip():
            self.DATABASE_URL = self._build_async_url(host)
        elif not in_docker:
            self.DATABASE_URL = self._ensure_localhost(self.DATABASE_URL)

        if not self.DATABASE_URL_SYNC.strip():
            self.DATABASE_URL_SYNC = self._build_sync_url(host)
        elif not in_docker:
            self.DATABASE_URL_SYNC = self._ensure_localhost(self.DATABASE_URL_SYNC)

        if not self.UPLOAD_DIR.strip():
            self.UPLOAD_DIR = str(_backend_dir() / "uploads")
        elif not in_docker and self.UPLOAD_DIR.replace("\\", "/").startswith("/app/"):
            self.UPLOAD_DIR = str(_backend_dir() / "uploads")

        self.POSTGRES_HOST = host
        # In-process FAISS (sentence-transformers) — separate from pgvector column storage
        if self.ENABLE_EMBEDDINGS and not self.USE_LOCAL_EMBEDDINGS:
            self.USE_LOCAL_EMBEDDINGS = True
        if not self.ENABLE_PGVECTOR:
            # DB vector column storage still off; FAISS in-memory is allowed
            pass

        if self.DEBUG and not self.RAG_DEBUG:
            self.RAG_DEBUG = True
        if self.RAG_DEBUG:
            self.RAG_LOG_LLM_PROMPT = True
        if self.USE_MARKER_PDF and self.PDF_PROCESS_IN_BACKGROUND is False:
            self.PDF_PROCESS_IN_BACKGROUND = True
        return self

    @property
    def use_marker_pdf(self) -> bool:
        return self.USE_MARKER_PDF

    @property
    def process_embeddings_enabled(self) -> bool:
        return self.USE_LOCAL_EMBEDDINGS and not self.PROCESS_MINIMAL_PIPELINE

    @property
    def process_voice_persona_enabled(self) -> bool:
        return not self.PROCESS_MINIMAL_PIPELINE

    @property
    def process_quiz_enabled(self) -> bool:
        return not self.PROCESS_MINIMAL_PIPELINE

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
    def cors_origin_regex(self) -> str | None:
        """Allow LAN dev URLs (e.g. http://192.168.x.x:5173) when DEBUG is on."""
        if self.DEBUG:
            return r"https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3})(:\d+)?$"
        return None

    @property
    def database_display(self) -> str:
        return f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
