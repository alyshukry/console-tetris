from dataclasses import dataclass

from server.schemas.common import Username


@dataclass
class User:
    username: Username
    password_hash: str
