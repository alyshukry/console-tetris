from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.dependencies import DatabaseDep
from server.schemas.user import (
    TokenPair,
    TokenRefresh,
    UserCreate,
    UserLogin,
    UserResponse,
)
from server.security import sign_access_token, sign_refresh_token, verify_refresh_token
from server.store import create_user, validate_user_login

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
        "refresh_token": sign_refresh_token(user.user_id),
        "access_token": sign_access_token(user.user_id),
    }


@router.post("/refresh", status_code=200, response_model=TokenPair)
def refresh_token(body: TokenRefresh):
    payload = verify_refresh_token(body.token)
    return {
        "refresh_token": sign_refresh_token(payload["user_id"]),
        "access_token": sign_access_token(payload["user_id"]),
    }
