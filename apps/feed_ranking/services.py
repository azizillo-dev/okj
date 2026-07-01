"""
OKJ PLATFORM - FEED RANKING SERVICES (apps/feed_ranking/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA BIZNES MANTIQ
(Score hisoblash, Redis Sorted Set keshni yozish va yangilash) shu yerda joylashadi.
"""

import logging
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Q
from django.core.cache import cache
from posts.models import Post
from follows.models import Follow

logger = logging.getLogger(__name__)


class FeedCacheAdapter:
    """
    Redis Sorted Set (ZSET) uchun gibrid adabtor.
    Productionda Redis ZSET (zadd, zrevrange, zcard) dan foydalanadi.
    Agar test jarayonida yoki Redis uzilib qolgan holatlarda xotira (locmem) orqali ishlaydi.
    """
    _locmem_cache = {}
    _redis_available = True

    @classmethod
    def _get_raw_client(cls):
        if not cls._redis_available:
            return None
        try:
            if hasattr(cache, "client"):
                client = cache.client.get_client()
                # Test connection quickly
                client.ping()
                return client
        except Exception:
            cls._redis_available = False
        return None

    @classmethod
    def zadd(cls, key: str, scored_items: List[Tuple[str, float]], ttl: int = 3600) -> None:
        if not scored_items:
            return
        client = cls._get_raw_client()
        if client:
            try:
                mapping = {post_id: score for post_id, score in scored_items}
                client.zadd(key, mapping)
                client.expire(key, ttl)
                return
            except Exception:
                cls._redis_available = False

        sorted_ids = [item[0] for item in scored_items]
        cls._locmem_cache[key] = sorted_ids

    @classmethod
    def zrevrange(cls, key: str, start: int, end: int) -> List[str]:
        client = cls._get_raw_client()
        if client:
            try:
                results = client.zrevrange(key, start, end)
                return [r.decode("utf-8") if isinstance(r, bytes) else str(r) for r in results]
            except Exception:
                cls._redis_available = False

        data = cls._locmem_cache.get(key, [])
        return data[start : end + 1]

    @classmethod
    def zcard(cls, key: str) -> int:
        client = cls._get_raw_client()
        if client:
            try:
                return client.zcard(key)
            except Exception:
                cls._redis_available = False

        data = cls._locmem_cache.get(key, [])
        return len(data)

    @classmethod
    def delete(cls, key: str) -> None:
        client = cls._get_raw_client()
        if client:
            try:
                client.delete(key)
            except Exception:
                cls._redis_available = False
        cls._locmem_cache.pop(key, None)


class FeedRankingService:
    """Ijtimoiy lentani algoritmik saralash va keshlar bilan ishlovchi servis."""

    @staticmethod
    def calculate_post_score(post: Post, now: Optional[datetime] = None) -> float:
        """
        Har bir postning algoritmik reyting score'ini hisoblovchi funksiya.
        Formula: Score = (Base_Weight + (Likes * 10) + (Comments * 20)) / (Age_In_Hours + 2)^1.5

        Base_Weight qoidalari:
        - REVIEW va EXCHANGE postlari uchun = 50
        - QUOTE va SHOWCASE (yoki boshqalar) uchun = 20
        """
        if now is None:
            now = timezone.now()

        post_type = getattr(post, "post_type", "")
        if post_type in [Post.PostType.REVIEW, Post.PostType.EXCHANGE, Post.PostType.SELL, Post.PostType.GIFT]:
            base_weight = 50.0
        else:
            base_weight = 20.0

        likes_count = getattr(post, "likes_cnt", None)
        if likes_count is None:
            likes_count = post.likes.filter(is_deleted=False).count()

        comments_count = getattr(post, "comments_cnt", None)
        if comments_count is None:
            comments_count = post.comments.filter(is_deleted=False).count()

        created_at = getattr(post, "created_at", now)
        age_seconds = max(0.0, (now - created_at).total_seconds())
        age_in_hours = age_seconds / 3600.0

        numerator = base_weight + (likes_count * 10.0) + (comments_count * 20.0)
        denominator = (age_in_hours + 2.0) ** 1.5
        return round(numerator / denominator, 4)

    @classmethod
    def generate_user_feed_cache(cls, user_id: int) -> int:
        """
        Foydalanuvchi ergashgan (Following) barcha faol foydalanuvchilarning oxirgi 30 kundagi
        postlarini yig'ib, Time-Decay formula bilan Score hisoblab, eng yuqori reytingli 500 ta
        post ID-sini va Score-ni Redis Sorted Set (ZSET) ichiga joylashtiradi.
        Key: "user:feed:cache:<user_id>"
        """
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        following_ids = list(
            Follow.objects.filter(
                follower_id=user_id,
                is_deleted=False
            ).values_list("following_id", flat=True)
        )

        author_ids = following_ids + [user_id]

        qs = (
            Post.published_objects.filter(
                user_id__in=author_ids,
                created_at__gte=thirty_days_ago,
                status=Post.Status.PUBLISHED,
                moderation_status=Post.ModerationStatus.APPROVED,
            )
            .annotate(
                likes_cnt=Count("likes", filter=Q(likes__is_deleted=False), distinct=True),
                comments_cnt=Count("comments", filter=Q(comments__is_deleted=False), distinct=True),
            )
        )

        if qs.count() < 50:
            qs = (
                Post.published_objects.filter(
                    created_at__gte=thirty_days_ago,
                    status=Post.Status.PUBLISHED,
                    moderation_status=Post.ModerationStatus.APPROVED,
                    visibility=Post.Visibility.PUBLIC,
                )
                .annotate(
                    likes_cnt=Count("likes", filter=Q(likes__is_deleted=False), distinct=True),
                    comments_cnt=Count("comments", filter=Q(comments__is_deleted=False), distinct=True),
                )
            )

        scored_posts = []
        for post in qs:
            score = cls.calculate_post_score(post, now=now)
            scored_posts.append((str(post.id), score))

        scored_posts.sort(key=lambda x: x[1], reverse=True)
        top_500 = scored_posts[:500]

        cache_key = f"user:feed:cache:{user_id}"
        FeedCacheAdapter.zadd(cache_key, top_500, ttl=3600)
        return len(top_500)
