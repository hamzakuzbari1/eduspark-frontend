from fastapi import APIRouter

from app.api import auth, student, teacher

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(teacher.router)
api_router.include_router(student.router)
