"""AI endpoints: chat, PDF ingest, transcription, TTS."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.lesson import Lesson, LessonStatus
from app.models.user import User, UserRole
from app.schemas.ai import (
    AiChatRequest,
    AiChatResponse,
    TranscribeResponse,
    TtsRequest,
    TtsResponse,
    VoiceChatResponse,
)
from app.schemas.student import ChatRequest
from app.services.chat_service import handle_student_chat
from app.services.lesson_process_api import start_lesson_processing
from app.services.rag_service import get_lesson_rag_debug
from app.services.voice_service import transcribe_audio as transcribe_audio_service
from app.ai.tts import is_tts_available, text_to_speech
from app.ai.whisper import is_whisper_available

router = APIRouter(prefix="/ai", tags=["AI"])
settings = get_settings()


def _upload_root() -> Path:
    p = Path(settings.UPLOAD_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p


@router.get("/debug/lesson/{lesson_id}")
async def debug_lesson_rag(
    lesson_id: int,
    q: str = "اشرح الدرس",
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Inspect RAG state for a lesson (chunks in DB, scores, sample retrieval).
    Requires login (teacher or student).
    """
    return await get_lesson_rag_debug(db, lesson_id, sample_query=q)


@router.post("/chat", response_model=AiChatResponse)
async def ai_chat(
    body: AiChatRequest,
    db: AsyncSession = Depends(get_db),
    student: User = Depends(require_role(UserRole.student)),
):
    try:
        result = await handle_student_chat(
            db,
            student,
            ChatRequest(lesson_id=body.lesson_id, message=body.message),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return AiChatResponse(reply=result.reply, messages=result.messages)


@router.post("/pdf/upload")
async def ai_upload_pdf(
    file: UploadFile = File(...),
    subject: str = Form(...),
    grade: str = Form(...),
    title: str | None = Form(None),
    lesson_id: int | None = Form(None),
    auto_process: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    teacher: User = Depends(require_role(UserRole.teacher)),
):
    """Upload PDF (same as /teacher/upload/pdf) with optional immediate RAG processing."""
    from app.services.upload_service import save_pdf_upload

    upload_result = await save_pdf_upload(
        file=file,
        subject=subject,
        grade=grade,
        title=title,
        lesson_id=lesson_id,
        db=db,
        teacher=teacher,
    )
    lid = upload_result["lesson_id"]

    if auto_process:
        result = await db.execute(
            select(Lesson).where(Lesson.id == lid, Lesson.teacher_id == teacher.id)
        )
        lesson = result.scalar_one_or_none()
        if lesson:
            proc = await start_lesson_processing(db, lesson, teacher.id)
            upload_result["status"] = proc.status
            upload_result["process_message"] = proc.message

    return upload_result


@router.post("/lessons/{lesson_id}/process")
async def ai_process_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    teacher: User = Depends(require_role(UserRole.teacher)),
):
    """Run full RAG pipeline on uploaded PDF + voice sample."""
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.teacher_id == teacher.id)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="الدرس غير موجود")
    if not lesson.pdf_path:
        raise HTTPException(status_code=400, detail="ارفع ملف PDF أولاً")

    proc = await start_lesson_processing(db, lesson, teacher.id)
    return {
        "lesson_id": proc.lesson_id,
        "status": proc.status,
        "message": proc.message,
    }


