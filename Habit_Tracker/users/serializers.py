from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
import random
import string
import re

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model. Displays user profile and guest expiry info."""
    guest_days_left = serializers.ReadOnlyField()
    is_guest_expired = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ["id","username","email","is_guest","notifications_enabled","created_on","guest_days_left","is_guest_expired",]
        read_only_fields = ["is_guest","guest_days_left","is_guest_expired"]

class GuestUserSerializer(serializers.Serializer):
    """Creates a temporary guest user with a random username and password. This serializer accepts no input fields; it only generates a guest account."""
    def create(self, validated_data):
        """Generate random guest credentials and create User instance."""
        random_str = "".join(random.choices(string.ascii_letters + string.digits,k=8))
        username = f"Guest_{random_str}"
        password = get_random_string(15)

        user = User.objects.create_user(username=username,password=password, is_guest=True)

        return user

class RegisterSerializer(serializers.ModelSerializer):
    """Validates and creates new user accounts with email/password."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["username","email","password"]
    
    def validate_username(self, username):
        """Ensure username doesn't contain '@' or email patterns."""
        if re.match(r".+@.+\..+",username): # Pattern: something@something.something
            raise serializers.ValidationError("Username cannot look like an email")
        
        if "@" in username:
            raise serializers.ValidationError("Username cannot contain '@' symbol")
        
        username = username.strip()
        return username

    def validate_email(self, email):
        """Ensure email is unique."""
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email is already taken")
        return email
    
    def create(self, validated_data):
        """Create user with hashed password."""
        password = validated_data.pop("password")

        user = User.objects.create_user(**validated_data, password=password)

        return user

class LoginSerializer(serializers.Serializer):
    """Authenticates a user using username/email and password. Does NOT generate tokens — views handle token issuing."""
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Verify credentials and attach authenticated user to data."""
        identifier = data.get("identifier")
        password = data.get("password")

        if "@" in identifier:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid login credentials")
        else:
            try:
                user = User.objects.get(username=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid login credentials")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid login credentials")
        
        data["user"] = user
        return data

class LogoutSerializer(serializers.Serializer):
    """Blacklists a JWT refresh token to log the user out. Requires SimpleJWT token_blacklist app to be enabled."""
    refresh_token = serializers.CharField()
    default_error_messages = {
        "invalid": "Invalid or expired token"
    }

    def validate(self, data):
        """Store refresh token for blacklisting."""
        self.refresh_token = data["refresh_token"]
        return data
    
    def save(self, **kwargs):
        """Add refresh token to blacklist."""
        try:
            RefreshToken(self.refresh_token).blacklist()
        except Exception:
            self.fail("invalid")
