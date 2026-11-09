from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from starlette.requests import HTTPConnection

from server.db.models.user import User
from server.db.session import SessionLocal
from server.db.store import get_user
from server.errors import InvalidToken, UserNotFound
from server.security import verify_token
from server.services.room_manager import RoomManager
from server.config import settings

bearer = HTTPBearer(auto_error=False)


class Bearer(HTTPBearer):
    async def __call__(self, conn: HTTPConnection):  # type: ignore[override]
        return await super().__call__(conn)  # type: ignore[arg-type]


def get_room_manager(conn: HTTPConnection) -> RoomManager:
    return conn.state.room_manager


BearerDep = Annotated[HTTPAuthorizationCredentials, Depends(Bearer(auto_error=False))]


def get_current_user(
    creds: BearerDep,
) -> User:
    if creds is None:
        raise InvalidToken()
    payload = verify_token(creds.credentials, settings.access_secret)
    with SessionLocal() as db:
        try:
            return get_user(db, payload["user_id"])
        except UserNotFound:
            raise InvalidToken() from None


def get_db() -> Iterator[Session]:
    with SessionLocal() as db:
        yield db


RoomManagerDep = Annotated[RoomManager, Depends(get_room_manager)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
DatabaseDep = Annotated[Session, Depends(get_db)]
