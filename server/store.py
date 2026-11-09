import itertools
from datetime import datetime

from server.errors import InvalidCredentials, UserNotFound, UsernameTaken
from server.models.user import User
from server.schemas.common import Username
from server.security import hash_password, verify_password

USERS: dict[int, User] = {}  # dict[user_id, tuple[username, password_hash, created_at]]
user_id_counter = itertools.count()


def get_user(username: Username) -> User:
    for user in USERS.values():
        if user.username == username:
            return user
    raise UserNotFound()

def validate_user_login(username: Username, password: str) -> User:
    for user in USERS.values():
        if user.username == username:
            if verify_password(password, user.password_hash):
                return user
            else:
                raise InvalidCredentials()
    raise UserNotFound()


def create_user(username: Username, password: str) -> User:
    if username not in (user.username for user in USERS.values()):
        user_id = next(user_id_counter)
        USERS[user_id] = User(
            user_id, username, hash_password(password), datetime.now()
        )
        return USERS[user_id]
    raise UsernameTaken()
