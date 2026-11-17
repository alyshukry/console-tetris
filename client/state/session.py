from dataclasses import dataclass


@dataclass
class SessionState:
    access_token: str | None = None
    refresh_token: str | None = None
    username: str | None = None
