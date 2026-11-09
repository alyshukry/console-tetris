from datetime import datetime

from pydantic import BaseModel, Field

from server.schemas.common import Username


class UserBase(BaseModel):
    username: Username

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int
    created_at: datetime

class TokenRefresh(BaseModel):
    token: str

class TokenPair(BaseModel):
    refresh_token: str
    access_token: str
