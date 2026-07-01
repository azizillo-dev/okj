"""
OKJ PLATFORM - FEED RANKING URLS (apps/feed_ranking/urls.py)
Nega bu fayl kerak: /api/v1/posts/feed/ marshrutini aniqlash.
"""

from django.urls import path
from .apis import UserRankedFeedApi

urlpatterns = [
    path("", UserRankedFeedApi.as_view(), name="user-ranked-feed"),
]
