"""
OKJ PLATFORM - INTERACTIONS SERVICE TESTS (apps/interactions/tests/test_services.py)
"""

import pytest
from accounts.models import User
from posts.models import Post
from interactions.services import InteractionService
from interactions.models import PostLike, PostBookmark


@pytest.mark.django_db
class TestInteractionService:
    def test_like_toggle_and_duplicate_prevention(self):
        user = User.objects.create_user(phone_number="+998903334499", okj_id="OKJ-90003")
        post = Post.objects.create(user=user, post_type=Post.PostType.SHOWCASE, slug="like-test-showcase")

        # 1-marta bosamiz (Like)
        like1, created1 = InteractionService.toggle_like(user=user, post=post)
        assert created1 is True
        assert PostLike.objects.filter(post=post, is_deleted=False).count() == 1

        # 2-marta bosamiz (Unlike / Soft delete)
        like2, created2 = InteractionService.toggle_like(user=user, post=post)
        assert created2 is False
        assert PostLike.objects.filter(post=post, is_deleted=False).count() == 0

        # 3-marta bosamiz (Restore existing row - duplicate prevention)
        like3, created3 = InteractionService.toggle_like(user=user, post=post)
        assert created3 is True
        assert like3.id == like1.id
        assert PostLike.objects.filter(post=post, is_deleted=False).count() == 1

    def test_bookmark_flow(self):
        user = User.objects.create_user(phone_number="+998904445599", okj_id="OKJ-90004")
        post = Post.objects.create(user=user, post_type=Post.PostType.QUOTE, slug="bm-test-quote")

        bm, created = InteractionService.toggle_bookmark(user=user, post=post, collection_name="Eng sara")
        assert created is True
        assert bm.collection_name == "Eng sara"
