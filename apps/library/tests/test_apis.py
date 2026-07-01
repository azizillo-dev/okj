"""
OKJ PLATFORM - LIBRARY API TESTS (apps/library/tests/test_apis.py)
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from accounts.services import UserService
from books.models import Book
from library.models import LibraryItem


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestLibraryAPI:
    def test_user_shelf_api(self, api_client):
        user = UserService.register_reader(phone_number="+998905554433")
        api_client.force_authenticate(user=user)

        book = Book.objects.create(title="Boburnoma", slug="boburnoma")
        LibraryItem.objects.create(user=user, book=book, status=LibraryItem.ReadingStatus.READING)

        response = api_client.get("/api/v1/library/shelf/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["count"] == 1

    def test_add_to_shelf_api(self, api_client):
        user = UserService.register_reader(phone_number="+998905554434")
        api_client.force_authenticate(user=user)

        book = Book.objects.create(title="Zararsiz Odatlar", slug="zararsiz-odatlar", verification_status="VERIFIED")
        payload = {"book_id": str(book.id), "status": "WANT_TO_READ"}

        response = api_client.post("/api/v1/library/shelf/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["status"] == "WANT_TO_READ"
