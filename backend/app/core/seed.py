"""Seed demo users for presentation."""

import logging

from sqlalchemy import select

from app.core.security import hash_password, verify_password
from app.db.session import AsyncSessionLocal
from app.models.profile import StudentProfile
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

DEMO_USERS = [
    {
        "email": "teacher@eduspark.sy",
        "name": "أستاذ أحمد",
        "password": "teacher123",
        "role": UserRole.teacher,
    },
    {
        "email": "student@eduspark.sy",
        "name": "سارة محمد",
        "password": "student123",
        "role": UserRole.student,
    },
]


async def seed_demo_users() -> None:
    async with AsyncSessionLocal() as db:
        for item in DEMO_USERS:
            result = await db.execute(select(User).where(User.email == item["email"]))
            user = result.scalar_one_or_none()

            if user:
                if not verify_password(item["password"], user.hashed_password):
                    user.hashed_password = hash_password(item["password"])
                    logger.info("Reset demo password for %s (hash was invalid)", item["email"])
                continue

            user = User(
                email=item["email"],
                name=item["name"],
                hashed_password=hash_password(item["password"]),
                role=item["role"],
            )
            db.add(user)
            await db.flush()
            if item["role"] == UserRole.student:
                db.add(StudentProfile(user_id=user.id, interests_json="[]", difficulty="medium"))
            logger.info("Seeded user: %s", item["email"])
        await db.commit()
