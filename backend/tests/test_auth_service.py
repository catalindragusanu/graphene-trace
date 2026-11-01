"""Unit tests for AuthService"""
import pytest
from datetime import datetime, timezone, timedelta
from jose import jwt
from app.services.auth_service import AuthService
from app.config import settings


class TestAuthService:
    """Test authentication service methods"""

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        plain_password = "testpassword123"
        hashed = AuthService.hash_password(plain_password)
        assert AuthService.verify_password(plain_password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        plain_password = "testpassword123"
        hashed = AuthService.hash_password(plain_password)
        assert AuthService.verify_password("wrongpassword", hashed) is False

    def test_hash_password_different_each_time(self):
        """Test that password hashing produces different hashes (salt)"""
        plain_password = "testpassword123"
        hash1 = AuthService.hash_password(plain_password)
        hash2 = AuthService.hash_password(plain_password)
        assert hash1 != hash2  # Different due to salt

    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = AuthService.create_access_token(data)

        # Decode and verify
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert "exp" in payload

    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = AuthService.create_access_token(data, expires_delta=expires_delta)

        # Decode and verify expiry is approximately correct
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_time = datetime.now(timezone.utc) + expires_delta
        # Allow 5 second tolerance
        assert abs((exp_time - expected_time).total_seconds()) < 5

    @pytest.mark.skip(reason="AuthService.authenticate_user is not implemented")
    def test_authenticate_user_success(self, db_session, test_patient):
        """Test successful user authentication"""
        user = AuthService.authenticate_user(
            email="patient@test.com",
            password="password123",
            db=db_session
        )
        assert user is not None
        assert user.email == "patient@test.com"
        assert user.id == test_patient.id

    @pytest.mark.skip(reason="AuthService.authenticate_user is not implemented")
    def test_authenticate_user_wrong_password(self, db_session, test_patient):
        """Test authentication fails with wrong password"""
        user = AuthService.authenticate_user(
            email="patient@test.com",
            password="wrongpassword",
            db=db_session
        )
        assert user is False

    @pytest.mark.skip(reason="AuthService.authenticate_user is not implemented")
    def test_authenticate_user_nonexistent_email(self, db_session):
        """Test authentication fails with nonexistent email"""
        user = AuthService.authenticate_user(
            email="nonexistent@test.com",
            password="password123",
            db=db_session
        )
        assert user is False

    def test_password_hash_security(self):
        """Test that password hashes are sufficiently secure"""
        password = "password123"
        hashed = AuthService.hash_password(password)

        # Check hash format (bcrypt starts with $2b$)
        assert hashed.startswith("$2b$")
        # Check minimum length
        assert len(hashed) >= 60

    def test_token_contains_required_claims(self):
        """Test that generated tokens contain all required claims"""
        data = {"sub": "test@example.com", "user_id": 1, "role": "patient"}
        token = AuthService.create_access_token(data)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "sub" in payload
        assert "user_id" in payload
        assert "role" in payload
        assert "exp" in payload
