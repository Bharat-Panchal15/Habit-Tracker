from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
import random
import string
import re

class UserSerializer(serializers.ModelSerializer):
    guest_days_left = serializers.ReadOnlyField()
    is_guest_expired = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ["id","username","email","is_guest","notifications_enabled","created_on","guest_days_left","is_guest_expired",]
        read_only_fields = ["is_guest","guest_days_left","is_guest_expired"]

class GuestUserSerializer(serializers.Serializer):
    def create(self, validated_data):
        random_str = "".join(random.choices(string.ascii_letters + string.digits,k=8))
        username = f"Guest_{random_str}"

        user = User.objects.create_user(username=username,password=User.objects.make_random_password(), is_guest=True)

        return user

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["username","email","password"]
    
    def validate_username(self, username):
        if "@" in username:
            raise serializers.ValidationError("Username cannot contain '@' symbol")
        
        if re.match(r".+@.+\..+",username): # Pattern: something@something.something
            raise serializers.ValidationError("Username cannot look like an email")
        
        username = username.strip()
        return username

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email is already taken")
        return email
    
    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(**validated_data, password=password)

        return user

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
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
    refresh_token = serializers.CharField()

    def validate(self, data):
        self.refresh_token = data["refresh_token"]
        return data
    
    def save(self, **kwargs):
        try:
            RefreshToken(self.refresh_token).blacklist()
        except Exception:
            self.fail("BAD Token")