from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.permissions import get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    UserCreate,
    UserResponse,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & Security"])


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email and password to receive JWT access token and refresh token.
    """
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)
    return AuthService.issue_tokens(db, user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Rotate refresh token: revoke old token and receive fresh access and refresh tokens.
    """
    return AuthService.rotate_refresh_token(db, req.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Revoke all active refresh tokens for the authenticated user.
    """
    AuthService.logout(db, current_user)
    return {"message": "Successfully logged out and revoked active sessions"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve profile and assigned role/scope of the currently authenticated user.
    """
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account (Worker, Inspector, Manager, etc.).
    """
    user = AuthService.register_user(db, user_in)
    return user
