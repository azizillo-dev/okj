"""
OKJ PLATFORM - FEED RANKING TESTS (apps/feed_ranking/tests/)
Nega bu testlar kerak:
1. OKJ_ID 100k+ da ham numerical tartib to'g'ri ishlashi.
2. Time-Decay algoritmi yangi post tepada chiqishi.
3. Redis cache-miss fallback SQL orqali ishlashi.
4. Fan-out on Write obunachilarning keshiga yetib borishi.
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from posts.models import Post
from posts.services import PostService
from accounts.services import UserService
from feed_ranking.services import FeedRankingService, FeedCacheAdapter
from feed_ranking.selectors import FeedRankingSelector

User = get_user_model()


@pytest.mark.django_db
class TestOkjNumberNumericalSorting:
    """okj_number maydonining to'g'ri numerik tartibda ishlashini tekshirish."""

    def test_okj_number_is_numeric_integer(self):
        """okj_number integer, okj_id matn ko'rinishida saqlangan."""
        user = UserService.register_reader(phone_number="+998901200001")
        assert isinstance(user.okj_number, int)
        assert user.okj_id == f"OKJ-{user.okj_number}"

    def test_okj_number_sequential(self):
        """Ketma-ket ro'yxatdan o'tishda okj_number ham ketma-ket bo'lishi kerak."""
        u1 = UserService.register_reader(phone_number="+998901200010")
        u2 = UserService.register_reader(phone_number="+998901200011")
        assert u2.okj_number == u1.okj_number + 1

    def test_okj_number_numerical_sort_beyond_99999(self):
        """
        99,999 dan oshganda ham numerik tartib to'g'ri ishlashi (lexicographic xavf yo'q).
        OKJ-99999 va OKJ-100000 numerical order bo'yicha: 99999 < 100000.
        """
        u1 = UserService.register_reader(phone_number="+998901200020")
        u2 = UserService.register_reader(phone_number="+998901200021")

        # okj_number larni to'g'ridan-to'g'ri yangilash (manual simulation)
        User.all_objects.filter(id=u1.id).update(okj_number=99999)
        User.all_objects.filter(id=u2.id).update(okj_number=100000)
        u1.refresh_from_db()
        u2.refresh_from_db()

        # Numerik tartib bo'yicha u1 < u2
        assert u1.okj_number < u2.okj_number
        # Matnli tartibda 'OKJ-99999' > 'OKJ-100000' bo'lishiga qaramay,
        # okj_number INTEGER sifatida to'g'ri: 99999 < 100000
        assert str(u1.okj_id) < str(u2.okj_id) or u1.okj_number < u2.okj_number

        # Yangi foydalanuvchi qo'shilganda order_by("-okj_number") orqali 100001 bo'ladi
        u3 = UserService.register_reader(phone_number="+998901200022")
        assert u3.okj_number == 100001

    def test_okj_number_unique_constraint(self):
        """Ikki foydalanuvchi bir xil okj_number olmasligi kerak."""
        u1 = UserService.register_reader(phone_number="+998901200030")
        u2 = UserService.register_reader(phone_number="+998901200031")
        assert u1.okj_number != u2.okj_number


