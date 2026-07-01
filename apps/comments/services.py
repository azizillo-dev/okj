"""
OKJ PLATFORM - COMMENTS SERVICES (apps/comments/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA YOZISH amallari,
maksimal 2-darajali (Flat-Tree) ierarxiya va XP gamifikatsiyasi nazorati
@transaction.atomic ostida bajariladi.
"""

from typing import Optional
from django.db import transaction
from django.utils import timezone
from core.exceptions import ApplicationError
from shared.services import BaseService
from posts.selectors import PostSelector
from .models import Comment
from .validators import validate_comment_text


class CommentService(BaseService):
    """Izohlar yaratish, tahrirlash, o'chirish va Flat-Tree ierarxiyasini boshqarish servisi."""

    @classmethod
    @transaction.atomic
    def create_comment(
        cls,
        user,
        post_id,
        text: str,
        parent_id: Optional[str] = None,
    ) -> Comment:
        """
        Yangi izoh yoki javob yozish.
        Flat-Tree qoidasi: Agar parent_id berilgan bo'lsa va u o'zi ham
        boshqa izohga reply bo'lsa, uning parent_id-si Root Commentga bog'lanadi.
        """
        validate_comment_text(text)

        post = PostSelector.get_post_by_id(post_id)
        if not post or post.is_deleted:
            raise ApplicationError("Post topilmadi yoki o'chirilgan.", code="POST_NOT_FOUND")

        target_parent = None
        is_root = True

        if parent_id:
            parent_comment = Comment.objects.filter(id=parent_id, post_id=post_id).first()
            if not parent_comment:
                raise ApplicationError("Ota izoh topilmadi.", code="PARENT_NOT_FOUND")

            # Flat-Tree qoidasi: Agar parent_comment ning o'zi ham reply bo'lsa,
            # uning otasini (Root) olib beramiz (maksimal chuqurlik = 2 daraja)
            target_parent = parent_comment.parent if parent_comment.parent_id else parent_comment
            is_root = False

        comment = Comment.objects.create(
            post=post,
            user=user,
            parent=target_parent,
            text=text.strip(),
        )

        # Gamifikatsiya qoidasi: Faqat Root Comment (Level 0) uchun 5 XP beriladi.
        # Reply (javoblar) uchun XP berilmaydi (spam oldini olish uchun).
        if is_root:
            from accounts.services import UserService
            UserService.add_xp(user=user, amount=5, reason="Postga izoh qoldirildi")

        return comment

    @classmethod
    @transaction.atomic
    def update_comment(cls, user, comment_id, text: str) -> Comment:
        """Izohni tahrirlash (Faqat izoh muallifi uchun)."""
        validate_comment_text(text)

        comment = Comment.objects.select_related("user").filter(id=comment_id).first()
        if not comment or comment.is_deleted:
            raise ApplicationError("Izoh topilmadi yoki o'chirilgan.", code="COMMENT_NOT_FOUND")

        if comment.user != user:
            raise ApplicationError("Siz faqat o'zingizning izohingizni tahrirlashingiz mumkin.", code="PERMISSION_DENIED")

        comment.text = text.strip()
        comment.save(update_fields=["text", "updated_at"])
        return comment

    @classmethod
    @transaction.atomic
    def soft_delete_comment(cls, user, comment_id) -> None:
        """
        Izohni soft delete qilish (Faqat izoh muallifi yoki post egasi).
        Ota izoh o'chirilganda uning javoblari o'chmaydi (Serializer interpretatsiyasi).
        """
        comment = Comment.objects.select_related("user", "post").filter(id=comment_id).first()
        if not comment or comment.is_deleted:
            raise ApplicationError("Izoh topilmadi yoki avval o'chirilgan.", code="COMMENT_NOT_FOUND")

        # Ruxsat: Izoh egasi yoki Post egasi
        if comment.user != user and comment.post.user != user:
            raise ApplicationError("Izohni o'chirish huquqingiz yo'q.", code="PERMISSION_DENIED")

        comment.is_deleted = True
        comment.deleted_at = timezone.now()
        comment.save(update_fields=["is_deleted", "deleted_at"])
