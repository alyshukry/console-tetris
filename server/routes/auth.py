from fastapi import APIRouter

from server.db.store import create_user, validate_user_login
from server.dependencies import DatabaseDep
from server.schemas.user import (
    TokenPair,
    TokenRefresh,
    UserCreate,
    UserLogin,
    UserResponse,
)
from server.security import sign_token, verify_token
from server.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201, response_model=UserResponse)
def register(body: UserCreate, db: DatabaseDep):
    user = create_user(db, body.username, body.password)
    return {
        "username": user.username,
        "user_id": user.user_id,
        "created_at": user.created_at,
    }


@router.post("/login", status_code=200, response_model=TokenPair)
def login(body: UserLogin, db: DatabaseDep):
    user = validate_user_login(db, body.username, body.password)
    return {
        "refresh_token": sign_token(user.user_id, settings.refresh_secret, 10080),
        "access_token": sign_token(user.user_id, settings.access_secret, 15),
    }


@router.post("/refresh", status_code=200, response_model=TokenPair)
def refresh_token(body: TokenRefresh):
    payload = verify_token(body.token, settings.refresh_secret)
    return {
        "refresh_token": sign_token(payload["user_id"], settings.refresh_secret, 10080),
        "access_token": sign_token(payload["user_id"], settings.access_secret, 15),
    }
