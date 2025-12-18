import pytest
from rest_framework.test import APIClient
from users.models import User

@pytest.mark.django_db
class TestRegisterAPI:
    """Test suite for the Register API endpoint."""
    def setup_method(self):
        self.client = APIClient()
        self.url = "/auth/api/v1/register/"
    
    def test_register_user_success(self):
        """Ensure a user can successfully register with valid data."""
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }

        response = self.client.post(self.url, payload)
        data = response.json()
        user = data["user"]
        
        assert response.status_code == 201
        assert "user" in data
        assert "access" in data
        assert "refresh" in data
        assert user["username"] == "testuser"
        assert user["email"] == payload["email"]
        assert user["is_guest"] is False
        assert User.objects.filter(username="testuser").exists()
    
    def test_register_returns_token_pair(self):
        """Verify registration returns access and refresh JWT tokens."""
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }

        response = self.client.post(self.url, payload)
        data = response.json()

        assert response.status_code == 201
        assert "user" in data
        assert "access" in data
        assert "refresh" in data
        assert isinstance(data["access"], str)
        assert isinstance(data["refresh"], str)
    
    def test_register_username_contain_at_symbol(self):
        """Usernames containing '@' should fail validation."""
        payload = {
            "username": "test@user",
            "email": "test@example.com",
            "password": "password123"
        }

        response = self.client.post(self.url, payload)
        data = response.json()

        assert response.status_code == 400
        assert "username" in data
        assert data["username"][0] == "Username cannot contain '@' symbol"
    
    def test_register_username_looks_like_email(self):
        """Usernames that look like an email address must fail validation."""
        payload = {
            "username": "test@user.com",
            "email": "test@example.com",
            "password": "password123"
        }

        response = self.client.post(self.url, payload)
        data = response.json()

        assert response.status_code == 400
        assert "username" in data
        assert data["username"][0] == "Username cannot look like an email"

    def test_register_duplicate_email_fails(self):
        """Registration should fail when using an email that already exists."""
        User.objects.create_user(username="testuser1", email="test@example.com", password="password123")

        payload = {
            "username": "testuser2",
            "email": "test@example.com",
            "password": "password123"
        }

        response = self.client.post(self.url, payload)
        data = response.json()

        assert response.status_code == 400
        assert "email" in data
        assert data["email"][0] == "Email is already taken"
    
    def test_register_invalid_email_format(self):
        """Invalid email formats must trigger validation errors."""
        payload = {
            "username": "testuser",
            "email": "invalid-email-format",
            "password": "password123"
        }

        response = self.client.post(self.url, payload)
        data = response.json()

        assert response.status_code == 400
        assert "email" in data
    
    def test_register_missing_username_fails(self):
        """Missing username should return a validation error."""
        payload = {
            "email":"test@example.com",
            "password": "password123",
        }

        response = self.client.post(self.url, payload)
        data = response.json()

        assert response.status_code == 400
        assert "username" in data # missing username field

    def test_register_missing_email_fails(self):
        """Missing email should return a validation error."""
        payload = {
            "username": "testuser",
            "password": "password123",
        }

        response = self.client.post(self.url, payload)
        data = response.json()

        assert response.status_code == 400
        assert "email" in data # missing email field

    def test_register_missing_password(self):
        """Missing password should return a validation error."""
        payload = {
            "username": "testuser",
            "email": "test@example.com",
        }

        response = self.client.post(self.url, payload)

        assert response.status_code == 400
        assert "password" in response.json()

    def test_authenticated_user_cannot_register(self):
        """Authenticated users should not be allowed to register again."""
        """Logged-in users should NOT be allowed to register again."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        login_url = "/auth/api/v1/login/"
        login_response = self.client.post(login_url, {
            "identifier": "testuser",
            "password": "password123"
        })
        assert login_response.status_code == 200
        data = login_response.json()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {data['access']}")

        payload = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password456",
        }
        response = self.client.post(self.url, payload)

        assert response.status_code == 403  # Forbidden for authenticated users
