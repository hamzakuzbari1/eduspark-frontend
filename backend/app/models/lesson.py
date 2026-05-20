import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LessonStatus(str, enum.Enum):
    draft = "draft"
    processing = "processing"
    processed = "processed"
    error = "error"


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(500), default="درس جديد")
    subject: Mapped[str] = mapped_column(String(120))
    grade: Mapped[str] = mapped_column(String(50))
    status: Mapped[LessonStatus] = mapped_column(default=LessonStatus.draft)
    pdf_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    voice_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    persona_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    teacher: Mapped["User"] = relationship(back_populates="lessons")
    chunks: Mapped[list["ContentChunk"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    chat_messages: Mapped[list["ChatMessage"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    quiz_questions: Mapped[list["QuizQuestion"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")


class ContentChunk(Base):
    """Text chunks from PDF — no vector column unless ENABLE_PGVECTOR is enabled."""

    __tablename__ = "content_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    lesson: Mapped["Lesson"] = relationship(back_populates="chunks")
