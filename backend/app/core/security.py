import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def hash_password(password: str) -> str:
    # bcrypt limit is 72 bytes
    safe = password.encode("utf-8")[:72]
    return bcrypt.hashpw(safe, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    safe = plain.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(safe, hashed.encode("utf-8"))
    except (ValueError, TypeError) as exc:
        logger.warning("bcrypt.checkpw failed (%s), trying passlib fallback", exc)
        try:
            return pwd_context.verify(plain, hashed)
        except Exception:
            logger.exception("passlib verify failed")
            return False


def create_access_token(subject: dict[str, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {**subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
