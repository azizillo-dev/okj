"""
OKJ PLATFORM - POSTS API VIEWS (apps/posts/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha YENGIL VIEWLAR (Thin Views).
Hech qanday ORM yoki biznes mantiqi yozilmaydi, faqat `selectors.py` va `services.py`.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from core.responses import APIResponse
from core.pagination import StandardResultsSetPagination
from .selectors import PostSelector
from .services import PostService
from .permissions import IsPostAuthorOrReadOnly
from .filters import filter_posts_feed
from .serializers import (
    PostReadSerializer,
    CreatePostSerializer,
    UpdatePostSerializer,
    PostReportSerializer,
)


class PostFeedApi(APIView):
    """Ijtimoiy lenta (Feed) va post yaratish API."""
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        posts = filter_posts_feed(request.query_params)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(posts, request, view=self)
        serializer = PostReadSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = CreatePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = PostService.create_post(user=request.user, **serializer.validated_data)
        read_serializer = PostReadSerializer(PostSelector.get_post_by_id(post.id))
        return APIResponse(
            data=read_serializer.data,
            message="Post muvaffaqiyatli yaratildi.",
            status_code=status.HTTP_201_CREATED,
        )


class PostDetailApi(APIView):
    """Postni o'qish, tahrirlash va o'chirish API."""
    permission_classes = [IsAuthenticated, IsPostAuthorOrReadOnly]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsPostAuthorOrReadOnly()]

    def get(self, request, slug: str):
        post = PostSelector.get_post_by_slug(slug)
        if not post:
            return APIResponse(message="Post topilmadi.", status_code=status.HTTP_404_NOT_FOUND)

        PostService.increment_post_views(post)
        serializer = PostReadSerializer(post)
        return APIResponse(data=serializer.data)

    def patch(self, request, slug: str):
        post = PostSelector.get_post_by_slug(slug)
        if not post:
            return APIResponse(message="Post topilmadi.", status_code=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, post)

        serializer = UpdatePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_post = PostService.update_post(post=post, **serializer.validated_data)
        read_serializer = PostReadSerializer(updated_post)
        return APIResponse(data=read_serializer.data, message="Post yangilandi.")

    def delete(self, request, slug: str):
        post = PostSelector.get_post_by_slug(slug)
        if not post:
            return APIResponse(message="Post topilmadi.", status_code=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, post)

        PostService.soft_delete_post(post)
        return APIResponse(message="Post o'chirildi.", status_code=status.HTTP_200_OK)


class PublishPostApi(APIView):
    """Qoralamani chop etish API."""
    permission_classes = [IsAuthenticated, IsPostAuthorOrReadOnly]

    def post(self, request, slug: str):
        post = PostSelector.get_post_by_slug(slug)
        if not post:
            return APIResponse(message="Post topilmadi.", status_code=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, post)

        published = PostService.publish_post(post)
        serializer = PostReadSerializer(published)
        return APIResponse(data=serializer.data, message="Post muvaffaqiyatli chop etildi.")


class ArchivePostApi(APIView):
    """Postni arxivlash API."""
    permission_classes = [IsAuthenticated, IsPostAuthorOrReadOnly]

    def post(self, request, slug: str):
        post = PostSelector.get_post_by_slug(slug)
        if not post:
            return APIResponse(message="Post topilmadi.", status_code=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, post)

        archived = PostService.archive_post(post)
        serializer = PostReadSerializer(archived)
        return APIResponse(data=serializer.data, message="Post arxivlandi.")


class ReportPostApi(APIView):
    """Post ustidan shikoyat yuborish API."""
    permission_classes = [IsAuthenticated]

    def post(self, request, slug: str):
        post = PostSelector.get_post_by_slug(slug)
        if not post:
            return APIResponse(message="Post topilmadi.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = PostReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        PostService.report_post(user=request.user, post=post, **serializer.validated_data)
        return APIResponse(message="Shikoyatingiz qabul qilindi va moderatsiyaga yuborildi.", status_code=status.HTTP_201_CREATED)
