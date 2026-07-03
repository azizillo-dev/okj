"""
OKJ PLATFORM - AUTHENTICATION URLS (apps/authentication/urls.py)
Nega bu fayl kerak: /api/v1/auth/ ostidagi marshrutlarni aniqlash.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .apis import (
    RequestOTPApi,
    VerifyOTPAndLoginApi,
    LoginPasswordApi,
    GoogleLoginApi,
    LogoutApi,
    LogoutAllDevicesApi,
    UserDevicesApi,
    LoginHistoryApi,
)

urlpatterns = [
    path("otp/request/", RequestOTPApi.as_view(), name="auth-otp-request"),
    path("otp/request", RequestOTPApi.as_view()),
    path("otp/verify/", VerifyOTPAndLoginApi.as_view(), name="auth-otp-verify"),
    path("otp/verify", VerifyOTPAndLoginApi.as_view()),
    path("login/password/", LoginPasswordApi.as_view(), name="auth-login-password"),
    path("login/password", LoginPasswordApi.as_view()),
    path("login/google/", GoogleLoginApi.as_view(), name="auth-login-google"),
    path("token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    path("logout/", LogoutApi.as_view(), name="auth-logout"),
    path("logout", LogoutApi.as_view()),
    path("logout/all/", LogoutAllDevicesApi.as_view(), name="auth-logout-all"),
    path("devices/", UserDevicesApi.as_view(), name="auth-devices"),
    path("history/", LoginHistoryApi.as_view(), name="auth-history"),
]
