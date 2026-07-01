import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from posts.models import Post
from posts.services import PostService

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestFeedRankingAPI:
    def test_user_ranked_feed_unauthenticated(self, api_client):
        response = api_client.get("/api/v1/posts/feed/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_ranked_feed_authenticated_success(self, api_client):
        user = User.objects.create_user(phone_number="+998901112220", okj_id="OKJ-90020")
        api_client.force_authenticate(user=user)

        post = PostService.create_post(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="API feed testi",
            status=Post.Status.PUBLISHED,
        )
        Post.objects.filter(id=post.id).update(moderation_status=Post.ModerationStatus.APPROVED)

        response = api_client.get("/api/v1/posts/feed/?page=1&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["results"]) >= 1
