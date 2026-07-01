"""
OKJ PLATFORM - POSTS URLS (apps/posts/urls.py)
Nega bu fayl kerak: /api/v1/posts/ ostidagi marshrutlarni aniqlash.
"""

from django.urls import path
from .apis import (
    PostFeedApi,
    PostDetailApi,
    PublishPostApi,
    ArchivePostApi,
    ReportPostApi,
)

urlpatterns = [
    path("", PostFeedApi.as_view(), name="posts-feed"),
    path("<str:slug>/", PostDetailApi.as_view(), name="posts-detail"),
    path("<str:slug>/publish/", PublishPostApi.as_view(), name="posts-publish"),
    path("<str:slug>/archive/", ArchivePostApi.as_view(), name="posts-archive"),
    path("<str:slug>/report/", ReportPostApi.as_view(), name="posts-report"),
]
