from datetime import datetime, timezone
from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token_string,
)
from app.models.user import User, WorkerProfile
from app.models.token import RefreshToken
from app.schemas.auth import UserCreate, TokenResponse, UserResponse
from app.services.audit_service import AuditService


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """Authenticate user credentials."""
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive. Please contact administrator.",
            )

        # Record audit login event
        AuditService.create_audit_entry(
            db=db,
            actor_id=user.id,
            action="LOGIN_SUCCESS",
            entity_type="USER",
            entity_id=user.id,
            change_metadata={"email": user.email, "role": user.role.value},
        )
        return user

    @staticmethod
    def register_user(db: Session, user_in: UserCreate, creator_id: Optional[str] = None) -> User:
        """Register a new user account."""
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{user_in.email}' already exists",
            )

        hashed_pwd = hash_password(user_in.password)
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_pwd,
            full_name=user_in.full_name,
            role=user_in.role,
            phone_number=user_in.phone_number,
            organization_id=user_in.organization_id,
            subsidiary_id=user_in.subsidiary_id,
            mine_id=user_in.mine_id,
            is_active=True,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # If worker profile data provided, create WorkerProfile record
        if user_in.worker_profile:
            wp = WorkerProfile(
                user_id=db_user.id,
                employee_id=user_in.worker_profile.employee_id,
                trade=user_in.worker_profile.trade,
                emergency_contact=user_in.worker_profile.emergency_contact,
                blood_group=user_in.worker_profile.blood_group,
            )
            db.add(wp)
            db.commit()
            db.refresh(db_user)

        AuditService.create_audit_entry(
            db=db,
            actor_id=creator_id or db_user.id,
            action="USER_REGISTERED",
            entity_type="USER",
            entity_id=db_user.id,
            change_metadata={"email": db_user.email, "role": db_user.role.value},
        )
        return db_user

    @staticmethod
    def issue_tokens(db: Session, user: User) -> TokenResponse:
        """Issue access and refresh tokens with refresh token rotation."""
        extra_claims = {
            "email": user.email,
            "name": user.full_name,
            "mine_id": user.mine_id,
            "org_id": user.organization_id,
        }
        access_token = create_access_token(
            subject=user.id,
            role=user.role.value,
            extra_claims=extra_claims,
        )
        raw_refresh_token, token_hash, expires_at = create_refresh_token(subject=user.id)

        # Store refresh token hash in DB
        db_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False,
        )
        db.add(db_token)
        db.commit()

        user_resp = UserResponse.model_validate(user)
        return TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_resp,
        )

    @staticmethod
    def rotate_refresh_token(db: Session, refresh_token_str: str) -> TokenResponse:
        """Rotate refresh token: revoke old token and issue new token pair."""
        try:
            payload = decode_token(refresh_token_str)
            if payload.get("type") != "refresh":
                raise ValueError("Not a refresh token")
            user_id = payload.get("sub")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        token_hash = hash_token_string(refresh_token_str)
        stored_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.user_id == user_id,
        ).first()

        if not stored_token or stored_token.is_revoked:
            # Token reuse detected or token revoked
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is revoked or already used",
            )

        # Revoke old refresh token
        stored_token.is_revoked = True
        db.commit()

        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Issue new token pair
        return AuthService.issue_tokens(db=db, user=user)

    @staticmethod
    def logout(db: Session, user: User) -> None:
        """Revoke all active refresh tokens for the user."""
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.is_revoked == False,
        ).update({"is_revoked": True})
        db.commit()

        AuditService.create_audit_entry(
            db=db,
            actor_id=user.id,
            action="LOGOUT",
            entity_type="USER",
            entity_id=user.id,
        )
