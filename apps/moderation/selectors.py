"""
OKJ PLATFORM - MODERATION SELECTORS (apps/moderation/selectors.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha barcha o'qish (Read)
amallari va moderatsiya navbati selektorlarda joylashishi shart.
"""

from typing import Optional
from django.db import connections, OperationalError
from .models import ContentReport, UserModerationFlag


def _verify_postgres():
    """
    Twelve-Factor & Infrastructure qoidasi:
    Bu modul faqat PostgreSQL'da ishlaydi. SQLite ruxsat etilmaydi.
    """
    if connections["default"].vendor != "postgresql":
        raise OperationalError(
            "Bu modul faqat PostgreSQL'da ishlaydi. SQLite ruxsat etilmaydi."
        )


class ModerationSelector:
    """Moderatsiya nazorati va navbat selektorlari."""

    @classmethod
    def get_pending_queue(cls):
        """Kelib tushgan va ko'rib chiqilmadi (PENDING) barcha shikoyatlar navbati."""
        _verify_postgres()
        return ContentReport.objects.filter(
            status=ContentReport.ReportStatus.PENDING
        ).select_related("reporter").order_by("created_at")

    @classmethod
    def get_report_by_id(cls, report_id) -> Optional[ContentReport]:
        """ID bo'yicha shikoyatni topish."""
        _verify_postgres()
        return ContentReport.objects.filter(id=report_id).select_related("reporter").first()

    @classmethod
    def get_user_moderation_flag(cls, user_id) -> Optional[UserModerationFlag]:
        """Kitobxonning moderatsiya flaglarini olish."""
        _verify_postgres()
        return UserModerationFlag.objects.filter(user_id=user_id).first()
