from dataclasses import dataclass


@dataclass
class Session:
    username: str
    access_token: str
    refresh_token: str
