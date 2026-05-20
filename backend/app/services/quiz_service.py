"""Generate exactly 3 MCQ questions with hints."""

import json
import logging
import re

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def generate_quiz_questions(
    lesson_text: str,
    subject: str,
    grade: str,
    count: int | None = None,
) -> list[dict]:
    count = count or settings.QUIZ_COUNT
    sample = lesson_text[:8000]

    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.GEMINI_MODEL)
            prompt = f"""من محتوى الدرس التالي، أنشئ بالضبط {count} أسئلة اختيار من متعدد بالعربية.
كل سؤال 4 خيارات (أ، ب، ج، د) وإجابة صحيحة واحدة وتلميح عند الخطأ.
المادة: {subject}، الصف: {grade}.

أعد JSON فقط كمصفوفة:
[{{"question":"...","options":["...","...","...","..."],"correct_index":0,"hint":"..."}}]

المحتوى:
{sample}
"""
            response = model.generate_content(prompt)
            text = (response.text or "").strip()
            match = re.search(r"\[[\s\S]*\]", text)
            if match:
                items = json.loads(match.group())
                return _normalize_quiz(items, count)
        except Exception as exc:
            logger.warning("Quiz generation failed: %s", exc)

    return _default_quiz(subject, count)


def _normalize_quiz(items: list, count: int) -> list[dict]:
    out = []
    for i, item in enumerate(items[:count]):
        options = item.get("options", [])
        if len(options) < 4:
            options = options + ["خيار إضافي"] * (4 - len(options))
        out.append(
            {
                "question": item.get("question", f"سؤال {i + 1}"),
                "options": options[:4],
                "correct_index": int(item.get("correct_index", 0)),
                "hint": item.get("hint", "راجع الشرح في المحادثة"),
            }
        )
    while len(out) < count:
        out.extend(_default_quiz("", count - len(out)))
    return out[:count]


def _default_quiz(subject: str, count: int) -> list[dict]:
    base = [
        {
            "question": f"ما الفكرة الرئيسية في درس {subject or 'هذا الدرس'}؟",
            "options": [
                "فهم المفاهيم الأساسية",
                "حفظ دون فهم",
                "تجاهل الأمثلة",
                "الخروج عن موضوع الدرس",
            ],
            "correct_index": 0,
            "hint": "ركّز على ما شرحه المعلّم في بداية الدرس",
        },
        {
            "question": "أيّ خيار يعبّر عن تطبيق عملي للدرس؟",
            "options": [
                "حل مثال مشابه للشرح",
                "نسيان التعريفات",
                "عدم قراءة الأسئلة",
                "الإجابة عشوائياً",
            ],
            "correct_index": 0,
            "hint": "فكّر بالأمثلة اللي شرحها المعلّم",
        },
        {
            "question": "كيف تتأكد إنك فهمت الدرس؟",
            "options": [
                "شرح الفكرة بكلماتك",
                "تخطي التمارين",
                "عدم السؤال",
                "الاعتماد على الحفظ فقط",
            ],
            "correct_index": 0,
            "hint": "جرب تشرح الدرس لصديقك بأسلوبك",
        },
    ]
    return base[:count]
