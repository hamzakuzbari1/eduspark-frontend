import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.seed import seed_demo_users
from app.db.session import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    logger.info("Uploads: %s", upload_path.resolve())
    logger.info("PostgreSQL: %s", settings.database_display)
    logger.info(
        "pgvector=%s embeddings=%s minimal_pipeline=%s (keyword RAG when minimal/off)",
        settings.ENABLE_PGVECTOR,
        settings.ENABLE_EMBEDDINGS,
        settings.PROCESS_MINIMAL_PIPELINE,
    )
    if settings.PROCESS_MINIMAL_PIPELINE:
        logger.info(
            "PROCESS_MINIMAL_PIPELINE=true → PDF/chunk/DB only (no embeddings, voice persona, quiz)"
        )

    await init_db()
    await seed_demo_users()

    if settings.USE_MARKER_PDF:
        logger.info(
            "Marker PDF: enabled timeout=%ss background=%s persist_md=%s",
            settings.MARKER_TIMEOUT_SECONDS,
            settings.PDF_PROCESS_IN_BACKGROUND,
            settings.MARKER_PERSIST_MD,
        )

    logger.info("%s ready — http://127.0.0.1:8000/docs", settings.APP_NAME)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="EduSpark — منصة تعليم ذكية | FastAPI + PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "database": settings.database_display,
        "pgvector": settings.ENABLE_PGVECTOR,
        "embeddings": settings.ENABLE_EMBEDDINGS,
        "use_marker_pdf": settings.USE_MARKER_PDF,
        "pdf_process_background": settings.PDF_PROCESS_IN_BACKGROUND,
    }
