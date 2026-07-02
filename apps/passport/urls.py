from django.urls import path
from .apis import UserReadingPassportApi, GlobalLeaderboardApi

app_name = "passport"

urlpatterns = [
    path("", UserReadingPassportApi.as_view(), name="user-passport"),
    path("leaderboard/", GlobalLeaderboardApi.as_view(), name="leaderboard"),
]
