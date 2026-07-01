"""
OKJ PLATFORM - POSTS API TESTS (apps/posts/tests/test_apis.py)
"""

import pytest
from rest_framework.test import APIClient
from rest_framework import status
from accounts.services import UserService
from posts.models import Post


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestPostsAPI:
    def test_post_feed_api_public(self, api_client):
        user = UserService.register_reader(phone_number="+998905556677")
        Post.objects.create(
            user=user,
            post_type=Post.PostType.QUOTE,
            status=Post.Status.PUBLISHED,
            moderation_status=Post.ModerationStatus.APPROVED,
            quote_text="Iqtibos test API",
            slug="iqtibos-test-api",
        )
        response = api_client.get("/api/v1/posts/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["count"] >= 1

    def test_create_post_api_authenticated(self, api_client):
        user = UserService.register_reader(phone_number="+998905556678")
        api_client.force_authenticate(user=user)

        payload = {
            "post_type": "QUOTE",
            "status": "PUBLISHED",
            "quote_text": "Haqiqiy bilim kitobdan olindi.",
        }
        response = api_client.post("/api/v1/posts/", payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["data"]["post_type"] == "QUOTE"
