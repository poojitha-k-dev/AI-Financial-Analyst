from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import timedelta

from backend.database import get_db
from backend.services.auth_service import (
    authenticate_user, create_user, create_access_token,
    get_current_active_user, hash_password, verify_password,
)
from backend.models.user import User
from backend.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Schemas ───────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    company_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip()


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    plan: str
    company_name: Optional[str]
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def strength(cls, v):
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters")
        return v


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    bio: Optional[str] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────
@router.post("/register", response_model=LoginResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = create_user(
        db=db,
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
    )
    if payload.company_name:
        user.company_name = payload.company_name
        db.commit()

    token = create_access_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return LoginResponse(
        access_token=token,
        user=_user_dict(user),
    )


@router.post("/login", response_model=LoginResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form.username, form.password)
    token = create_access_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return LoginResponse(access_token=token, user=_user_dict(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_active_user)):
    return _user_out(current_user)


@router.patch("/me")
def update_profile(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name.strip()
    if payload.company_name is not None:
        current_user.company_name = payload.company_name
    if payload.bio is not None:
        current_user.bio = payload.bio
    db.commit()
    db.refresh(current_user)
    return {"message": "Profile updated", "user": _user_dict(current_user)}


@router.post("/change-password")
def change_password(
    payload: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(400, "Current password is incorrect")
    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


@router.post("/logout")
def logout():
    # Stateless JWT — client simply discards the token
    return {"message": "Logged out successfully"}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _user_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "plan": user.plan,
        "company_name": user.company_name,
    }


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        plan=user.plan,
        company_name=user.company_name,
        is_active=user.is_active,
        created_at=str(user.created_at),
    )
