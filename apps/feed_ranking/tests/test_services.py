import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from posts.models import Post
from posts.services import PostService
from feed_ranking.services import FeedRankingService, FeedCacheAdapter

User = get_user_model()


@pytest.mark.django_db
class TestFeedRankingService:
    def test_calculate_post_score_base_weights(self):
        user = User.objects.create_user(phone_number="+998901112201", okj_id="OKJ-90001")
        now = timezone.now()

        review_post = Post.objects.create(
            user=user,
            post_type=Post.PostType.REVIEW,
            user_rating=5,
            title="Zur",
            content="Yaxshi kitob",
            slug="review-post-1",
        )
        quote_post = Post.objects.create(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Bilim kuchdir",
            slug="quote-post-1",
        )

        score_review = FeedRankingService.calculate_post_score(review_post, now=now)
        score_quote = FeedRankingService.calculate_post_score(quote_post, now=now)

        assert score_review > score_quote

    def test_time_decay_algorithm(self):
        user = User.objects.create_user(phone_number="+998901112202", okj_id="OKJ-90002")
        now = timezone.now()

        new_post = Post.objects.create(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Yangi post",
            slug="new-post-1",
        )
        old_post = Post.objects.create(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Eski post",
            slug="old-post-1",
        )
        Post.objects.filter(id=old_post.id).update(created_at=now - timedelta(hours=10))
        old_post.refresh_from_db()

        score_new = FeedRankingService.calculate_post_score(new_post, now=now)
        score_old = FeedRankingService.calculate_post_score(old_post, now=now)

        assert score_new > score_old

    def test_generate_user_feed_cache(self):
        user = User.objects.create_user(phone_number="+998901112203", okj_id="OKJ-90003")
        post1 = PostService.create_post(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Birinchi iqtibos",
            status=Post.Status.PUBLISHED,
        )
        Post.objects.filter(id=post1.id).update(moderation_status=Post.ModerationStatus.APPROVED)

        count = FeedRankingService.generate_user_feed_cache(user.id)
        assert count >= 1

        cached_ids = FeedCacheAdapter.zrevrange(f"user:feed:cache:{user.id}", 0, 10)
        assert str(post1.id) in cached_ids
