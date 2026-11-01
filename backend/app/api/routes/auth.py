"""Authentication API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.rate_limit import limiter
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthService
from app.models.user import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # 5 login attempts per minute per IP
def login(request: Request, login_request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.

    Args:
        request: Incoming HTTP request (used by the rate limiter)
        login_request: Login credentials (email and password)
        db: Database session

    Returns:
        TokenResponse: JWT token and user information

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_request.email).first()

    # Verify credentials
    if not user or not AuthService.verify_password(login_request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        role=user.role.value,
        name=user.name,
        date_of_birth=user.date_of_birth,
        medical_condition=user.medical_condition,
        photo_url=user.photo_url
    )
