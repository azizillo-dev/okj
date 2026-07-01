import pytest
from django.contrib.auth import get_user_model
from posts.models import Post
from posts.services import PostService
from feed_ranking.selectors import FeedRankingSelector
from feed_ranking.services import FeedCacheAdapter

User = get_user_model()


@pytest.mark.django_db
class TestFeedRankingSelector:
    def test_get_ranked_feed_cache_miss_fallback(self):
        user = User.objects.create_user(phone_number="+998901112210", okj_id="OKJ-90010")
        post = PostService.create_post(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Kesh miss testi uchun post",
            status=Post.Status.PUBLISHED,
        )
        Post.objects.filter(id=post.id).update(moderation_status=Post.ModerationStatus.APPROVED)

        # Keshni tozalaymiz (Cache Miss)
        cache_key = f"user:feed:cache:{user.id}"
        FeedCacheAdapter.delete(cache_key)
        assert len(FeedCacheAdapter.zrevrange(cache_key, 0, 10)) == 0

        # Selektorni chaqiramiz
        posts = FeedRankingSelector.get_ranked_feed_for_user(user=user, page=1, page_size=20)
        assert len(posts) >= 1
        assert posts[0].id == post.id

        # Endi kesh to'lgan bo'lishi kerak
        assert len(FeedCacheAdapter.zrevrange(cache_key, 0, 10)) >= 1
