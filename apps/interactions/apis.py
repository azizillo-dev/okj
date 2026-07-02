"""
OKJ PLATFORM - INTERACTIONS API VIEWS (apps/interactions/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha YENGIL VIEWLAR (Thin Views).
Faqat `selectors.py` va `services.py` dan foydalanadi.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.responses import APIResponse
from posts.selectors import PostSelector
from .services import InteractionService
from .serializers import PostLikeSerializer, PostBookmarkSerializer, BookmarkCreateSerializer


class PostLikeToggleApi(APIView):
    """Postga layk bosish (yoki almashtirish) va laykni qaytib olish API."""
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id: str):
        post = PostSelector.get_post_by_id(post_id)
        if not post:
            return APIResponse(message="Post topilmadi.", status_code=status.HTTP_404_NOT_FOUND)

        like_obj, created = InteractionService.toggle_like(user=request.user, post=post)
        if not created:
            return APIResponse(message="Layk qaytib olindi.", status_code=status.HTTP_200_OK)

        serializer = PostLikeSerializer(like_obj)
        return APIResponse(data=serializer.data, message="Postga layk bosildi.", status_code=status.HTTP_201_CREATED)

    def delete(self, request, post_id: str):
        post = PostSelector.get_post_by_id(post_id)
        if not post:
            return APIResponse(message="Post topilmadi.", status_code=status.HTTP_404_NOT_FOUND)

        InteractionService.unlike_post(user=request.user, post=post)
        return APIResponse(message="Layk qaytib olindi.", status_code=status.HTTP_200_OK)


class PostBookmarkToggleApi(APIView):
    """Postni saqlab qo'yish va saqlanganlardan o'chirish API."""
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id: str):
        post = PostSelector.get_post_by_id(post_id)
        if not post:
            return APIResponse(message="Post topilmadi.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = BookmarkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        collection_name = serializer.validated_data.get("collection_name", "Asosiy")

        bm_obj, created = InteractionService.toggle_bookmark(user=request.user, post=post, collection_name=collection_name)
        if not created:
            return APIResponse(message="Post saqlanganlardan o'chirildi.", status_code=status.HTTP_200_OK)

        read_serializer = PostBookmarkSerializer(bm_obj)
        return APIResponse(data=read_serializer.data, message="Post saqlab qo'yildi.", status_code=status.HTTP_201_CREATED)

    def delete(self, request, post_id: str):
        post = PostSelector.get_post_by_id(post_id)
        if not post:
            return APIResponse(message="Post topilmadi.", status_code=status.HTTP_404_NOT_FOUND)

        InteractionService.unbookmark_post(user=request.user, post=post)
        return APIResponse(message="Post saqlanganlardan o'chirildi.", status_code=status.HTTP_200_OK)
