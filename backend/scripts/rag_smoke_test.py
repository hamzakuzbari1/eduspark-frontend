"""Quick RAG DB check: python scripts/rag_smoke_test.py [lesson_id]"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.models.lesson import ContentChunk, Lesson, LessonStatus
from app.services.rag_service import retrieve_chunks_detailed


async def main() -> None:
    lesson_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    settings = get_settings()
    print("RAG_FORCE_TOP_K", settings.RAG_FORCE_TOP_K, "RAG_DEBUG", settings.RAG_DEBUG)
    print("OLLAMA", settings.OLLAMA_BASE_URL, settings.OLLAMA_MODEL)

    async with AsyncSessionLocal() as db:
        if lesson_id:
            lessons = [lesson_id]
        else:
            r = await db.execute(
                select(Lesson.id).where(Lesson.status == LessonStatus.processed).limit(5)
            )
            lessons = [row[0] for row in r.all()]

        if not lessons:
            print("No processed lessons found")
            return

        for lid in lessons:
            cnt = await db.scalar(
                select(func.count()).select_from(ContentChunk).where(ContentChunk.lesson_id == lid)
            )
            ret = await retrieve_chunks_detailed(db, lid, "اشرح الدرس")
            print(f"\nlesson_id={lid} db_chunks={cnt} selected={len(ret.chunks)} strategy={ret.strategy}")
            for p in ret.chunk_previews:
                print(" ", p[:100])


if __name__ == "__main__":
    asyncio.run(main())