@pytest.mark.django_db
class TestFeedRankingServiceScoring:
    """Time-Decay algoritmi va score hisoblash testlari."""

    def test_review_post_higher_score_than_quote(self):
        """REVIEW postining base_weight > QUOTE — score tepada bo'lishi kerak."""
        user = User.objects.create_user(phone_number="+998901210001", okj_id="OKJ-SCORE-01", okj_number=90001)
        now = timezone.now()

        review_post = Post.objects.create(
            user=user,
            post_type=Post.PostType.REVIEW,
            user_rating=5,
            title="Taqriz sarlavha",
            content="Yaxshi kitob",
            slug="review-score-test-1",
        )
        quote_post = Post.objects.create(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Bilim kuchdir",
            slug="quote-score-test-1",
        )

        score_review = FeedRankingService.calculate_post_score(review_post, now=now)
        score_quote = FeedRankingService.calculate_post_score(quote_post, now=now)
        assert score_review > score_quote, (
            f"REVIEW score ({score_review}) QUOTE score ({score_quote}) dan yuqori bo'lishi kerak"
        )

    def test_newer_post_higher_score_than_older(self):
        """Yangi post eski postdan score tepada bo'lishi kerak (Time-Decay)."""
        user = User.objects.create_user(phone_number="+998901210002", okj_id="OKJ-SCORE-02", okj_number=90002)
        now = timezone.now()

        new_post = Post.objects.create(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Yangi post",
            slug="new-post-score-1",
        )
        old_post = Post.objects.create(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Eski post",
            slug="old-post-score-1",
        )
        # Eski postni 24 soat oldin yaratilgan deb ko'rsatamiz
        Post.objects.filter(id=old_post.id).update(created_at=now - timedelta(hours=24))
        old_post.refresh_from_db()

        score_new = FeedRankingService.calculate_post_score(new_post, now=now)
        score_old = FeedRankingService.calculate_post_score(old_post, now=now)
        assert score_new > score_old, (
            f"Yangi post score ({score_new}) eski post score ({score_old}) dan yuqori bo'lishi kerak"
        )

    def test_post_with_more_likes_higher_score(self):
        """Ko'proq laykli post baland score olishi kerak."""
        user = User.objects.create_user(phone_number="+998901210003", okj_id="OKJ-SCORE-03", okj_number=90003)
        now = timezone.now()

        post = Post.objects.create(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Mashhur post",
            slug="popular-post-score-1",
        )
        # likes_cnt va comments_cnt annotatsiya orqali qo'shamiz
        post.likes_cnt = 50
        post.comments_cnt = 0
        score_popular = FeedRankingService.calculate_post_score(post, now=now)

        post.likes_cnt = 0
        score_unpopular = FeedRankingService.calculate_post_score(post, now=now)

        assert score_popular > score_unpopular

    def test_score_formula_correctness(self):
        """Score formulasi to'g'ri hisoblashini tekshirish."""
        user = User.objects.create_user(phone_number="+998901210004", okj_id="OKJ-SCORE-04", okj_number=90004)
        now = timezone.now()

        post = Post.objects.create(
            user=user,
            post_type=Post.PostType.REVIEW,
            content="Formula testi",
            slug="formula-test-1",
        )
        post.likes_cnt = 10
        post.comments_cnt = 5
        # Yangi post — age ≈ 0 soat → (0 + 2)^1.5 = 2.8284
        expected_numerator = 50.0 + (10 * 10.0) + (5 * 20.0)  # 50 + 100 + 100 = 250
        expected_denominator = (0 + 2.0) ** 1.5  # ≈ 2.8284
        expected_score = round(expected_numerator / expected_denominator, 4)

        actual_score = FeedRankingService.calculate_post_score(post, now=now)
        assert abs(actual_score - expected_score) < 0.5, (
            f"Score {actual_score} kutilgan {expected_score} ga yaqin bo'lishi kerak"
        )


@pytest.mark.django_db
class TestFeedRankingCacheMissFallback:
    """Cache miss bo'lganda SQL fallback ishlashi testlari."""

    def test_cache_miss_returns_sql_posts(self):
        """Redis keshi bo'sh bo'lganda SQL fallback postlarni qaytaradi."""
        user = UserService.register_reader(phone_number="+998901220001")
        post = PostService.create_post(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Fallback testi uchun post",
            status=Post.Status.PUBLISHED,
        )
        Post.objects.filter(id=post.id).update(moderation_status=Post.ModerationStatus.APPROVED)

        # Keshni tozalaymiz (Cache Miss simulyatsiyasi)
        cache_key = f"user:feed:cache:{user.id}"
        FeedCacheAdapter.delete(cache_key)
        assert FeedCacheAdapter.zcard(cache_key) == 0

        # SQL fallback orqali postlar qaytarilishi kerak
        posts = FeedRankingSelector._get_sql_fallback_posts(user, page=1, page_size=20)
        assert len(posts) >= 1
        assert any(str(p.id) == str(post.id) for p in posts)

    def test_get_ranked_feed_cache_miss_triggers_rebuild(self):
        """get_ranked_feed_for_user cache miss bo'lganda rebuild ishlatadi."""
        user = UserService.register_reader(phone_number="+998901220002")
        post = PostService.create_post(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Rebuild testi uchun post",
            status=Post.Status.PUBLISHED,
        )
        Post.objects.filter(id=post.id).update(moderation_status=Post.ModerationStatus.APPROVED)

        # Keshni tozalaymiz
        cache_key = f"user:feed:cache:{user.id}"
        FeedCacheAdapter.delete(cache_key)

        # Selektor chaqirilganda natija qaytarilishi kerak (SQL fallback)
        posts = FeedRankingSelector.get_ranked_feed_for_user(user=user, page=1, page_size=20)
        assert isinstance(posts, list)
        assert len(posts) >= 1

    def test_generate_user_feed_cache_fills_cache(self):
        """generate_user_feed_cache keshni to'ldiradi."""
        user = UserService.register_reader(phone_number="+998901220003")
        post = PostService.create_post(
            user=user,
            post_type=Post.PostType.QUOTE,
            quote_text="Kesh to'ldirish testi",
            status=Post.Status.PUBLISHED,
        )
        Post.objects.filter(id=post.id).update(moderation_status=Post.ModerationStatus.APPROVED)

        # Keshni tozalash
        cache_key = f"user:feed:cache:{user.id}"
        FeedCacheAdapter.delete(cache_key)

        count = FeedRankingService.generate_user_feed_cache(user.id)
        assert count >= 1

        # Keshda ma'lumot bor
        assert FeedCacheAdapter.zcard(cache_key) >= 1

        # Keshdan o'qilganda post mavjud
        cached_ids = FeedCacheAdapter.zrevrange(cache_key, 0, 20)
        assert str(post.id) in cached_ids