@router.post("/transcribe", response_model=TranscribeResponse)
async def ai_transcribe(
    file: UploadFile = File(...),
    lesson_id: int | None = Form(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    data = await file.read()
    if len(data) > settings.MAX_AUDIO_BYTES:
        raise HTTPException(status_code=400, detail="حجم الملف الصوتي كبير جداً")

    ext = Path(file.filename or "audio.webm").suffix or ".webm"
    folder = _upload_root() / f"user_{user.id}"
    folder.mkdir(parents=True, exist_ok=True)
    audio_path = folder / f"transcribe_{uuid.uuid4().hex}{ext}"
    audio_path.write_bytes(data)

    if lesson_id and user.role == UserRole.student:
        lr = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
        lesson = lr.scalar_one_or_none()
        if not lesson:
            raise HTTPException(status_code=404, detail="الدرس غير موجود")

    text = await transcribe_audio_service(audio_path)
    engine = "whisper" if is_whisper_available() and text else "gemini"
    if not text:
        engine = "fallback"
        text = ""

    return TranscribeResponse(text=text, engine=engine)


@router.post("/chat/voice", response_model=VoiceChatResponse)
async def ai_voice_chat(
    file: UploadFile = File(...),
    lesson_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    student: User = Depends(require_role(UserRole.student)),
):
    """Voice question → transcribe → RAG chat → optional TTS reply."""
    data = await file.read()
    if len(data) > settings.MAX_AUDIO_BYTES:
        raise HTTPException(status_code=400, detail="حجم الملف الصوتي كبير جداً")

    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.status == LessonStatus.processed)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="الدرس غير موجود")

    folder = _upload_root() / f"student_{student.id}"
    folder.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "question.webm").suffix or ".webm"
    audio_path = folder / f"q_{uuid.uuid4().hex}{ext}"
    audio_path.write_bytes(data)

    question = await transcribe_audio_service(audio_path)
    if not question.strip():
        raise HTTPException(status_code=400, detail="تعذر فهم التسجيل الصوتي")

    chat_result = await handle_student_chat(
        db,
        student,
        ChatRequest(lesson_id=lesson_id, message=question),
    )

    audio_url = None
    if lesson.voice_path and is_tts_available():
        out = await text_to_speech(
            chat_result.reply,
            lesson.voice_path,
            folder / f"answer_{uuid.uuid4().hex}.wav",
        )
        if out:
            audio_url = f"/api/ai/audio/{Path(out).name}"

    return VoiceChatResponse(
        question=question,
        reply=chat_result.reply,
        audio_url=audio_url,
        messages=chat_result.messages,
    )


@router.post("/tts", response_model=TtsResponse)
async def ai_tts(
    body: TtsRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Lesson).where(Lesson.id == body.lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="الدرس غير موجود")

    if user.role == UserRole.teacher and lesson.teacher_id != user.id:
        raise HTTPException(status_code=403, detail="ليس لديك صلاحية")
    if user.role == UserRole.student and lesson.status != LessonStatus.processed:
        raise HTTPException(status_code=400, detail="الدرس غير جاهز")

    if not lesson.voice_path:
        return TtsResponse(
            audio_url=None,
            message="لا توجد عينة صوت للمعلّم — ارفع الصوت عند إنشاء الدرس",
            engine="none",
        )

    if not is_tts_available():
        return TtsResponse(
            audio_url=None,
            message="محرك TTS غير مفعّل على الخادم",
            engine="disabled",
        )

    out_dir = _upload_root() / "tts"
    out_path = out_dir / f"{uuid.uuid4().hex}.wav"
    path = await text_to_speech(body.text, lesson.voice_path, out_path)
    if not path:
        raise HTTPException(status_code=500, detail="فشل تحويل النص إلى صوت")

    return TtsResponse(
        audio_url=f"/api/ai/audio/{Path(path).name}",
        message="تم إنشاء الملف الصوتي",
        engine="xtts",
    )


@router.get("/audio/{filename}")
async def serve_tts_audio(
    filename: str,
    user: User = Depends(get_current_user),
):
    safe = Path(filename).name
    path = _upload_root() / "tts" / safe
    if not path.is_file():
        # Also check student answer files in uploads tree
        matches = list(_upload_root().rglob(safe))
        path = matches[0] if matches else path
    if not path.is_file():
        raise HTTPException(status_code=404, detail="الملف غير موجود")
    return FileResponse(path, media_type="audio/wav")
