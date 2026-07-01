"""
OKJ PLATFORM - INTERACTIONS URLS (apps/interactions/urls.py)
Nega bu fayl kerak: /api/v1/posts/{id}/like/ va /bookmark/ marshrutlarini ulab berish.
"""

from django.urls import path
from .apis import PostLikeToggleApi, PostBookmarkToggleApi

urlpatterns = [
    path("<str:post_id>/like/", PostLikeToggleApi.as_view(), name="post-like-toggle"),
    path("<str:post_id>/bookmark/", PostBookmarkToggleApi.as_view(), name="post-bookmark-toggle"),
]
