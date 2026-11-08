from dataclasses import dataclass

from server.schemas.common import Username


@dataclass
class User:
    user_id: int
    username: Username
    password_hash: str
