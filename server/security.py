from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from server.config import settings

ALGORITHM = "HS256"

_ph = PasswordHasher()


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, password)
    except VerifyMismatchError:
        return False


def sign_access_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    return jwt.encode(payload, settings.access_secret, algorithm=ALGORITHM)


def sign_refresh_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, settings.refresh_secret, algorithm=ALGORITHM)


def verify_access_token(token: str) -> dict:
    return jwt.decode(token, settings.access_secret, algorithms=[ALGORITHM])


def verify_refresh_token(token: str) -> dict:
    return jwt.decode(token, settings.refresh_secret, algorithms=[ALGORITHM])
