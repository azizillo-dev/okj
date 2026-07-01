"""
OKJ PLATFORM - BOOKS API TESTS (apps/books/tests/test_apis.py)
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from accounts.services import UserService
from books.models import Book


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestBooksAPI:
    def test_book_list_api(self, api_client):
        Book.objects.create(
            title="Navoiy",
            slug="navoiy",
            verification_status=Book.VerificationStatus.VERIFIED,
        )
        response = api_client.get("/api/v1/books/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["count"] == 1

    def test_create_book_api(self, api_client):
        user = UserService.register_reader(phone_number="+998951112233")
        api_client.force_authenticate(user=user)

        payload = {"title": "Temur tuzuklari", "page_count": 150}
        response = api_client.post("/api/v1/books/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["slug"] == "temur-tuzuklari"
