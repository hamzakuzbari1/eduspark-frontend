import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.profile import StudentProfile
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    email = body.email.lower().strip()
    logger.info("Register request email=%s role=%s", email, body.role)

    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="البريد الإلكتروني مستخدم مسبقاً")

    role = UserRole.teacher if body.role == "teacher" else UserRole.student
    user = User(
        email=email,
        name=body.name.strip(),
        hashed_password=hash_password(body.password),
        role=role,
    )
    db.add(user)
    await db.flush()

    if role == UserRole.student:
        db.add(StudentProfile(user_id=user.id, interests_json="[]", difficulty="medium"))

    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    logger.info("Register OK user_id=%s email=%s jwt=issued", user.id, email)
    return TokenResponse(
        access_token=token,
        user=UserOut(id=user.id, name=user.name, email=user.email, role=user.role.value),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    email = body.email.lower().strip()
    client = request.client.host if request.client else "?"
    logger.info("Login request email=%s client=%s", email, client)

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("Login failed: email not found (%s)", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="البريد أو كلمة المرور غير صحيحة",
        )

    logger.info("Login email lookup OK user_id=%s role=%s", user.id, user.role.value)

    password_ok = verify_password(body.password, user.hashed_password)
    logger.info("Login password_verify=%s user_id=%s", password_ok, user.id)

    if not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="البريد أو كلمة المرور غير صحيحة",
        )

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    logger.info("Login JWT created user_id=%s role=%s", user.id, user.role.value)

    return TokenResponse(
        access_token=token,
        user=UserOut(id=user.id, name=user.name, email=user.email, role=user.role.value),
    )
