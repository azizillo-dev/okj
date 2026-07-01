"""
OKJ PLATFORM - FOLLOWS API VIEWS (apps/follows/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha YENGIL VIEWLAR (Thin Views).
Faqat `selectors.py` va `services.py` dan foydalanadi.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from core.responses import APIResponse
from core.pagination import StandardResultsSetPagination
from .services import FollowService
from .selectors import FollowSelector
from .serializers import FollowerReadSerializer, FollowingReadSerializer


class FollowUserApi(APIView):
    """Kitobxonga obuna bo'lish yoki almashtirish (Toggle) API."""
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id: str):
        follow_obj, created = FollowService.toggle_follow(follower=request.user, following_id=user_id)
        if not created:
            return APIResponse(message="Obuna bekor qilindi.", status_code=status.HTTP_200_OK)

        serializer = FollowingReadSerializer(follow_obj)
        return APIResponse(data=serializer.data, message="Muvaffaqiyatli obuna bo'lindi.", status_code=status.HTTP_201_CREATED)


class UnfollowUserApi(APIView):
    """Obunani bekor qilish API."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id: str):
        FollowService.unfollow_user(follower=request.user, following_id=user_id)
        return APIResponse(message="Obuna bekor qilindi.", status_code=status.HTTP_200_OK)


class UserFollowersListApi(APIView):
    """Foydalanuvchining obunachilarini (Followers) o'qish API."""
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get(self, request, user_id: str):
        followers = FollowSelector.get_followers(user_id)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(followers, request, view=self)
        serializer = FollowerReadSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class UserFollowingListApi(APIView):
    """Foydalanuvchi kuzatayotgan (Following) shaxslar ro'yxatini o'qish API."""
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get(self, request, user_id: str):
        following = FollowSelector.get_following(user_id)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(following, request, view=self)
        serializer = FollowingReadSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
