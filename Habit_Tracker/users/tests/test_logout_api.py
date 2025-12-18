import pytest
from rest_framework.test import APIClient
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.mark.django_db
class TestLogoutAPI:
    """Test suite for the Logout API endpoint."""
    def setup_method(self):
        """Set up authenticated user and JWT tokens for logout tests."""
        self.client = APIClient()
        self.url = "/auth/api/v1/logout/"
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")
        refresh = RefreshToken.for_user(self.user)
        self.refresh_token = refresh
        self.access_token = refresh.access_token

    def test_logout_success(self):
        """Authenticated user can successfully logout using a valid refresh token."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.post(self.url, {"refresh_token": str(self.refresh_token)})

        assert response.status_code == 204

    def test_logout_missing_token(self):
        """Logout should fail if refresh token is not provided."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.post(self.url, {})

        assert response.status_code == 400
        assert "refresh_token" in response.json()

    def test_logout_invalid_token(self):
        """Invalid refresh token should return a validation error."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        
        response = self.client.post(self.url, {"refresh_token": "invalid_refresh_token"})
        data = response.json()

        assert response.status_code == 400
        assert "Invalid or expired token" in data

    def test_logout_requires_authentication(self):
        """Unauthenticated users must not be allowed to logout."""
        response = self.client.post(self.url, {"refresh_token": str(self.refresh_token)})

        assert response.status_code == 401

    def test_logout_token_blacklisted(self):
        """Refresh token must be blacklisted after successful logout."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        
        response = self.client.post(self.url, {"refresh_token": str(self.refresh_token)})

        refresh_url = "/auth/api/v1/token/refresh/"
        resfresh_response = self.client.post(refresh_url, {"refresh_token": str(self.refresh_token)})

        assert response.status_code == 204
        assert resfresh_response.status_code in (400, 401)
