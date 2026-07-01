"""
OKJ PLATFORM - LIBRARY MODELS (apps/library/models.py)
Nega bu fayl kerak: Kitobxonning shaxsiy javoni (Want to Read, Reading, Finished, Dropped),
sevimlilar ro'yxati, kunlik o'qish loglari, olovchalar (streaklar) va yillik/oylik maqsadlarini saqlash.
"""

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from core.models import UUIDModel, TimeStampedModel
from books.models import Book
from .validators import (
    validate_user_rating,
    validate_positive_pages,
    validate_challenge_year,
    validate_challenge_month,
)


class LibraryItem(UUIDModel, TimeStampedModel):
    """
    Kitobxonning shaxsiy kutubxonasidagi kitob holati.
    Nega kerak: Kitobxon kitobni qaysi javonga qo'ygani, necha sahifa o'qigani va o'z bahosini bilish.
    """
    class ReadingStatus(models.TextChoices):
        WANT_TO_READ = "WANT_TO_READ", "O'qishni xohlayman"
        READING = "READING", "Hozir o'qiyapman"
        FINISHED = "FINISHED", "O'qib bo'ldim"
        DROPPED = "DROPPED", "Tashlab ketdim"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="library_items"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="library_items")
    status = models.CharField(
        max_length=20, choices=ReadingStatus.choices, default=ReadingStatus.WANT_TO_READ, db_index=True
    )
    is_favorite = models.BooleanField(default=False, db_index=True)
    current_page = models.PositiveIntegerField(default=0, validators=[validate_positive_pages])
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    user_rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_user_rating], db_index=True
    )
    notes = models.TextField(blank=True, help_text="Shaxsiy qaydlar")

    class Meta:
        verbose_name = "Kutubxona Kitobi"
        verbose_name_plural = "Kutubxona Kitoblari"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "book"], name="unique_user_book_shelf")
        ]
        indexes = [
            models.Index(fields=["user", "status", "-updated_at"], name="idx_lib_user_status"),
            models.Index(fields=["user", "is_favorite"], name="idx_lib_user_fav"),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.book.title} ({self.status})"


class ReadingLog(TimeStampedModel):
    """
    Kunlik o'qish logi (Duolingo / GitHub tarzida kunlik faollikni yozish).
    Nega kerak: Heatmap (faollik xaritasi) va olovchani (streak) hisoblash.
    """
    library_item = models.ForeignKey(LibraryItem, on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reading_logs", db_index=True
    )
    pages_read = models.PositiveIntegerField(validators=[validate_positive_pages], help_text="Joriy sessiyada o'qilgan sahifalar")
    minutes_spent = models.PositiveIntegerField(default=0, help_text="O'qishga sarflangan daqiqalar")
    log_date = models.DateField(default=timezone.now, db_index=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "O'qish Logi"
        verbose_name_plural = "O'qish Loglari"
        ordering = ["-log_date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "log_date"], name="idx_log_user_date"),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.pages_read} bet ({self.log_date})"


class UserReadingStatistic(TimeStampedModel):
    """
    Kitobxonning 1-to-1 umumlashgan o'qish statistikasi va olovcha (streak) hisoblagichi.
    Nega kerak: Har safar minglab loglarni yig'masdan tezkor profil ma'lumotini ko'rsatish.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reading_statistics", primary_key=True
    )
    total_books_finished = models.PositiveIntegerField(default=0)
    total_pages_read = models.PositiveIntegerField(default=0)
    total_minutes_spent = models.PositiveIntegerField(default=0)
    current_streak_days = models.PositiveIntegerField(default=0)
    longest_streak_days = models.PositiveIntegerField(default=0)
    last_log_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "O'qish Statistikasi"
        verbose_name_plural = "O'qish Statistikalari"

    def __str__(self):
        return f"{self.user.username} (Streak: {self.current_streak_days} kun)"


class ReadingGoal(TimeStampedModel):
    """
    Yillik va oylik o'qish chaqiriqlari (Challenge / Goal).
    Nega kerak: Kitobxonga o'zi uchun maqsad qo'yish (m-n: 2026 yilda 24 ta kitob o'qish).
    """
    class PeriodType(models.TextChoices):
        YEARLY = "YEARLY", "Yillik Challenge"
        MONTHLY = "MONTHLY", "Oylik Challenge"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reading_goals"
    )
    period_type = models.CharField(max_length=10, choices=PeriodType.choices, default=PeriodType.YEARLY)
    target_year = models.PositiveSmallIntegerField(validators=[validate_challenge_year], db_index=True)
    target_month = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_challenge_month], db_index=True
    )
    target_books = models.PositiveIntegerField(default=12, validators=[validate_positive_pages])
    completed_books = models.PositiveIntegerField(default=0)
    target_pages = models.PositiveIntegerField(default=0)
    completed_pages = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "O'qish Maqsadi (Challenge)"
        verbose_name_plural = "O'qish Maqsadlari"
        ordering = ["-target_year", "-target_month"]
        constraints = [
            models.UniqueConstraint(fields=["user", "period_type", "target_year", "target_month"], name="unique_user_period_goal")
        ]

    def __str__(self):
        period = f"{self.target_year}-{self.target_month}" if self.target_month else f"{self.target_year}"
        return f"{self.user.username} — {self.period_type} ({period}): {self.completed_books}/{self.target_books}"
