"""
OKJ PLATFORM - LIBRARY ADMIN PANEL (apps/library/admin.py)
Nega bu fayl kerak: Boshqaruv paneli orqali kitobxonlarning javonlari,
kunlik o'qilgan sahifalar va streaklarni nazorat qilish.
"""

from django.contrib import admin
from .models import LibraryItem, ReadingLog, UserReadingStatistic, ReadingGoal


@admin.register(LibraryItem)
class LibraryItemAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "status", "is_favorite", "current_page", "user_rating", "updated_at")
    list_filter = ("status", "is_favorite", "user_rating")
    search_fields = ("user__username", "user__phone_number", "book__title")
    autocomplete_fields = ("user", "book")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(ReadingLog)
class ReadingLogAdmin(admin.ModelAdmin):
    list_display = ("user", "library_item", "pages_read", "minutes_spent", "log_date")
    list_filter = ("log_date",)
    search_fields = ("user__username", "library_item__book__title")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(UserReadingStatistic)
class UserReadingStatisticAdmin(admin.ModelAdmin):
    list_display = ("user", "current_streak_days", "longest_streak_days", "total_books_finished", "total_pages_read")
    search_fields = ("user__username", "user__phone_number")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ReadingGoal)
class ReadingGoalAdmin(admin.ModelAdmin):
    list_display = ("user", "period_type", "target_year", "target_month", "completed_books", "target_books")
    list_filter = ("period_type", "target_year")
    search_fields = ("user__username",)