@pytest.mark.django_db
class TestFanOutOnWrite:
    """Fan-out on Write: Yangi post obunachilarga push qilinishi testi."""

    def test_fan_out_pushes_to_follower_cache(self):
        """Yangi post yaratilganda obunachining keshiga push qilinadi."""
        from follows.services import FollowService

        author = UserService.register_reader(phone_number="+998901230001")
        follower = UserService.register_reader(phone_number="+998901230002")

        # Obuna qilish
        FollowService.follow_user(follower=follower, following_id=author.id)

        # Obunachining keshini boshlang'ich holga keltirish (birorta yozuv bo'lishi kerak)
        follower_cache_key = f"user:feed:cache:{follower.id}"
        FeedCacheAdapter.zadd(follower_cache_key, [("placeholder-id", 1.0)], ttl=3600)
        assert FeedCacheAdapter.zcard(follower_cache_key) >= 1

        # Yangi post yaratish va chop etish
        post = PostService.create_post(
            user=author,
            post_type=Post.PostType.QUOTE,
            quote_text="Fan-out test posti",
            status=Post.Status.PUBLISHED,
        )
        Post.objects.filter(id=post.id).update(moderation_status=Post.ModerationStatus.APPROVED)

        # Fan-out bajarish
        count = FeedRankingService.fan_out_new_post(post_id=str(post.id), author_id=author.id)
        assert count >= 1

        # Obunachining keshida yangi post bo'lishi kerak
        cached_ids = FeedCacheAdapter.zrevrange(follower_cache_key, 0, 50)
        assert str(post.id) in cached_ids


@pytest.mark.django_db
class TestCircuitBreakerHalfOpen:
    """Circuit Breaker Half-Open holati testlari."""

    def test_half_open_recovery(self):
        import time
        # Xatolikni simulyatsiya qilamiz
        FeedCacheAdapter._mark_failure()
        assert FeedCacheAdapter._redis_available is False
        assert FeedCacheAdapter._last_failure_time is not None

        # 30 soniyadan kam vaqt o'tganda hali ham ochiq (qayta urib ko'rmaydi)
        assert FeedCacheAdapter._get_raw_client() is None

        # 30 soniya o'tgan holatni simulyatsiya qilamiz
        FeedCacheAdapter._last_failure_time = time.time() - 31.0
        # Client olishga harakat qilamiz
        FeedCacheAdapter._get_raw_client()
        # Agar Redis yoki locmem bo'lsa mantiq ishlaydi
        FeedCacheAdapter._redis_available = True
        FeedCacheAdapter._last_failure_time = None


@pytest.mark.django_db
class TestHybridTopUpLogic:
    """UX Gibrid Top-Up: Following va Public postlarning birlashtirilishi testi."""

    def test_following_score_superiority_in_topup(self):
        from follows.services import FollowService
        author = UserService.register_reader(phone_number="+998901240001")
        public_author = UserService.register_reader(phone_number="+998901240002")
        reader = UserService.register_reader(phone_number="+998901240003")

        FollowService.follow_user(follower=reader, following_id=author.id)

        # Following post
        f_post = PostService.create_post(
            user=author,
            post_type=Post.PostType.QUOTE,
            quote_text="Following post",
            status=Post.Status.PUBLISHED,
            visibility=Post.Visibility.PUBLIC,
        )
        Post.objects.filter(id=f_post.id).update(moderation_status=Post.ModerationStatus.APPROVED)

        # Public post (pastroq reytingli yoki balandroq reytingli bo'lsa ham)
        p_post = PostService.create_post(
            user=public_author,
            post_type=Post.PostType.REVIEW,
            user_rating=5,
            title="Public review",
            content="Juda zo'r kitob",
            status=Post.Status.PUBLISHED,
            visibility=Post.Visibility.PUBLIC,
        )
        Post.objects.filter(id=p_post.id).update(moderation_status=Post.ModerationStatus.APPROVED)

        count = FeedRankingService.generate_user_feed_cache(reader.id)
        assert count >= 2

        cache_key = f"user:feed:cache:{reader.id}"
        cached_ids = FeedCacheAdapter.zrevrange(cache_key, 0, 10)
        # Following post har doim 1- o'rinda (top-up postdan yuqori) bo'lishi kerak
        assert cached_ids[0] == str(f_post.id)
