import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import require_role
from app.db.session import get_db
from app.models.lesson import Lesson, LessonStatus
from app.models.quiz import QuizQuestion
from app.models.user import User, UserRole
from app.schemas.teacher import LessonOut, LessonStatusOut, ProcessResponse
from app.services.lesson_process_api import start_lesson_processing
from app.services.upload_service import ensure_upload_dir, save_pdf_upload

router = APIRouter(prefix="/teacher", tags=["Teacher"])
settings = get_settings()


@router.post("/upload/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    subject: str = Form(...),
    grade: str = Form(...),
    title: str | None = Form(None),
    lesson_id: int | None = Form(None),
    db: AsyncSession = Depends(get_db),
    teacher: User = Depends(require_role(UserRole.teacher)),
):
    return await save_pdf_upload(
        file=file,
        subject=subject,
        grade=grade,
        title=title,
        lesson_id=lesson_id,
        db=db,
        teacher=teacher,
    )


@router.post("/upload/voice")
async def upload_voice(
    file: UploadFile = File(...),
    lesson_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    teacher: User = Depends(require_role(UserRole.teacher)),
):
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.teacher_id == teacher.id)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="الدرس غير موجود")

    data = await file.read()
    if len(data) > settings.MAX_AUDIO_BYTES:
        raise HTTPException(status_code=400, detail="حجم الملف الصوتي كبير جداً")

    upload_dir = ensure_upload_dir(teacher.id)
    ext = Path(file.filename or "voice.webm").suffix or ".webm"
    voice_path = upload_dir / f"{lesson.id}_voice_{uuid.uuid4().hex}{ext}"
    voice_path.write_bytes(data)

    lesson.voice_path = str(voice_path)
    await db.commit()

    return {"lesson_id": lesson.id, "message": "تم رفع العينة الصوتية بنجاح"}


@router.post("/lessons/{lesson_id}/process", response_model=ProcessResponse)
async def process_lesson_endpoint(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: User = Depends(require_role(UserRole.teacher)),
):
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.teacher_id == teacher.id)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="الدرس غير موجود")
    if not lesson.pdf_path:
        raise HTTPException(status_code=400, detail="ارفع ملف PDF أولاً")

    return await start_lesson_processing(db, lesson, teacher.id)


@router.get("/lessons/{lesson_id}/status", response_model=LessonStatusOut)
async def lesson_process_status(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: User = Depends(require_role(UserRole.teacher)),
):
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.teacher_id == teacher.id)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="الدرس غير موجود")
    return LessonStatusOut(
        lesson_id=lesson.id,
        status=lesson.status.value,
        message=lesson.error_message or "",
        preview=lesson.preview,
        page_count=lesson.page_count,
    )


@router.get("/content", response_model=list[LessonOut])
async def list_teacher_content(
    db: AsyncSession = Depends(get_db),
    teacher: User = Depends(require_role(UserRole.teacher)),
):
    result = await db.execute(
        select(Lesson).where(Lesson.teacher_id == teacher.id).order_by(Lesson.created_at.desc())
    )
    lessons = result.scalars().all()
    out: list[LessonOut] = []
    for lesson in lessons:
        q_count = await db.scalar(
            select(func.count()).select_from(QuizQuestion).where(QuizQuestion.lesson_id == lesson.id)
        )
        out.append(
            LessonOut(
                id=lesson.id,
                title=lesson.title,
                subject=lesson.subject,
                grade=lesson.grade,
                status=lesson.status.value,
                preview=lesson.preview,
                page_count=lesson.page_count,
                created_at=lesson.created_at.isoformat() if lesson.created_at else None,
                students=0,
                questions=int(q_count or 0),
            )
        )
    return out
