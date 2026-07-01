"""
OKJ PLATFORM - FEED RANKING SELECTORS (apps/feed_ranking/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha bazadan yoki keshtan
o'qish (read-only) amallari faqat selektorlar orqali amalga oshiriladi.
"""

from typing import List
from posts.models import Post
from feed_ranking.services import FeedCacheAdapter, FeedRankingService


class FeedRankingSelector:
    """Algoritmik saralangan ijtimoiy lenta uchun selektorlar."""

    @classmethod
    def get_ranked_feed_for_user(cls, user, page: int = 1, page_size: int = 20) -> List[Post]:
        """
        Kitobxonning shaxsiy lentasini yuklash.
        Mantiq: Dastlab Redis'dagi Sorted Set'dan tegishli sahifa (page) uchun post ID-larini o'qiydi (ZREVRANGE).
        Agar kesh bo'sh bo'lsa (Cache Miss), zaxira reja (Fallback) sifatida PostgreSQL bazasining o'zidan
        hisoblab, select_related va prefetch_related bilan N+1 muammosiz yuklab beradi va keshni yangilaydi.
        """
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20

        start = (page - 1) * page_size
        end = start + page_size - 1

        cache_key = f"user:feed:cache:{user.id}"
        post_ids = FeedCacheAdapter.zrevrange(cache_key, start, end)

        if not post_ids:
            # Cache Miss: servis orqali keshni qayta hisoblab yozamiz
            FeedRankingService.generate_user_feed_cache(user.id)
            post_ids = FeedCacheAdapter.zrevrange(cache_key, start, end)

        if not post_ids:
            return []

        # N+1 muammosiz ma'lumotlarni yuklash
        posts_db = (
            Post.published_objects.filter(id__in=post_ids)
            .select_related("user", "book")
            .prefetch_related("media")
        )

        # Redis zrevrange tartibini bazadan keluvchi obyektlarga to'liq saqlab qolamiz
        posts_map = {str(p.id): p for p in posts_db}
        ordered_posts = [posts_map[pid] for pid in post_ids if pid in posts_map]
        return ordered_posts

    @classmethod
    def get_total_feed_count(cls, user) -> int:
        """Lentadagi jami postlar sonini qaytaradi (Paginatsiya uchun)."""
        cache_key = f"user:feed:cache:{user.id}"
        count = FeedCacheAdapter.zcard(cache_key)
        if count == 0:
            count = FeedRankingService.generate_user_feed_cache(user.id)
            count = FeedCacheAdapter.zcard(cache_key)
        return count
