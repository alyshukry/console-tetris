from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import HTTPConnection

from server.errors import InvalidToken, UserNotFound
from server.models.user import User
from server.security import verify_access_token
from server.services.room_manager import RoomManager
from server.store import get_user

bearer = HTTPBearer(auto_error=False)


def get_room_manager(conn: HTTPConnection) -> RoomManager:
    return conn.state.room_manager


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> User:
    if creds is None:
        raise InvalidToken()
    payload = verify_access_token(creds.credentials)
    try:
        return get_user(payload["user_id"])
    except UserNotFound:
        raise InvalidToken() from None


RoomManagerDep = Annotated[RoomManager, Depends(get_room_manager)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
