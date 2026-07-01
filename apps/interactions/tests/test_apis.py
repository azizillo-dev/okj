"""
OKJ PLATFORM - INTERACTIONS API TESTS (apps/interactions/tests/test_apis.py)
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
class TestInteractionsAPI:
    def test_like_and_bookmark_toggle_api(self, api_client):
        user = UserService.register_reader(phone_number="+998905556699")
        api_client.force_authenticate(user=user)

        post = Post.objects.create(user=user, post_type=Post.PostType.QUOTE, slug="api-test-quote")

        # Like bosamiz
        resp_like = api_client.post(f"/api/v1/posts/{post.id}/like/")
        assert resp_like.status_code == status.HTTP_201_CREATED

        # Unlike qilamiz
        resp_unlike = api_client.delete(f"/api/v1/posts/{post.id}/like/")
        assert resp_unlike.status_code == status.HTTP_200_OK

        # Bookmark bosamiz
        resp_bm = api_client.post(f"/api/v1/posts/{post.id}/bookmark/", {"collection_name": "Asosiy"}, format="json")
        assert resp_bm.status_code == status.HTTP_201_CREATED
