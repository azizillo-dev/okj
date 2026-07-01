"""
OKJ PLATFORM - INTERACTIONS SERVICES (apps/interactions/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha BARCHA YOZISH amallari
(Layk bosish, qoniqmaslik, bookmark qo'shish/o'chirish) @transaction.atomic ostida.
"""

from typing import Tuple
from django.db import transaction
from django.utils import timezone
from core.exceptions import ApplicationError
from shared.services import BaseService
from .models import PostLike, PostBookmark
from posts.models import Post


class InteractionService(BaseService):
    """Postlar bilan interaksiyaga kirishish servisi."""

    @classmethod
    @transaction.atomic
    def like_post(cls, user, post: Post) -> PostLike:
        """
        Postga layk bosish. Agar avval o'chirilgan (soft deleted) layk bo'lsa uni qayta tiklash.
        """
        if post.is_deleted:
            raise ApplicationError("O'chirilgan postga layk bosib bo'lmaydi.")

        like_obj = PostLike.all_objects.filter(user=user, post=post).first()
        if like_obj:
            if like_obj.is_deleted:
                like_obj.is_deleted = False
                like_obj.deleted_at = None
                like_obj.save(update_fields=["is_deleted", "deleted_at"])
                # Layk tiklanganda XP berish yoki kelajakda bildirishnoma jo'natish
                cls._on_post_liked(user, post)
            return like_obj

        like_obj = PostLike.objects.create(user=user, post=post)
        cls._on_post_liked(user, post)
        return like_obj

    @classmethod
    @transaction.atomic
    def unlike_post(cls, user, post: Post) -> None:
        """Layqni qaytib olish (Soft Delete)."""
        like_obj = PostLike.objects.filter(user=user, post=post, is_deleted=False).first()
        if like_obj:
            like_obj.is_deleted = True
            like_obj.deleted_at = timezone.now()
            like_obj.save(update_fields=["is_deleted", "deleted_at"])

    @classmethod
    @transaction.atomic
    def toggle_like(cls, user, post: Post) -> Tuple[PostLike, bool]:
        """
        Layk holatini almashtirish (Toggle).
        Qaytadi: (PostLike yoki None, created_or_restored: bool)
        """
        active_like = PostLike.objects.filter(user=user, post=post, is_deleted=False).first()
        if active_like:
            cls.unlike_post(user=user, post=post)
            return active_like, False
        
        new_like = cls.like_post(user=user, post=post)
        return new_like, True

    @classmethod
    @transaction.atomic
    def bookmark_post(cls, user, post: Post, collection_name: str = "Asosiy") -> PostBookmark:
        """Postni saqlanganlarga qo'shish."""
        if post.is_deleted:
            raise ApplicationError("O'chirilgan postni saqlab bo'lmaydi.")

        bm_obj = PostBookmark.all_objects.filter(user=user, post=post).first()
        if bm_obj:
            if bm_obj.is_deleted or bm_obj.collection_name != collection_name:
                bm_obj.is_deleted = False
                bm_obj.deleted_at = None
                bm_obj.collection_name = collection_name
                bm_obj.save(update_fields=["is_deleted", "deleted_at", "collection_name"])
            return bm_obj

        return PostBookmark.objects.create(user=user, post=post, collection_name=collection_name)

    @classmethod
    @transaction.atomic
    def unbookmark_post(cls, user, post: Post) -> None:
        """Postni saqlanganlardan o'chirish (Soft Delete)."""
        bm_obj = PostBookmark.objects.filter(user=user, post=post, is_deleted=False).first()
        if bm_obj:
            bm_obj.is_deleted = True
            bm_obj.deleted_at = timezone.now()
            bm_obj.save(update_fields=["is_deleted", "deleted_at"])

    @classmethod
    @transaction.atomic
    def toggle_bookmark(cls, user, post: Post, collection_name: str = "Asosiy") -> Tuple[PostBookmark, bool]:
        """Bookmark holatini almashtirish (Toggle)."""
        active_bm = PostBookmark.objects.filter(user=user, post=post, is_deleted=False).first()
        if active_bm:
            cls.unbookmark_post(user=user, post=post)
            return active_bm, False

        new_bm = cls.bookmark_post(user=user, post=post, collection_name=collection_name)
        return new_bm, True

    @classmethod
    def _on_post_liked(cls, user, post: Post):
        """Layk bosilganda muallifga XP berish va kelajak notification funksiyasi zaminga tayyorlash."""
        if user != post.user:
            from accounts.services import UserService
            UserService.add_xp(user=post.user, amount=2, reason="Postga layk bosildi")
