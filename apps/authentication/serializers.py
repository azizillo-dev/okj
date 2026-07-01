"""
OKJ PLATFORM - AUTHENTICATION SERIALIZERS (apps/authentication/serializers.py)
Nega bu fayl kerak: OTP so'rash, tasdiqlash va parolli kirish payloadlarini validatsiya qilish.
"""

from rest_framework import serializers
from .models import OTPCode, UserDevice, LoginHistory
from .validators import validate_auth_phone_number, validate_otp_code_format


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[validate_auth_phone_number])
    purpose = serializers.ChoiceField(choices=OTPCode.Purpose.choices, default=OTPCode.Purpose.LOGIN)


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[validate_auth_phone_number])
    code = serializers.CharField(max_length=10, validators=[validate_otp_code_format])
    device_id = serializers.CharField(max_length=255, default="web_browser")
    device_type = serializers.ChoiceField(choices=UserDevice.DeviceType.choices, default=UserDevice.DeviceType.WEB)
    device_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    fcm_token = serializers.CharField(max_length=500, required=False, allow_blank=True)


class LoginPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, validators=[validate_auth_phone_number])
    password = serializers.CharField(write_only=True)
    device_id = serializers.CharField(max_length=255, default="web_browser")
    device_type = serializers.ChoiceField(choices=UserDevice.DeviceType.choices, default=UserDevice.DeviceType.WEB)
    device_name = serializers.CharField(max_length=255, required=False, allow_blank=True)


class GoogleLoginSerializer(serializers.Serializer):
    google_id = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False, allow_blank=True)
    full_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    device_id = serializers.CharField(max_length=255, default="google_device")
    device_type = serializers.ChoiceField(choices=UserDevice.DeviceType.choices, default=UserDevice.DeviceType.WEB)


class LogoutSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=255)
    refresh_token = serializers.CharField(required=False, allow_blank=True)


class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDevice
        fields = ("id", "device_id", "device_type", "device_name", "is_trusted", "is_active", "last_active_at")


class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = ("id", "phone_number", "ip_address", "user_agent", "status", "failure_reason", "created_at")
