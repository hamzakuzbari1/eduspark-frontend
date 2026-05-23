from pydantic import BaseModel, Field


class AiChatRequest(BaseModel):
    lesson_id: int
    message: str = Field(min_length=1, max_length=4000)


class AiChatResponse(BaseModel):
    reply: str
    messages: list[dict]


class TranscribeResponse(BaseModel):
    text: str
    engine: str


class TtsRequest(BaseModel):
    text: str = Field(min_length=1, max_length=8000)
    lesson_id: int


class TtsResponse(BaseModel):
    audio_url: str | None = None
    message: str
    engine: str


class VoiceChatRequest(BaseModel):
    lesson_id: int


class VoiceChatResponse(BaseModel):
    question: str
    reply: str
    audio_url: str | None = None
    messages: list[dict]
