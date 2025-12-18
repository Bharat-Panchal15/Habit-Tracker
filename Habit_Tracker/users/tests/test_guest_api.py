import pytest
from rest_framework.test import APIClient
from users.models import User

@pytest.mark.django_db
class TestGuestUserAPI:
    """Tests for guest user creation endpoint."""
    def setup_method(self):
        self.client = APIClient()
        self.url = "/auth/api/v1/guest/"

    def test_create_guest_user_success(self):
        """Test successful guest user creation."""
        response = self.client.post(self.url, {})
        data = response.json()
        user_data = data["user"]

        assert response.status_code == 201
        assert "user" in data
        assert "access" in data
        assert "refresh" in data
        assert user_data["is_guest"] is True
        assert user_data["username"].startswith("Guest_")
        assert User.objects.filter(id=user_data["id"]).exists()
    
    def test_guest_user_returns_tokens(self):
        """Test that access and refresh tokens are returned upon guest user creation."""
        response = self.client.post(self.url, {})
        data = response.json()

        assert response.status_code == 201
        assert "access" in data
        assert "refresh" in data
        assert isinstance(data["access"], str)
        assert isinstance(data["refresh"], str)

    def test_guest_user_fields(self):
        """Test that the guest user has correct fields set."""
        response = self.client.post(self.url, {})
        data = response.json()
        user_data = data["user"]

        assert response.status_code == 201
        assert "id" in user_data
        assert "username" in user_data
        assert "email" in user_data
        assert "password" not in user_data
        assert "is_guest_expired" in user_data
        assert "guest_days_left" in user_data
        assert user_data.get("is_guest") is True
    
    def test_guest_expiry(self):
        """Test that guest user expiry fields are correct."""
        response = self.client.post(self.url, {})
        data = response.json()
        user_data = data["user"]

        assert response.status_code == 201
        assert user_data["is_guest_expired"] is False
        assert user_data["guest_days_left"] == 7
    
    def test_multiple_guest_user_creations(self):
        """Test that multiple guest users can be created with unique usernames."""
        response1 = self.client.post(self.url, {})
        response2 = self.client.post(self.url, {})
        data1 = response1.json()
        data2 = response2.json()
        user1_data = data1["user"]
        user2_data = data2["user"]

        assert response1.status_code == 201
        assert response2.status_code == 201
        assert user1_data["username"] != user2_data["username"]
        assert User.objects.filter(id=user1_data["id"]).exists()
        assert User.objects.filter(id=user2_data["id"]).exists()
    
    def test_guest_user_login_denied(self):
        """Test that guest users cannot log in via standard login endpoint."""
        # Create a guest user first
        guest_response = self.client.post(self.url, {})
        guest_data = guest_response.json()
        guest_username = guest_data["user"]["username"]

        # Attempt to log in with guest credentials
        login_url = "/auth/api/v1/login/"
        login_response = self.client.post(login_url, {"username": guest_username, "password": "anything"})
        
        assert login_response.status_code in (400,401) # Login should fail