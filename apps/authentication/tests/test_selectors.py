"""
OKJ PLATFORM - AUTHENTICATION SELECTOR TESTS (apps/authentication/tests/test_selectors.py)
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from authentication.models import OTPCode
from authentication.selectors import AuthSelector


@pytest.mark.django_db
class TestAuthSelector:
    def test_get_valid_otp(self):
        otp = OTPCode.objects.create(
            phone_number="+998903334455",
            code="9988",
            expires_at=timezone.now() + timedelta(minutes=5),
            is_used=False,
        )
        found = AuthSelector.get_valid_otp("+998903334455", "9988")
        assert found is not None
        assert found.id == otp.id

    def test_used_otp_returns_none(self):
        OTPCode.objects.create(
            phone_number="+998904445566",
            code="7777",
            expires_at=timezone.now() + timedelta(minutes=5),
            is_used=True,
        )
        found = AuthSelector.get_valid_otp("+998904445566", "7777")
        assert found is None
