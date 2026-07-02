"""
OKJ PLATFORM - AUTHENTICATION SERVICE TESTS (apps/authentication/tests/test_services.py)
"""

import pytest
from core.exceptions import ApplicationError
from authentication.services import AuthService
from authentication.models import LoginHistory


@pytest.mark.django_db
class TestAuthService:
    def test_request_and_verify_otp_passwordless(self):
        otp = AuthService.request_otp(phone_number="+998905556677")
        assert len(otp.code) == 4
        assert otp.is_used is False

        result = AuthService.verify_otp_and_login(
            phone_number="+998905556677",
            code=otp.code,
            device_id="test_iphone",
        )
        assert "access" in result
        assert "refresh" in result
        assert "okj_id" in result

        # Kod ishlatilgani nazorat qilinadi
        otp.refresh_from_db()
        assert otp.is_used is True

    def test_brute_force_lockout_triggers(self):
        # 5 ta xato urinish yozamiz
        for _ in range(5):
            LoginHistory.objects.create(
                phone_number="+998907778899",
                status=LoginHistory.Status.FAILED,
            )
        with pytest.raises(ApplicationError) as exc_info:
            AuthService.request_otp(phone_number="+998907778899")
        assert exc_info.value.status_code == 429
