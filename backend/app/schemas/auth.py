"""Pydantic schemas for authentication"""
from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Request schema for user login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response schema for successful login"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    name: str
    date_of_birth: Optional[date] = None
    medical_condition: Optional[str] = None
    photo_url: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token"""
    refresh_token: str


class RegisterRequest(BaseModel):
    """Request schema for user registration"""
    email: EmailStr
    password: str
    name: str
    role: str  # "patient" or "clinician"
