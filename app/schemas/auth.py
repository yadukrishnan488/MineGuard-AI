from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.enums import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class WorkerProfileCreate(BaseModel):
    employee_id: str
    trade: str
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = None


class WorkerProfileResponse(BaseModel):
    id: str
    employee_id: str
    trade: str
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = None

    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.WORKER
    phone_number: Optional[str] = None
    organization_id: Optional[str] = None
    subsidiary_id: Optional[str] = None
    mine_id: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    worker_profile: Optional[WorkerProfileCreate] = None


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    worker_profile: Optional[WorkerProfileResponse] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
