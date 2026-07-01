"""
OKJ PLATFORM - POSTS SELECTOR TESTS (apps/posts/tests/test_selectors.py)
"""

import pytest
from accounts.models import User
from posts.models import Post
from posts.selectors import PostSelector


@pytest.mark.django_db
class TestPostSelector:
    def test_get_feed_posts_filtered(self):
        user = User.objects.create_user(phone_number="+998902224455", okj_id="OKJ-80003")
        Post.objects.create(
            user=user,
            post_type=Post.PostType.QUOTE,
            status=Post.Status.PUBLISHED,
            moderation_status=Post.ModerationStatus.APPROVED,
            quote_text="Iqtibos 1",
            slug="iqtibos-1",
            hashtags="#kitob #adabiyot",
        )
        Post.objects.create(
            user=user,
            post_type=Post.PostType.REVIEW,
            status=Post.Status.PUBLISHED,
            moderation_status=Post.ModerationStatus.APPROVED,
            user_rating=5,
            slug="taqriz-1",
        )

        quote_feed = PostSelector.get_feed_posts(post_type="QUOTE")
        assert len(quote_feed) == 1
        assert quote_feed[0].post_type == "QUOTE"

        hashtag_feed = PostSelector.get_feed_posts(hashtag="kitob")
        assert len(hashtag_feed) == 1
