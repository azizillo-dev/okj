"""
OKJ PLATFORM - POSTS FILTERS (apps/posts/filters.py)
Nega bu fayl kerak: Lenta va qidiruv so'rovlarida parametrlar orqali
toza filtrlash mantiqi.
"""

from typing import Dict, Any
from .selectors import PostSelector


def filter_posts_feed(query_params: Dict[str, Any]):
    """So'rov parametrlaridan lenta filtrlarini ajratib olish."""
    return PostSelector.get_feed_posts(
        post_type=query_params.get("post_type"),
        district_id=query_params.get("district_id"),
        book_id=query_params.get("book_id"),
        hashtag=query_params.get("hashtag"),
    )
