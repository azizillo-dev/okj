"""
OKJ PLATFORM - COMMENTS API TESTS (apps/comments/tests/test_apis.py)
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
class TestCommentsAPI:
    def test_comment_list_create_delete_api(self, api_client):
        user = UserService.register_reader(phone_number="+998905556611")
        api_client.force_authenticate(user=user)

        post = Post.objects.create(user=user, post_type=Post.PostType.QUOTE, slug="api-test-comment-quote")

        # Izoh yozamiz
        resp_post = api_client.post(f"/api/v1/posts/{post.id}/comments/", {"text": "Ajoyib izoh"}, format="json")
        assert resp_post.status_code == status.HTTP_201_CREATED
        comment_id = resp_post.json()["data"]["id"]

        # Izohlar ro'yxatini o'qiymiz
        resp_get = api_client.get(f"/api/v1/posts/{post.id}/comments/")
        assert resp_get.status_code == status.HTTP_200_OK
        assert len(resp_get.json()["data"]) == 1

        # Izohni o'chiramiz
        resp_del = api_client.delete(f"/api/v1/comments/{comment_id}/")
        assert resp_del.status_code == status.HTTP_200_OK
