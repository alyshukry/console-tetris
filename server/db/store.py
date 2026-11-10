from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from server.db.models.user import User
from server.errors import InvalidCredentials, UsernameTaken, UserNotFound
from server.schemas.common import Username
from server.security import hash_password, verify_password

_DUMMY_HASH = hash_password("dummy hash")

def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise UserNotFound()
    return user


def validate_user_login(db: Session, username: Username, password: str) -> User:
    user = db.scalar(select(User).where(User.username == username))
    password_ok = verify_password(password, user.password_hash if user else _DUMMY_HASH)
    if user is None or not password_ok:
        raise InvalidCredentials()
    return user


def create_user(db: Session, username: Username, password: str) -> User:
    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise UsernameTaken() from None
    db.refresh(user)
    return user
