"""
OKJ PLATFORM - INTERACTIONS MODEL TESTS (apps/interactions/tests/test_models.py)
"""

import pytest
from accounts.models import User
from posts.models import Post
from interactions.models import PostLike, PostBookmark


@pytest.mark.django_db
class TestInteractionsModels:
    def test_post_like_and_bookmark_creation(self):
        user = User.objects.create_user(phone_number="+998901112299", okj_id="OKJ-90001")
        post = Post.objects.create(user=user, post_type=Post.PostType.QUOTE, slug="like-test-quote")

        like = PostLike.objects.create(user=user, post=post)
        assert str(like) == f"{user.username} ❤️ {post.id}"

        bookmark = PostBookmark.objects.create(user=user, post=post, collection_name="O'qishim shart")
        assert str(bookmark) == f"{user.username} 🔖 {post.id} (O'qishim shart)"
