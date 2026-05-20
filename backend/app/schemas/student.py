from pydantic import BaseModel, Field


class LessonCardOut(BaseModel):
    id: int
    title: str
    subject: str
    grade: str
    teacherName: str
    preview: str
    icon: str = "mdi-book-open-page-variant"


class LessonDetailOut(BaseModel):
    id: int
    title: str
    subject: str
    grade: str
    teacherName: str
    preview: str
    chatMessages: list[dict] = []
    quizQuestions: list[dict] = []


class ChatRequest(BaseModel):
    lesson_id: int
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    reply: str
    messages: list[dict]


class QuizQuestionOut(BaseModel):
    id: int
    question: str
    options: list[str]
    hint: str | None = None


class QuizSubmitRequest(BaseModel):
    lesson_id: int
    answers: dict[str, int]  # question_id -> selected_index


class QuizSubmitResponse(BaseModel):
    correct_count: int
    total: int
    feedback: list[dict]
    score_percent: int


class ProfileUpdate(BaseModel):
    interests: list[str] = []
    difficulty: str = "medium"


class ProfileOut(BaseModel):
    interests: list[str]
    difficulty: str
