"""
OKJ PLATFORM - LIBRARY SERIALIZERS (apps/library/serializers.py)
Nega bu fayl kerak: Kutubxona kitoblari, o'qish loglari, heatmap va
maqsadlar uchun JSON validatsiya va serializatsiya.
"""

from rest_framework import serializers
from books.serializers import BookReadSerializer
from .models import LibraryItem, ReadingLog, UserReadingStatistic, ReadingGoal


class LibraryItemReadSerializer(serializers.ModelSerializer):
    """Javondagi kitobni o'qish uchun serializer (Book o'ralgan)."""
    book = BookReadSerializer(read_only=True)

    class Meta:
        model = LibraryItem
        fields = (
            "id",
            "book",
            "status",
            "is_favorite",
            "current_page",
            "started_at",
            "finished_at",
            "user_rating",
            "notes",
            "created_at",
            "updated_at",
        )


class AddShelfItemSerializer(serializers.Serializer):
    book_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=LibraryItem.ReadingStatus.choices, default=LibraryItem.ReadingStatus.WANT_TO_READ)
    is_favorite = serializers.BooleanField(default=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class UpdateShelfItemSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=LibraryItem.ReadingStatus.choices, required=False)
    is_favorite = serializers.BooleanField(required=False)
    user_rating = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class LogReadingProgressSerializer(serializers.Serializer):
    library_item_id = serializers.UUIDField()
    pages_read = serializers.IntegerField(min_value=1)
    minutes_spent = serializers.IntegerField(min_value=0, default=0)
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)


class ReadingLogReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingLog
        fields = ("id", "library_item", "pages_read", "minutes_spent", "log_date", "note", "created_at")


class UserReadingStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReadingStatistic
        fields = (
            "total_books_finished",
            "total_pages_read",
            "total_minutes_spent",
            "current_streak_days",
            "longest_streak_days",
            "last_log_date",
        )


class ReadingGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingGoal
        fields = (
            "id",
            "period_type",
            "target_year",
            "target_month",
            "target_books",
            "completed_books",
            "target_pages",
            "completed_pages",
        )


class CreateGoalSerializer(serializers.Serializer):
    period_type = serializers.ChoiceField(choices=ReadingGoal.PeriodType.choices, default=ReadingGoal.PeriodType.YEARLY)
    target_year = serializers.IntegerField(min_value=2024)
    target_month = serializers.IntegerField(min_value=1, max_value=12, required=False, allow_null=True)
    target_books = serializers.IntegerField(min_value=1, default=12)
    target_pages = serializers.IntegerField(min_value=0, default=0)
