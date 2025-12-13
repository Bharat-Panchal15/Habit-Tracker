from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from users.permissions import IsAnonymous
from users.models import User
from users.serializers import UserSerializer, GuestUserSerializer, RegisterSerializer, LoginSerializer, LogoutSerializer

# Helper: build token pair for a user
def _get_token_pair_for_user(user: User):
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    return str(access), str(refresh)

# Create your views here.

class GuestUserView(APIView):
    """
    Guest user creation endpoint.

    Permission: IsAnonymous

    POST Response:
    {
    "user": { ... user profile ... },
    "access": "<access_token>",
    "refresh": "<refresh_token>"
    }
    """
    permission_classes = [IsAnonymous]

    def post(self, request):
        serializer = GuestUserSerializer(data=request.data or {})
        if serializer.is_valid():
            user = serializer.save()
            access_token, refresh_token = _get_token_pair_for_user(user)
            user_data = UserSerializer(user, context={"request": request}).data

            return Response(
                {
                    "user": user_data,
                    "access": access_token,
                    "refresh": refresh_token,
                }, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    """
    User registration endpoint.

    Methods:
    - POST /api/{version}/register/ -> Create a new user account

    Permission: IsAnonymous

    Request body:
    {
      "username": "john_doe",
      "email": "john@example.com",
      "password": "secure_password"
    }

    Response:
    {
      "user": { ... user profile ... },
      "access": "<access_token>",
      "refresh": "<refresh_token>"
    }

    Validation:
    - Username cannot contain '@' or look like an email.
    - Email must be unique.
    - Password is hashed before storage.
    """
    permission_classes = [IsAnonymous]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data or {})
        if serializer.is_valid():
            user = serializer.save()
            access_token, refresh_token = _get_token_pair_for_user(user)
            user_data = UserSerializer(user, context={"request": request}).data

            return Response(
                {
                    "user": user_data,
                    "access": access_token,
                    "refresh": refresh_token,
                }, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    User login endpoint.

    Methods:
    - POST /api/{version}/login/ -> Authenticate user and issue tokens

    Permission: IsAnonymous

    Request body:
    {
      "identifier": "john_doe",   (can be username or email)
      "password": "secure_password"
    }

    Response:
    {
      "user": { ... user profile ... },
      "access": "<access_token>",
      "refresh": "<refresh_token>"
    }

    Notes:
    - Identifier can be either username or email.
    - Returns 200 OK with tokens on successful login.
    """
    permission_classes = [IsAnonymous]

    def post(self, request):
        serializer = LoginSerializer(data=request.data or {})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            access_token, refresh_token = _get_token_pair_for_user(user)
            user_data = UserSerializer(user, context={"request": request}).data

            return Response(
                {
                    "user": user_data,
                    "access": access_token,
                    "refresh": refresh_token,
                }, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """
    User logout endpoint.

    Methods:
    - POST /api/{version}/logout/ -> Blacklist refresh token

    Permission: IsAuthenticated

    Request body:
    {
      "refresh_token": "<refresh_token>"
    }

    Response: 204 No Content on success

    Notes:
    - Requires SimpleJWT token_blacklist app to be enabled in INSTALLED_APPS.
    - Blacklisting prevents token reuse after logout.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data or {})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)