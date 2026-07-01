"""
OKJ PLATFORM - COMMENTS URLS (apps/comments/urls.py)
Nega bu fayl kerak: /api/v1/posts/{post_id}/comments/ va /api/v1/comments/{comment_id}/ marshrutlari.
"""

from django.urls import path
from .apis import PostCommentListCreateApi, CommentDetailApi

urlpatterns = [
    path("posts/<str:post_id>/comments/", PostCommentListCreateApi.as_view(), name="post-comments"),
    path("comments/<str:comment_id>/", CommentDetailApi.as_view(), name="comment-detail"),
]
