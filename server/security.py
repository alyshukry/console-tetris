from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from server.config import settings
from server.errors import InvalidToken, TokenExpired

ALGORITHM = "HS256"

_ph = PasswordHasher()


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, password)
    except VerifyMismatchError:
        return False


def sign_token(user_id: int, secret: str, ttl: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(UTC) + timedelta(minutes=ttl),
    }
    return jwt.encode(payload, secret, algorithm=ALGORITHM)

def verify_token(token: str, secret: str) -> dict:
    try:
        return jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise TokenExpired() from None
    except jwt.InvalidTokenError:
        raise InvalidToken() from None