"""Dependency injection functions for FastAPI"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from app.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User, UserRole

# HTTP Bearer security scheme
# auto_error=False so a missing token yields 401 (not FastAPI's default 403)
security = HTTPBearer(auto_error=False)
optional_security = security


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer credentials with JWT token
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    try:
        # Decode token
        payload = AuthService.decode_token(credentials.credentials)
        # Refresh tokens must not be usable as access tokens
        if payload.get("type") == "refresh":
            raise credentials_exception

        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_exception

    return user


def require_clinician(current_user: User = Depends(get_current_user)) -> User:
    """
    Require the current user to be a clinician.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current user (clinician)

    Raises:
        HTTPException: If user is not a clinician
    """
    if current_user.role != UserRole.clinician:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clinician access required"
        )

    return current_user


def require_patient(current_user: User = Depends(get_current_user)) -> User:
    """
    Require the current user to be a patient.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current user (patient)

    Raises:
        HTTPException: If user is not a patient
    """
    if current_user.role != UserRole.patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient access required"
        )

    return current_user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(optional_security),
    db: Session = Depends(get_db)
) -> User | None:
    """
    Get the current user if authenticated, None otherwise.

    Useful for endpoints that have both authenticated and unauthenticated access.

    Args:
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        User or None: Current user if authenticated
    """
    if not credentials:
        return None

    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
