"""
OKJ PLATFORM - POSTS SERVICE TESTS (apps/posts/tests/test_services.py)
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from core.exceptions import ApplicationError
from accounts.models import User
from posts.models import Post
from posts.services import PostService


@pytest.mark.django_db
class TestPostService:
    def test_quote_requires_quote_text(self):
        user = User.objects.create_user(phone_number="+998903334455", okj_id="OKJ-80004")
        with pytest.raises(ApplicationError) as exc_info:
            PostService.create_post(
                user=user,
                post_type=Post.PostType.QUOTE,
                quote_text="",
            )
        assert exc_info.value.code == "QUOTE_TEXT_REQUIRED"

    def test_showcase_published_requires_image(self):
        user = User.objects.create_user(phone_number="+998903334456", okj_id="OKJ-80005")
        with pytest.raises(ApplicationError) as exc_info:
            PostService.create_post(
                user=user,
                post_type=Post.PostType.SHOWCASE,
                status=Post.Status.PUBLISHED,
                media_items=[],
            )
        assert exc_info.value.code == "SHOWCASE_IMAGE_REQUIRED"

    def test_thirty_minute_media_edit_lock(self):
        user = User.objects.create_user(phone_number="+998903334457", okj_id="OKJ-80006")
        post = PostService.create_post(
            user=user,
            post_type=Post.PostType.SHOWCASE,
            status=Post.Status.PUBLISHED,
            media_items=[{"image_url": "http://img.uz/1.jpg"}],
        )
        # Vaqtni 31 daqiqa oldinga siljitamiz
        Post.objects.filter(id=post.id).update(published_at=timezone.now() - timedelta(minutes=31))
        post.refresh_from_db()

        with pytest.raises(ApplicationError) as exc_info:
            PostService.update_post(post=post, media_items=[{"image_url": "http://img.uz/2.jpg"}])
        assert exc_info.value.code == "MEDIA_EDIT_EXPIRED"
