"""
OKJ PLATFORM - ACCOUNTS URLS (apps/accounts/urls.py)
Nega bu fayl kerak: /api/v1/accounts/ ostidagi marshrutlarni aniqlash.
"""

from django.urls import path
from .apis import (
    DistrictListApi,
    ReaderRegisterApi,
    ReaderProfileApi,
    DistrictLeaderboardApi,
)

urlpatterns = [
    path("districts/", DistrictListApi.as_view(), name="district-list"),
    path("districts", DistrictListApi.as_view()),
    path("register/", ReaderRegisterApi.as_view(), name="reader-register"),
    path("register", ReaderRegisterApi.as_view()),
    path("me/", ReaderProfileApi.as_view(), name="reader-profile"),
    path("me", ReaderProfileApi.as_view()),
    path("leaderboard/district/<int:district_id>/", DistrictLeaderboardApi.as_view(), name="district-leaderboard"),
]
