"""
OKJ PLATFORM - FOLLOWS URLS (apps/follows/urls.py)
Nega bu fayl kerak: /api/v1/users/{id}/follow/, unfollow/, followers/, following/ marshrutlari.
"""

from django.urls import path
from .apis import FollowUserApi, UnfollowUserApi, UserFollowersListApi, UserFollowingListApi

urlpatterns = [
    path("<str:user_id>/follow/", FollowUserApi.as_view(), name="user-follow"),
    path("<str:user_id>/unfollow/", UnfollowUserApi.as_view(), name="user-unfollow"),
    path("<str:user_id>/followers/", UserFollowersListApi.as_view(), name="user-followers"),
    path("<str:user_id>/following/", UserFollowingListApi.as_view(), name="user-following"),
]
