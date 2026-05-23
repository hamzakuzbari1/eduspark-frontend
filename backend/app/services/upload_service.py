"""Shared PDF / voice upload logic for teacher and AI routes."""

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.lesson import Lesson, LessonStatus
from app.models.user import User

settings = get_settings()


def ensure_upload_dir(teacher_id: int) -> Path:
    p = Path(settings.UPLOAD_DIR) / f"teacher_{teacher_id}"
    p.mkdir(parents=True, exist_ok=True)
    return p


async def save_pdf_upload(
    *,
    file: UploadFile,
    subject: str,
    grade: str,
    title: str | None,
    lesson_id: int | None,
    db: AsyncSession,
    teacher: User,
) -> dict:
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="يجب أن يكون الملف PDF")

    data = await file.read()
    if len(data) > settings.MAX_PDF_BYTES:
        raise HTTPException(status_code=400, detail="حجم الملف يتجاوز الحد المسموح")

    upload_dir = ensure_upload_dir(teacher.id)

    if lesson_id:
        result = await db.execute(
            select(Lesson).where(Lesson.id == lesson_id, Lesson.teacher_id == teacher.id)
        )
        lesson = result.scalar_one_or_none()
        if not lesson:
            raise HTTPException(status_code=404, detail="الدرس غير موجود")
    else:
        lesson = Lesson(
            teacher_id=teacher.id,
            subject=subject,
            grade=grade,
            title=title or "درس جديد",
            status=LessonStatus.draft,
        )
        db.add(lesson)
        await db.flush()

    filename = f"{lesson.id}_{uuid.uuid4().hex}.pdf"
    pdf_path = upload_dir / filename
    pdf_path.write_bytes(data)

    lesson.pdf_path = str(pdf_path)
    lesson.subject = subject
    lesson.grade = grade
    if title:
        lesson.title = title
    await db.commit()
    await db.refresh(lesson)

    return {
        "lesson_id": lesson.id,
        "filename": file.filename,
        "message": "تم رفع ملف PDF بنجاح",
    }
