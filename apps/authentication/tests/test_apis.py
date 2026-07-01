"""
OKJ PLATFORM - AUTHENTICATION API TESTS (apps/authentication/tests/test_apis.py)
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from authentication.services import AuthService


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestAuthAPI:
    def test_request_otp_api(self, api_client):
        response = api_client.post(
            "/api/v1/auth/otp/request/",
            {"phone_number": "+998909998877"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True
        assert "dev_code" in response.json()["data"]

    def test_verify_otp_api_success(self, api_client):
        otp = AuthService.request_otp(phone_number="+998908887766")
        response = api_client.post(
            "/api/v1/auth/otp/verify/",
            {
                "phone_number": "+998908887766",
                "code": otp.code,
                "device_id": "test_device_api",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.json()["data"]
