"""
OKJ PLATFORM - AUTHENTICATION MODEL TESTS (apps/authentication/tests/test_models.py)
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from accounts.models import User
from authentication.models import OTPCode, UserDevice, LoginHistory


@pytest.mark.django_db
class TestAuthenticationModels:
    def test_otp_code_expiry(self):
        otp = OTPCode.objects.create(
            phone_number="+998901112233",
            code="1234",
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        assert otp.is_expired is True

    def test_user_device_creation(self):
        user = User.objects.create_user(phone_number="+998902223344", okj_id="OKJ-90001")
        device = UserDevice.objects.create(
            user=user,
            device_id="iphone_15_pro_uid",
            device_type=UserDevice.DeviceType.IOS,
        )
        assert str(device).startswith(user.username)
        assert device.is_active is True
