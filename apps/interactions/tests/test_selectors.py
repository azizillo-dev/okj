"""
OKJ PLATFORM - INTERACTIONS SELECTOR TESTS (apps/interactions/tests/test_selectors.py)
"""

import pytest
from accounts.models import User
from posts.models import Post
from interactions.models import PostLike, PostBookmark
from interactions.selectors import InteractionSelector


@pytest.mark.django_db
class TestInteractionSelector:
    def test_get_post_likes_and_checks(self):
        user = User.objects.create_user(phone_number="+998902223399", okj_id="OKJ-90002")
        post = Post.objects.create(user=user, post_type=Post.PostType.REVIEW, slug="like-test-review")

        PostLike.objects.create(user=user, post=post)
        PostBookmark.objects.create(user=user, post=post)

        likes = InteractionSelector.get_post_likes(post)
        assert len(likes) == 1
        assert InteractionSelector.is_post_liked_by_user(post, user) is True
        assert InteractionSelector.is_post_bookmarked_by_user(post, user) is True
