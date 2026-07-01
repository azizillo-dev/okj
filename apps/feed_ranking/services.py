"""
OKJ PLATFORM - FEED RANKING SERVICES (apps/feed_ranking/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA BIZNES MANTIQ
(Score hisoblash, Redis Sorted Set keshni yozish, Fan-out on Write) shu yerda joylashadi.

ARXITEKTURA:
- FeedCacheAdapter: Redis ZSET ↔ LocMem gibrid. Redis yo'q bo'lsa ham ishlaydi.
- FeedRankingService.calculate_post_score(): Time-Decay algoritm.
- FeedRankingService.generate_user_feed_cache(): Bir foydalanuvchi lentasini qayta hisoblaydi.
- FeedRankingService.fan_out_new_post(): Yangi post barcha obunachilarga ZADD orqali push.
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
    Productionda Redis ZSET (zadd, zrevrange, zcard, zadd) dan foydalanadi.
    Agar test jarayonida yoki Redis uzilib qolgan holatlarda xotira (locmem) orqali ishlaydi.
    Circuit Breaker: Bir marta xato bo'lsa Redis'ni tekshirishni to'xtatadi (ping bilan qayta tekshiradi).
    """
    _locmem_cache: dict = {}
    _redis_available: bool = True

    @classmethod
    def _get_raw_client(cls):
        if not cls._redis_available:
            return None
        try:
            if hasattr(cache, "client"):
                client = cache.client.get_client()
                client.ping()
                return client
        except Exception:
            cls._redis_available = False
        return None

    @classmethod
    def zadd(cls, key: str, scored_items: List[Tuple[str, float]], ttl: int = 3600) -> None:
        """ZADD — Post ID va Score larni Sorted Set'ga yozish."""
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

        # LocMem fallback — (post_id, score) jufti sifatida saqlash
        existing = cls._locmem_cache.get(key, [])
        existing_dict = {pid: sc for pid, sc in existing}
        for pid, sc in scored_items:
            existing_dict[pid] = sc
        # Score bo'yicha teskari tartibda saqlash
        sorted_items = sorted(existing_dict.items(), key=lambda x: x[1], reverse=True)
        cls._locmem_cache[key] = sorted_items

    @classmethod
    def zrevrange(cls, key: str, start: int, end: int) -> List[str]:
        """ZREVRANGE — Yuqori scoreli post ID larni sahifalab o'qish."""
        client = cls._get_raw_client()
        if client:
            try:
                results = client.zrevrange(key, start, end)
                return [r.decode("utf-8") if isinstance(r, bytes) else str(r) for r in results]
            except Exception:
                cls._redis_available = False

        data = cls._locmem_cache.get(key, [])
        sliced = data[start : end + 1]
        return [item[0] if isinstance(item, tuple) else item for item in sliced]

    @classmethod
    def zcard(cls, key: str) -> int:
        """ZCARD — Sorted Set'dagi elementlar sonini olish."""
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
        """Keshdan key'ni o'chirish."""
        client = cls._get_raw_client()
        if client:
            try:
                client.delete(key)
            except Exception:
                cls._redis_available = False
        cls._locmem_cache.pop(key, None)


