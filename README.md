# EduSpark — منصة التعليم الذكي

واجهة عربية (RTL) + FastAPI + **PostgreSQL محلي** — بدون الحاجة إلى Docker للتطوير.

## المتطلبات

| أداة | الإصدار |
|------|---------|
| Node.js | 18+ |
| Python | 3.10+ |
| PostgreSQL | 14+ مع [pgvector](https://github.com/pgvector/pgvector#installation) |

## 1) إعداد PostgreSQL (مرة واحدة)

**مهم:** وجود قاعدة `eduspark` لا يعني وجود مستخدم `eduspark`. راجع **[LOCAL_SETUP.md](./LOCAL_SETUP.md)** إذا ظهر `password authentication failed`.

```powershell
cd backend
python scripts\verify_setup.py    # بعد ضبط .env
```

أو من pgAdmin على قاعدة `eduspark`:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
-- وإنشاء مستخدم eduspark إن لم يكن موجوداً (انظر LOCAL_SETUP.md)
```

## 2) إعداد المشروع

```bash
cp .env.example .env
# عدّل POSTGRES_* إذا كانت بيانات الاتصال مختلفة
```

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API: http://localhost:8000  
- Swagger: http://localhost:8000/docs  

### Frontend

```bash
# من جذر المشروع
npm install
npm run dev
```

- التطبيق: http://localhost:5173  

## حسابات تجريبية (تُنشأ تلقائياً عند أول تشغيل)

| الدور | البريد | كلمة المرور |
|-------|--------|-------------|
| معلم | teacher@eduspark.sy | teacher123 |
| طالب | student@eduspark.sy | student123 |

## ملف `.env`

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=eduspark
POSTGRES_PASSWORD=eduspark
POSTGRES_DB=eduspark
VITE_API_URL=http://localhost:8000
```

## هيكل المشروع

```
├── backend/              FastAPI + SQLAlchemy + asyncpg
│   ├── app/
│   ├── scripts/          setup_local_db.sql
│   └── uploads/          ملفات PDF/صوت محلياً
├── src/                  Vue 3 + Vuetify
├── .env                  إعدادات محلية
└── deploy/               Docker (اختياري للنشر)
```

## Docker (اختياري — الحاويات كاملة)

التطوير المحلي بدون Docker ما زال مدعوماً. لتشغيل الواجهة + API + PostgreSQL مع hot reload:

```bash
docker compose up --build
```

| الخدمة | الرابط |
|--------|--------|
| الواجهة | http://localhost:5173 |
| API | http://localhost:8000/docs |

التفاصيل: **[DOCKER.md](./DOCKER.md)** — المنافذ، المتغيرات، تعارض 5432، استكشاف الأخطاء.

## استكشاف الأخطاء

| المشكلة | الحل |
|---------|------|
| `Connection refused` على 5432 | شغّل خدمة PostgreSQL محلياً |
| `extension "vector" does not exist` | ثبّت pgvector على PostgreSQL |
| `uvicorn` غير معروف | استخدم `python -m uvicorn` من مجلد `backend` |
| الواجهة لا تتصل بالـ API | تأكد من `VITE_API_URL=http://localhost:8000` |
