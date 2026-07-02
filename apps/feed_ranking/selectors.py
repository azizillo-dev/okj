"""
OKJ PLATFORM - FEED RANKING SELECTORS (apps/feed_ranking/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha bazadan yoki keshdan
o'qish (read-only) amallari faqat selektorlar orqali amalga oshiriladi.

FAIL-SAFE FALLBACK STRATEGIYASI:
1. Dastlab Redis ZSET'dan ZREVRANGE bilan O(log N) tezlikda o'qiladi.
2. Cache Miss bo'lsa — Celery task orqali fon rejimida kesh yangilanadi.
3. Redis bilan muammo bo'lsa (ConnectionError) — PostgreSQL'dan to'g'ridan-to'g'ri
   SQL darajasida o'qib qaytariladi (tizim hech qachon yiqilmaydi).
"""

import logging
from typing import List
from datetime import timedelta
from django.utils import timezone
from posts.models import Post
from follows.models import Follow
from feed_ranking.services import FeedCacheAdapter, FeedRankingService

logger = logging.getLogger(__name__)


class FeedRankingSelector:
    """Algoritmik saralangan ijtimoiy lenta uchun selektorlar."""

    @classmethod
    def _get_sql_fallback_posts(cls, user, page: int, page_size: int) -> List[Post]:
        """
        Redis mavjud bo'lmagan hollarda PostgreSQL'dan to'g'ridan-to'g'ri yuklash.
        Foydalanuvchi ergashgan odamlarning postlari vaqt bo'yicha (so'nggi birinchi) qaytariladi.
        N+1 muammosiz: select_related + prefetch_related.
        """
        following_ids = list(
            Follow.objects.filter(
                follower_id=user.id,
                is_deleted=False
            ).values_list("following_id", flat=True)
        )
        author_ids = following_ids + [user.id]

        thirty_days_ago = timezone.now() - timedelta(days=30)
        offset = (page - 1) * page_size

        return list(
            Post.published_objects.filter(
                user_id__in=author_ids,
                created_at__gte=thirty_days_ago,
                status=Post.Status.PUBLISHED,
                moderation_status=Post.ModerationStatus.APPROVED,
            )
            .select_related("user", "book", "district")
            .prefetch_related("media")
            .order_by("-created_at")[offset : offset + page_size]
        )

    @classmethod
    def get_ranked_feed_for_user(cls, user, page: int = 1, page_size: int = 20) -> List[Post]:
        """
        Kitobxonning shaxsiy algoritmik lentasini yuklash.

        Kesh mavjud (Cache Hit):
          Redis ZSET → ZREVRANGE (O(log N + M)) → Post IDs →
          PostgreSQL batch query (select_related + prefetch_related) →
          Redis tartibi qayta tiklanadi → Qaytariladi

        Cache Miss:
          Celery task fon rejimida keshni yangilaydi →
          SQL Fallback'dan darhol natija qaytariladi (foydalanuvchi kutmaydi)

        Fail-Safe (Redis xatosi):
          SQL Fallback'dan darhol qaytariladi, xato log ga tushadi
        """
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        start = (page - 1) * page_size
        end = start + page_size - 1

        cache_key = f"user:feed:cache:{user.id}"

        try:
            post_ids = FeedCacheAdapter.zrevrange(cache_key, start, end)
        except Exception as e:
            logger.warning(f"Redis o'qish xatosi, SQL fallback'ga o'tildi: {e}")
            return cls._get_sql_fallback_posts(user, page, page_size)

        if not post_ids:
            # Cache Miss: Celery task orqali fon rejimida keshni qayta hisoblash
            try:
                from feed_ranking.tasks import rebuild_user_feed_cache_task
                rebuild_user_feed_cache_task.delay(str(user.id))
            except Exception:
                # Celery mavjud bo'lmasa sinxron bajarish
                FeedRankingService.generate_user_feed_cache(user.id)

            # SQL Fallback orqali darhol natija qaytarish
            return cls._get_sql_fallback_posts(user, page, page_size)

        # N+1 muammosiz ma'lumotlarni yuklash
        posts_db = (
            Post.published_objects.filter(id__in=post_ids)
            .select_related("user", "book", "district")
            .prefetch_related("media")
        )

        # Redis ZREVRANGE tartibini tiklash (DB order_by ishlamaydi)
        posts_map = {str(p.id): p for p in posts_db}
        ordered_posts = [posts_map[pid] for pid in post_ids if pid in posts_map]
        return ordered_posts

    @classmethod
    def get_total_feed_count(cls, user) -> int:
        """Lentadagi jami postlar sonini qaytaradi (Paginatsiya uchun)."""
        cache_key = f"user:feed:cache:{user.id}"
        try:
            count = FeedCacheAdapter.zcard(cache_key)
            if count == 0:
                count = FeedRankingService.generate_user_feed_cache(user.id)
                count = FeedCacheAdapter.zcard(cache_key)
            return count
        except Exception:
            # Fallback: DB'dan hisoblash
            from datetime import timedelta
            following_ids = list(
                Follow.objects.filter(
                    follower_id=user.id, is_deleted=False
                ).values_list("following_id", flat=True)
            )
            author_ids = following_ids + [user.id]
            return Post.published_objects.filter(
                user_id__in=author_ids,
                created_at__gte=timezone.now() - timedelta(days=30),
                status=Post.Status.PUBLISHED,
                moderation_status=Post.ModerationStatus.APPROVED,
            ).count()