class FeedRankingService:
    """
    Ijtimoiy lentani algoritmik saralash va keshlar bilan ishlovchi servis.

    Asosiy algoritmlar:
    1. Time-Decay Score: Yangi va mashxur postlar yuqorida.
    2. Fan-out on Write: Yangi post barcha obunachilarga push.
    3. Fallback: Redis yo'q bo'lganda PostgreSQL dan to'g'ridan-to'g'ri yuklash.
    """

    # Base weight konstantalari (post turiga qarab)
    BASE_WEIGHT_HIGH = 50.0    # REVIEW, EXCHANGE, SELL, GIFT — platformaning asosiy qadriyatlari
    BASE_WEIGHT_MID = 20.0     # QUOTE, SHOWCASE
    BASE_WEIGHT_LOW = 10.0     # Boshqa turdagi postlar

    @classmethod
    def calculate_post_score(cls, post: Post, now: Optional[datetime] = None) -> float:
        """
        Har bir postning algoritmik reyting score'ini hisoblovchi funksiya.

        Formula:
            Score = (Base_Weight + (Likes * 10) + (Comments * 20)) / (Age_In_Hours + 2)^1.5

        Base_Weight qoidalari:
        - REVIEW va EXCHANGE/SELL/GIFT uchun = 50 (platformaning asosiy qadriyati)
        - QUOTE va SHOWCASE uchun = 20
        - Boshqa turdagi postlar uchun = 10

        Denominator (+2) sababi:
        - Yangi post (0 soatlik) cheksizlikka bo'linib ketmasligi uchun.
        - Birinchi 2 soat ichida post munosib ko'rinishni saqlaydi.

        Exponent (1.5) sababi:
        - Vaqt bilan score eksponentsial pasayadi (Hacker News gravity algoritmi).
        """
        if now is None:
            now = timezone.now()

        post_type = getattr(post, "post_type", "")
        if post_type in [Post.PostType.REVIEW, Post.PostType.EXCHANGE, Post.PostType.SELL, Post.PostType.GIFT]:
            base_weight = cls.BASE_WEIGHT_HIGH
        elif post_type in [Post.PostType.QUOTE, Post.PostType.SHOWCASE]:
            base_weight = cls.BASE_WEIGHT_MID
        else:
            base_weight = cls.BASE_WEIGHT_LOW

        likes_count = getattr(post, "likes_cnt", None)
        if likes_count is None:
            likes_count = post.likes.filter(is_deleted=False).count()

        comments_count = getattr(post, "comments_cnt", None)
        if comments_count is None:
            comments_count = post.comments.filter(is_deleted=False).count()

        created_at = getattr(post, "created_at", now)
        if created_at.tzinfo is None:
            created_at = timezone.make_aware(created_at)
        age_seconds = max(0.0, (now - created_at).total_seconds())
        age_in_hours = age_seconds / 3600.0

        numerator = base_weight + (likes_count * 10.0) + (comments_count * 20.0)
        denominator = (age_in_hours + 2.0) ** 1.5
        return round(numerator / denominator, 4)

    @classmethod
    def _build_feed_queryset(cls, author_ids: list, thirty_days_ago):
        """N+1 muammosiz post queryset yasash."""
        return (
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

    @classmethod
    def generate_user_feed_cache(cls, user_id) -> int:
        """
        Foydalanuvchi ergashgan (Following) barcha faol foydalanuvchilarning oxirgi 30 kundagi
        postlarini yig'ib, Time-Decay formula bilan Score hisoblab, eng yuqori reytingli 500 ta
        post ID-sini va Score-ni Redis Sorted Set (ZSET) ichiga joylashtiradi.

        Fan-in (Pull) strategiyasi:
        - Kesh muddati tugaganda yoki yangi kitobxon kelganda chaqiriladi.
        - 50 dan kam post bo'lsa platformaning umum postlaridan ham to'ldiradi.

        Redis Key: "user:feed:cache:<user_id>"
        TTL: 3600 soniya (1 soat)
        Limit: Eng yuqori 500 ta post
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
        qs = cls._build_feed_queryset(author_ids, thirty_days_ago)

        # Agar following lentasida kamroq post bo'lsa, umum postlar bilan to'ldirish
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

    @classmethod
    def fan_out_new_post(cls, post_id: str, author_id) -> int:
        """
        Fan-out on Write: Yangi post yaratilganda uni barcha obunachilarga (Followers) keshiga
        asinxron ZADD orqali push qilish.

        Bu nima uchun kerak:
        - Pull strategiyasi (generate_user_feed_cache) har bir so'rovda qimmat.
        - Fan-out: Yangi post yaratilganda uni darhol barcha obunachilarning Sorted Set'iga
          qo'shish — keyingi so'rov ZREVRANGE O(log N) bilan tez ishlaydi.

        Cheklov (Celebrity problem):
        - Millionlab obunachisi bo'lgan mashhur foydalanuvchilar uchun bu sinxron bajarilmaydi.
        - Celery asinxron task orqali bajarilishi kerak (tasks.py da).

        Returns: Fan-out qilingan obunachilar soni.
        """
        try:
            post = (
                Post.published_objects
                .filter(id=post_id, status=Post.Status.PUBLISHED)
                .annotate(
                    likes_cnt=Count("likes", filter=Q(likes__is_deleted=False), distinct=True),
                    comments_cnt=Count("comments", filter=Q(comments__is_deleted=False), distinct=True),
                )
                .first()
            )
            if not post:
                return 0

            score = cls.calculate_post_score(post, now=timezone.now())
            post_id_str = str(post_id)
            scored_item = [(post_id_str, score)]

            # Barcha obunachilarni olish
            follower_ids = list(
                Follow.objects.filter(
                    following_id=author_id,
                    is_deleted=False
                ).values_list("follower_id", flat=True)
            )

            count = 0
            for follower_id in follower_ids:
                cache_key = f"user:feed:cache:{follower_id}"
                # Faqat kesh mavjud bo'lgan holatlarda push qilamiz (yo'q bo'lsa isrof)
                if FeedCacheAdapter.zcard(cache_key) > 0:
                    FeedCacheAdapter.zadd(cache_key, scored_item, ttl=3600)
                    count += 1

            # Muallif o'z lentasiga ham qo'shadi
            author_cache_key = f"user:feed:cache:{author_id}"
            if FeedCacheAdapter.zcard(author_cache_key) > 0:
                FeedCacheAdapter.zadd(author_cache_key, scored_item, ttl=3600)

            return count

        except Exception as e:
            logger.error(f"Fan-out xatosi (post_id={post_id}): {e}")
            return 0
