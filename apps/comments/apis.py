"""
OKJ PLATFORM - COMMENTS API VIEWS (apps/comments/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha YENGIL VIEWLAR (Thin Views).
Hech qanday ORM yoki biznes mantiqi yozilmaydi, faqat `selectors.py` va `services.py`.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from core.responses import APIResponse
from .selectors import CommentSelector
from .services import CommentService
from .serializers import CommentReadSerializer, CommentWriteSerializer


class PostCommentListCreateApi(APIView):
    """Postning barcha izohlarini daraxtsimon o'qish (GET) va yangi izoh yozish (POST) API."""

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, post_id: str):
        comments = CommentSelector.get_comments_for_post(post_id)
        serializer = CommentReadSerializer(comments, many=True)
        return APIResponse(data=serializer.data)

    def post(self, request, post_id: str):
        serializer = CommentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = CommentService.create_comment(
            user=request.user,
            post_id=post_id,
            text=serializer.validated_data["text"],
            parent_id=serializer.validated_data.get("parent_id"),
        )
        read_serializer = CommentReadSerializer(comment)
        return APIResponse(
            data=read_serializer.data,
            message="Izoh muvaffaqiyatli qo'shildi.",
            status_code=status.HTTP_201_CREATED,
        )


class CommentDetailApi(APIView):
    """Izohni tahrirlash (PATCH) va soft delete qilish (DELETE) API."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, comment_id: str):
        serializer = CommentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_comment = CommentService.update_comment(
            user=request.user,
            comment_id=comment_id,
            text=serializer.validated_data["text"],
        )
        read_serializer = CommentReadSerializer(updated_comment)
        return APIResponse(data=read_serializer.data, message="Izoh yangilandi.")

    def delete(self, request, comment_id: str):
        CommentService.soft_delete_comment(user=request.user, comment_id=comment_id)
        return APIResponse(message="Izoh o'chirildi.", status_code=status.HTTP_200_OK)
