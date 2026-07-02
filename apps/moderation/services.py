"""
OKJ PLATFORM - MODERATION SERVICES (apps/moderation/services.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha barcha yozish (Insert/Update)
va Trust & Safety biznes qoidalari faqat shu servislar ichida bajarilishi shart.
"""

from typing import Optional
from django.db import transaction
from django.utils import timezone
from core.exceptions import ApplicationError
from shared.services import BaseService
from accounts.models import User
from posts.models import Post
from comments.models import Comment
from books.models import Book
from .models import ContentReport, UserModerationFlag
from .selectors import _verify_postgres


class ModerationService(BaseService):
    """Trust & Safety va kontent moderatsiyasi servisi."""

    @classmethod
    @transaction.atomic
    def report_content(
        cls,
        reporter: User,
        content_type: str,
        target_id,
        reason: str,
        description: Optional[str] = None,
    ) -> ContentReport:
        """
        Foydalanuvchi tomonidan kontent ustidan shikoyat qoldirish mantiqi.
        """
        _verify_postgres()
        content_type = content_type.upper().strip()

        # Target kontent borligini tekshiramiz
        if content_type == ContentReport.ContentType.POST:
            if not Post.all_objects.filter(id=target_id).exists():
                raise ApplicationError("Shikoyat qilinayotgan post topilmadi.")
        elif content_type == ContentReport.ContentType.COMMENT:
            if not Comment.objects.filter(id=target_id).exists():
                raise ApplicationError("Shikoyat qilinayotgan izoh topilmadi.")
        elif content_type == ContentReport.ContentType.BOOK:
            if not Book.objects.filter(id=target_id).exists():
                raise ApplicationError("Shikoyat qilinayotgan kitob topilmadi.")
        else:
            raise ApplicationError("Noma'lum kontent turi.")

        report = ContentReport.objects.create(
            reporter=reporter,
            content_type=content_type,
            target_id=target_id,
            reason=reason,
            description=description or "",
            status=ContentReport.ReportStatus.PENDING,
        )
        return report

    @classmethod
    @transaction.atomic
    def resolve_report(
        cls,
        moderator: User,
        report_id,
        action: str,
        notes: Optional[str] = None,
    ) -> ContentReport:
        """
        Moderator qarori (Faqat Staff/Superuser).
        Agar action == 'APPROVE_AND_BLOCK' bo'lsa, kontent soft-delete bo'ladi.
        Agar action == 'DISMISS' bo'lsa, shikoyat rad etiladi.
        """
        _verify_postgres()
        if not (moderator.is_staff or moderator.is_superuser):
            raise ApplicationError("Faqat moderatorlar yoki adminlar shikoyatni hal qila oladi.")

        report = ContentReport.objects.select_for_update().filter(id=report_id).first()
        if not report:
            raise ApplicationError("Shikoyat topilmadi.")

        action = action.upper().strip()

        if action == "APPROVE_AND_BLOCK":
            # Kontentni bloklash (Soft Delete)
            if report.content_type == ContentReport.ContentType.POST:
                post = Post.all_objects.filter(id=report.target_id).first()
                if post:
                    post.is_deleted = True
                    post.moderation_status = Post.ModerationStatus.REJECTED
                    post.save(update_fields=["is_deleted", "moderation_status", "updated_at"])
            elif report.content_type == ContentReport.ContentType.COMMENT:
                comment = Comment.objects.filter(id=report.target_id).first()
                if comment:
                    comment.is_deleted = True
                    comment.is_approved = False
                    comment.save(update_fields=["is_deleted", "is_approved", "updated_at"])
            elif report.content_type == ContentReport.ContentType.BOOK:
                book = Book.objects.filter(id=report.target_id).first()
                if book:
                    book.is_deleted = True
                    book.verification_status = Book.VerificationStatus.REJECTED
                    book.save(update_fields=["is_deleted", "verification_status", "updated_at"])

            report.status = ContentReport.ReportStatus.RESOLVED
            report.moderator_notes = notes or "Kontent bloklandi."
            report.save(update_fields=["status", "moderator_notes", "updated_at"])

        elif action == "DISMISS":
            report.status = ContentReport.ReportStatus.DISMISSED
            report.moderator_notes = notes or "Shikoyat rad etildi."
            report.save(update_fields=["status", "moderator_notes", "updated_at"])
        else:
            raise ApplicationError("Noma'lum qaror amali (action).")

        return report

    @classmethod
    @transaction.atomic
    def admin_toggle_shadow_ban(
        cls,
        user_id,
        is_ban: bool,
        admin_user: Optional[User] = None,
    ) -> UserModerationFlag:
        """
        Admin tomonidan foydalanuvchiga shadow ban berish yoki echish mantiqi (Faqat Superuser).
        """
        _verify_postgres()
        if admin_user and not admin_user.is_superuser:
            raise ApplicationError("Faqat superuser shadow ban bera oladi.")

        user = User.objects.filter(id=user_id, is_deleted=False).first()
        if not user:
            raise ApplicationError("Kitobxon topilmadi.")

        flag, _ = UserModerationFlag.objects.select_for_update().get_or_create(user=user)
        flag.is_shadow_banned = is_ban
        flag.shadow_banned_at = timezone.now() if is_ban else None
        flag.shadow_banned_by = admin_user if is_ban else None
        flag.save()
        return flag
