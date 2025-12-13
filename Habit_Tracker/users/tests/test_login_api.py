import pytest
from rest_framework.test import APIClient
from users.models import User

@pytest.mark.django_db
class TestLoginAPI:
    """Test suite for the Login API endpoint."""
    def setup_method(self):
        self.client = APIClient()
        self.login_url = "/auth/api/v1/login/"
    
    def test_login_with_username_success(self):
        """A user can log in successfully using their username and password."""
        User.objects.create_user(username="testuser", email="test@example.com", password="password123")

        payload = {
            "identifier": "testuser",
            "password": "password123"
        }

        response = self.client.post(self.login_url, payload)
        data = response.json()

        assert response.status_code == 200
        assert "user" in data
        assert "access" in data
        assert "refresh" in data
        assert data["user"]["username"] == "testuser"

    def test_login_with_email_success(self):
        """A user can log in successfully using their email and password."""
        User.objects.create_user(username="testuser", email="test@example.com", password="password123")

        payload = {
            "identifier": "test@example.com",
            "password": "password123"
        }

        response = self.client.post(self.login_url, payload)
        data = response.json()

        assert response.status_code == 200
        assert "user" in data
        assert "access" in data
        assert "refresh" in data
        assert data["user"]["email"] == "test@example.com"

    def test_login_invalid_password(self):
        """Login must fail when the password is incorrect."""
        User.objects.create_user(username="testuser", email="test@example.com", password="password123")

        payload = {
            "identifier": "testuser",
            "password": "password456"
        }

        response = self.client.post(self.login_url, payload)
        data = response.json()

        assert response.status_code == 400
        assert "non_field_errors" in data
        assert data["non_field_errors"][0] == "Invalid login credentials"

    def test_login_nonexistent_identifier(self):
        """Login must fail when the username or email does not exist."""
        payload = {
            "identifier": "testuser",
            "password": "password123"
        }

        response = self.client.post(self.login_url, payload)
        data = response.json()

        assert response.status_code == 400
        assert "non_field_errors" in data
        assert data["non_field_errors"][0] == "Invalid login credentials"

    def test_login_missing_identifier(self):
        """Login must fail when the identifier field is missing."""
        payload = {
            "password": "password123"
        }

        response = self.client.post(self.login_url, payload)
        data = response.json()

        assert response.status_code == 400
        assert "identifier" in data

    def test_login_authenticated_user_denied(self):
        """Authenticated users must not be allowed to access the login endpoint."""
        user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")

        response = self.client.post(self.login_url, {"identifier": "testuser","password": "password123"})
        access_token = response.json().get("access")

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.post(self.login_url, {"identifier": "testuser","password": "password123"})

        assert response.status_code == 403
        assert "detail" in response.json() # DRF returns a standard permission error payload
    
    def test_login_returns_token_pair(self):
        """Successful login must return both access and refresh tokens."""
        User.objects.create_user(username="testuser", email="test@example.com", password="password123")

        payload = {
            "identifier": "test@example.com",
            "password": "password123",
        }

        response = self.client.post(self.login_url, payload)
        data = response.json()

        assert response.status_code == 200
        assert "access" in data
        assert "refresh" in data
        assert isinstance(data["access"], str)
        assert isinstance(data["refresh"], str)