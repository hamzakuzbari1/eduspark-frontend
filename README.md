# EduSpark Frontend

واجهة عربية (RTL) لمنصة EduSpark — تعليم ذكي بأسلوب المعلم ولهجة سورية.

## التشغيل

```bash
npm install
npm run dev
npm run build
```

## المسارات

| المسار | الوصف |
|--------|--------|
| `/login` | تسجيل الدخول (معلم / طالب) |
| `/register` | إنشاء حساب + اختيار الدور |
| `/teacher/dashboard` | لوحة المعلم — إحصائيات ودروس ونشاط |
| `/teacher/upload` | رفع درس (PDF + صوت + مادة + صف) |
| `/student/dashboard` | لوحة الطالب — بطاقات الدروس |
| `/student/lesson/:id` | جلسة التعلّم (دردشة AI + اختبار + نتائج) |
| `/student/profile` | اهتمامات ومستوى الصعوبة |

## المكوّنات القابلة لإعادة الاستخدام

- `UploadCard` — رفع PDF مع شريط تقدم
- `LoadingOverlay` — معالجة AI
- `VoiceRecorder` — تسجيل 30 ثانية
- `LessonCard` / `StudentLessonCard`
- `ChatBubble` / `TypingIndicator` / `ChatPanel`
- `QuizCard` / `QuizResults`
- `AppSidebar` / `StudentSidebar` / `EmptyState`

## هيكل المشروع

```
src/
├── composables/       usePdfUpload, useVoiceRecorder, useAiChat, useAuth
├── utils/             session, validate
├── components/
│   ├── auth/          AuthShell
│   ├── common/        PageHeader, UploadCard, LoadingOverlay, EmptyState, …
│   ├── layout/        AppSidebar, StudentSidebar, AppHeader
│   ├── teacher/       PdfUploadBox, PdfPreviewCard, StatCard, …
│   └── student/       ChatPanel, QuizCard, QuizResults, …
├── data/              dummyData, studentData, activityData, profileOptions
└── views/             Login, Register, Teacher, Student
```

## تجربة العرض التوضيحي

**معلم:** `teacher@eduspark.sy` → لوحة التحكم → رفع درس → معالجة AI

**طالب:** تسجيل كطالب → الدروس → درس → محادثة + اختبار → الملف الشخصي
