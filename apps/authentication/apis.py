"""
OKJ PLATFORM - AUTHENTICATION API VIEWS (apps/authentication/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha YENGIL VIEWLAR (Thin Views).
Ular faqat kiruvchi ma'lumotni serializer orqali validatsiya qilib,
to'g'ridan-to'g'ri `services.py` ga yuboradi.
"""

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from core.responses import APIResponse
from core.utils import get_client_ip
from .services import AuthService
from .selectors import AuthSelector
from .serializers import (
    RequestOTPSerializer,
    VerifyOTPSerializer,
    LoginPasswordSerializer,
    GoogleLoginSerializer,
    LogoutSerializer,
    UserDeviceSerializer,
    LoginHistorySerializer,
)


class RequestOTPApi(APIView):
    """SMS orqali 4 xonali tasdiqlash kodi so'rash API."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = AuthService.request_otp(**serializer.validated_data)
        # Test va lokal ishlab chiqish uchun kodni message da qaytaramiz
        return APIResponse(
            data={"expires_at": otp.expires_at, "dev_code": otp.code},
            message=f"{otp.phone_number} raqamiga tasdiqlash kodi yuborildi.",
        )


class VerifyOTPAndLoginApi(APIView):
    """OTP tasdiqlash va JWT Access/Refresh tokenlarni olish API."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip = get_client_ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "")

        tokens = AuthService.verify_otp_and_login(ip_address=ip, user_agent=ua, **serializer.validated_data)
        return APIResponse(data=tokens, message="Muvaffaqiyatli kirildi.", status_code=status.HTTP_200_OK)


class LoginPasswordApi(APIView):
    """An'anaviy telefon va parol orqali kirish API."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip = get_client_ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "")

        tokens = AuthService.login_with_password(ip_address=ip, user_agent=ua, **serializer.validated_data)
        return APIResponse(data=tokens, message="Muvaffaqiyatli kirildi.")


class GoogleLoginApi(APIView):
    """Google OAuth token orqali kirish / tayyorgarlik API."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip = get_client_ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "")

        tokens = AuthService.google_login_service(ip_address=ip, user_agent=ua, **serializer.validated_data)
        return APIResponse(data=tokens, message="Google orqali muvaffaqiyatli kirildi.")


class LogoutApi(APIView):
    """Joriy seans / qurilmadan chiqish API."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AuthService.logout_device(
            user=request.user,
            device_id=serializer.validated_data["device_id"],
            refresh_token=serializer.validated_data.get("refresh_token"),
        )
        return APIResponse(message="Tizimdan muvaffaqiyatli chiqildi.")


class LogoutAllDevicesApi(APIView):
    """Barcha faol seans / qurilmalardan chiqish API."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        count = AuthService.logout_all_devices(user=request.user)
        return APIResponse(message=f"Barcha qurilmalardan chiqildi ({count} ta seans yopildi).")


class UserDevicesApi(APIView):
    """Kitobxonning faol seans / qurilmalari ro'yxati API."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        devices = AuthSelector.get_user_devices(user_id=request.user.id)
        serializer = UserDeviceSerializer(devices, many=True)
        return APIResponse(data=serializer.data)


class LoginHistoryApi(APIView):
    """Kitobxonning kirish urinishlari auditi ro'yxati API."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = AuthSelector.get_login_history(user_id=request.user.id)
        serializer = LoginHistorySerializer(history, many=True)
        return APIResponse(data=serializer.data)
