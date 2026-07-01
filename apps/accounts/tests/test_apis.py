"""
OKJ PLATFORM - ACCOUNTS API TESTS (apps/accounts/tests/test_apis.py)
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import District
from accounts.services import UserService


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestAccountsAPI:
    def test_district_list_api(self, api_client):
        District.objects.create(name="Olmazor", region_name="Toshkent")
        response = api_client.get("/api/v1/accounts/districts/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True
        assert len(response.json()["data"]) == 1

    def test_register_reader_api(self, api_client):
        district = District.objects.create(name="Bektemir", region_name="Toshkent")
        payload = {
            "phone_number": "+998931112233",
            "first_name": "Bobur",
            "district_id": district.id,
        }
        response = api_client.post("/api/v1/accounts/register/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["success"] is True
        assert body["data"]["phone_number"] == "+998931112233"
        assert "OKJ-" in body["data"]["okj_id"]

    def test_profile_api_unauthenticated_blocked(self, api_client):
        response = api_client.get("/api/v1/accounts/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_api_authenticated_success(self, api_client):
        user = UserService.register_reader(phone_number="+998934445566")
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/accounts/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["okj_id"] == user.okj_id
