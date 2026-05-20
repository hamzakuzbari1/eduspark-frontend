import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.chat import ChatMessage
from app.models.lesson import Lesson, LessonStatus
from app.models.profile import StudentProfile
from app.models.quiz import QuizAttempt, QuizQuestion
from app.models.user import User, UserRole
from app.schemas.student import (
    ChatRequest,
    ChatResponse,
    LessonCardOut,
    LessonDetailOut,
    ProfileOut,
    ProfileUpdate,
    QuizQuestionOut,
    QuizSubmitRequest,
    QuizSubmitResponse,
)
from app.services.ai_service import generate_tutor_reply
from app.services.rag_service import retrieve_chunks

router = APIRouter(prefix="/student", tags=["Student"])


def _format_time(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.strftime("%H:%M")


@router.get("/lessons", response_model=list[LessonCardOut])
async def list_lessons(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.student)),
):
    result = await db.execute(
        select(Lesson)
        .where(Lesson.status == LessonStatus.processed)
        .options(selectinload(Lesson.teacher))
        .order_by(Lesson.created_at.desc())
    )
    lessons = result.scalars().all()
    return [
        LessonCardOut(
            id=l.id,
            title=l.title,
            subject=l.subject,
            grade=l.grade,
            teacherName=l.teacher.name if l.teacher else "معلّم",
            preview=l.preview or "درس تفاعلي بالذكاء الاصطناعي",
        )
        for l in lessons
    ]


@router.get("/lesson/{lesson_id}", response_model=LessonDetailOut)
async def get_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    student: User = Depends(require_role(UserRole.student)),
):
    result = await db.execute(
        select(Lesson)
        .where(Lesson.id == lesson_id, Lesson.status == LessonStatus.processed)
        .options(selectinload(Lesson.teacher), selectinload(Lesson.quiz_questions))
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="الدرس غير موجود")

    chat_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.lesson_id == lesson_id, ChatMessage.student_id == student.id)
        .order_by(ChatMessage.created_at)
    )
    messages = [
        {
            "id": m.id,
            "role": m.role,
            "text": m.content,
            "time": _format_time(m.created_at),
        }
        for m in chat_result.scalars().all()
    ]

    if not messages:
        messages = [
            {
                "id": 1,
                "role": "ai",
                "text": f"أهلاً {student.name}! أنا معلّمك الذكي — اسألني أي شي عن درس «{lesson.title}».",
                "time": _format_time(datetime.utcnow()),
            }
        ]

    quiz = []
    for q in sorted(lesson.quiz_questions, key=lambda x: x.sort_order):
        quiz.append(
            {
                "id": q.id,
                "question": q.question,
                "options": json.loads(q.options_json),
                "correctIndex": q.correct_index,
                "hint": q.hint,
            }
        )

    return LessonDetailOut(
        id=lesson.id,
        title=lesson.title,
        subject=lesson.subject,
        grade=lesson.grade,
        teacherName=lesson.teacher.name if lesson.teacher else "معلّم",
        preview=lesson.preview or "",
        chatMessages=messages,
        quizQuestions=quiz,
    )


@router.post("/chat", response_model=ChatResponse)
async def student_chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    student: User = Depends(require_role(UserRole.student)),
):
    result = await db.execute(
        select(Lesson).where(Lesson.id == body.lesson_id, Lesson.status == LessonStatus.processed)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        raise HTTPException(status_code=404, detail="الدرس غير موجود")

    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == student.id)
    )
    profile = profile_result.scalar_one_or_none()
    difficulty = profile.difficulty if profile else "medium"

    db.add(
        ChatMessage(
            lesson_id=lesson.id,
            student_id=student.id,
            role="student",
            content=body.message,
        )
    )

    chunks = await retrieve_chunks(db, lesson.id, body.message)
    reply = await generate_tutor_reply(
        body.message,
        chunks,
        lesson.persona_prompt or "",
        lesson.subject,
        lesson.grade,
        difficulty,
    )

    ai_msg = ChatMessage(
        lesson_id=lesson.id,
        student_id=student.id,
        role="ai",
        content=reply,
    )
    db.add(ai_msg)
    await db.commit()
    await db.refresh(ai_msg)

    history = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.lesson_id == lesson.id, ChatMessage.student_id == student.id)
        .order_by(ChatMessage.created_at)
    )
    messages = [
        {
            "id": m.id,
            "role": m.role,
            "text": m.content,
            "time": _format_time(m.created_at),
        }
        for m in history.scalars().all()
    ]

    return ChatResponse(reply=reply, messages=messages)


@router.get("/quiz/{lesson_id}", response_model=list[QuizQuestionOut])
async def get_quiz(
    lesson_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.student)),
):
    result = await db.execute(
        select(QuizQuestion)
        .where(QuizQuestion.lesson_id == lesson_id)
        .order_by(QuizQuestion.sort_order)
    )
    questions = result.scalars().all()
    if not questions:
        raise HTTPException(status_code=404, detail="لا يوجد اختبار لهذا الدرس")
    return [
        QuizQuestionOut(
            id=q.id,
            question=q.question,
            options=json.loads(q.options_json),
            hint=q.hint,
        )
        for q in questions
    ]


@router.post("/quiz/submit", response_model=QuizSubmitResponse)
async def submit_quiz(
    body: QuizSubmitRequest,
    db: AsyncSession = Depends(get_db),
    student: User = Depends(require_role(UserRole.student)),
):
    lesson_id = body.lesson_id
    result = await db.execute(
        select(QuizQuestion).where(QuizQuestion.lesson_id == lesson_id).order_by(QuizQuestion.sort_order)
    )
    questions = result.scalars().all()
    if not questions:
        raise HTTPException(status_code=404, detail="لا يوجد اختبار")

    correct = 0
    feedback = []
    for q in questions:
        selected = body.answers.get(str(q.id), body.answers.get(q.id, -1))
        is_correct = int(selected) == q.correct_index
        if is_correct:
            correct += 1
        feedback.append(
            {
                "questionId": q.id,
                "correct": is_correct,
                "hint": q.hint if not is_correct else None,
                "message": "إجابة صحيحة!" if is_correct else "حاول مرة أخرى — راجع التلميح",
            }
        )

    total = len(questions)
    db.add(
        QuizAttempt(
            lesson_id=lesson_id,
            student_id=student.id,
            answers_json=json.dumps(body.answers, ensure_ascii=False),
            correct_count=correct,
            feedback_json=json.dumps(feedback, ensure_ascii=False),
        )
    )
    await db.commit()

    return QuizSubmitResponse(
        correct_count=correct,
        total=total,
        feedback=feedback,
        score_percent=round((correct / total) * 100) if total else 0,
    )


@router.put("/profile", response_model=ProfileOut)
async def update_profile(
    body: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    student: User = Depends(require_role(UserRole.student)),
):
    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == student.id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = StudentProfile(user_id=student.id)
        db.add(profile)

    profile.interests_json = json.dumps(body.interests, ensure_ascii=False)
    profile.difficulty = body.difficulty
    await db.commit()

    return ProfileOut(interests=body.interests, difficulty=body.difficulty)


@router.get("/profile", response_model=ProfileOut)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    student: User = Depends(require_role(UserRole.student)),
):
    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == student.id))
    profile = result.scalar_one_or_none()
    if not profile:
        return ProfileOut(interests=[], difficulty="medium")
    return ProfileOut(
        interests=json.loads(profile.interests_json or "[]"),
        difficulty=profile.difficulty,
    )
