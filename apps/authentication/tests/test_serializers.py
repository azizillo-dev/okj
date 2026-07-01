"""
OKJ PLATFORM - AUTHENTICATION SERIALIZER TESTS (apps/authentication/tests/test_serializers.py)
"""

import pytest
from authentication.serializers import RequestOTPSerializer, VerifyOTPSerializer


class TestAuthSerializers:
    def test_request_otp_serializer_valid(self):
        serializer = RequestOTPSerializer(data={"phone_number": "+998901234567"})
        assert serializer.is_valid() is True

    def test_request_otp_serializer_invalid_phone(self):
        serializer = RequestOTPSerializer(data={"phone_number": "12345"})
        assert serializer.is_valid() is False
        assert "phone_number" in serializer.errors
