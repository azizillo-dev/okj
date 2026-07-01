"""
OKJ PLATFORM - COMMENTS SERVICE TESTS (apps/comments/tests/test_services.py)
"""

import pytest
from accounts.models import User
from posts.models import Post
from comments.services import CommentService
from comments.serializers import CommentReadSerializer


@pytest.mark.django_db
class TestCommentService:
    def test_flat_tree_and_xp_gamification(self):
        user1 = User.objects.create_user(phone_number="+998903334455", okj_id="OKJ-91004")
        user2 = User.objects.create_user(phone_number="+998903334456", okj_id="OKJ-91005")
        user3 = User.objects.create_user(phone_number="+998903334457", okj_id="OKJ-91006")
        post = Post.objects.create(user=user1, post_type=Post.PostType.SHOWCASE, slug="flat-tree-showcase")

        # 1. Root Comment yozish (Level 0) -> +5 XP beriladi
        root = CommentService.create_comment(user=user1, post_id=post.id, text="Root izoh")
        user1.refresh_from_db()
        assert user1.xp == 5
        assert root.parent is None

        # 2. Reply yozish (Level 1) -> 0 XP beriladi
        reply1 = CommentService.create_comment(user=user2, post_id=post.id, text="1-javob", parent_id=root.id)
        user2.refresh_from_db()
        assert user2.xp == 0
        assert reply1.parent_id == root.id

        # 3. 3-darajaga urininish: reply1 ga javob yozganda ham avtomatik root ga bog'lanadi (Flat-Tree)
        reply2 = CommentService.create_comment(user=user3, post_id=post.id, text="2-javob", parent_id=reply1.id)
        assert reply2.parent_id == root.id

    def test_soft_delete_serializer_interpretation(self):
        user = User.objects.create_user(phone_number="+998903334458", okj_id="OKJ-91007")
        post = Post.objects.create(user=user, post_type=Post.PostType.QUOTE, slug="delete-interp-quote")

        root = CommentService.create_comment(user=user, post_id=post.id, text="O'chiriladigan izoh")
        CommentService.create_comment(user=user, post_id=post.id, text="Javob izoh", parent_id=root.id)

        # Soft delete qilamiz
        CommentService.soft_delete_comment(user=user, comment_id=root.id)
        root.refresh_from_db()
        assert root.is_deleted is True

        # Serializerda tekshiramiz
        data = CommentReadSerializer(root).data
        assert data["text"] == "Bu izoh muallif tomonidan o'chirilgan"
