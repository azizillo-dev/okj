"""
OKJ PLATFORM - LIBRARY URLS (apps/library/urls.py)
Nega bu fayl kerak: /api/v1/library/ ostidagi marshrutlarni aniqlash.
"""

from django.urls import path
from .apis import (
    UserShelfListCreateApi,
    ShelfItemDetailApi,
    CurrentReadingApi,
    LogProgressApi,
    ReadingStatisticsApi,
    HeatmapApi,
    GoalsListCreateApi,
)

urlpatterns = [
    path("shelf/", UserShelfListCreateApi.as_view(), name="library-shelf-list"),
    path("shelf/current/", CurrentReadingApi.as_view(), name="library-current-reading"),
    path("shelf/<str:book_id>/", ShelfItemDetailApi.as_view(), name="library-shelf-detail"),
    path("logs/progress/", LogProgressApi.as_view(), name="library-log-progress"),
    path("statistics/", ReadingStatisticsApi.as_view(), name="library-statistics"),
    path("heatmap/", HeatmapApi.as_view(), name="library-heatmap"),
    path("goals/", GoalsListCreateApi.as_view(), name="library-goals"),
]
