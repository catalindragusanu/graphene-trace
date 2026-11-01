"""Integration tests for authentication API endpoints"""
import pytest
from fastapi import status


class TestAuthEndpoints:
    """Test /api/auth endpoints"""

    # Note: /register endpoint does not exist in current implementation
    # Tests below focus on existing /login endpoint

    def test_login_success(self, client, test_patient):
        """Test successful login"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "patient@test.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_patient):
        """Test login with wrong password fails"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "patient@test.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent email fails"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.skip(reason="GET /api/auth/me is not implemented")
    def test_get_current_user_with_valid_token(self, client, auth_headers_patient, test_patient):
        """Test getting current user info with valid token"""
        response = client.get("/api/auth/me", headers=auth_headers_patient)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "patient@test.com"
        assert data["id"] == test_patient.id
        assert data["role"] == "patient"

    @pytest.mark.skip(reason="GET /api/auth/me is not implemented")
    def test_get_current_user_without_token(self, client):
        """Test getting current user without token fails"""
        response = client.get("/api/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.skip(reason="GET /api/auth/me is not implemented")
    def test_get_current_user_with_invalid_token(self, client):
        """Test getting current user with invalid token fails"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_expiration(self, client, test_patient):
        """Test that tokens contain expiration"""
        from jose import jwt
        from app.config import settings

        response = client.post(
            "/api/auth/login",
            json={
                "email": "patient@test.com",
                "password": "password123"
            }
        )
        token = response.json()["access_token"]

        # Decode token (without verification for testing)
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        assert "exp" in payload
