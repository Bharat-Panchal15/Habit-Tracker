from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, GuestUserView, LogoutView


urlpatterns = [
    path("api/v1/guest/", GuestUserView.as_view(), name="guest"),
    path("api/v1/register/", RegisterView.as_view(), name="register"),
    path("api/v1/login/", LoginView.as_view(), name="login"),
    path("api/v1/logout/", LogoutView.as_view(), name="logout"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]