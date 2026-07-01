"""
OKJ PLATFORM - ACCOUNTS ADMIN PANEL (apps/accounts/admin.py)
Nega bu fayl kerak: Boshqaruv paneli (Django Admin) orqali kitobxonlar va tumanlarni
qulay saralash, qidirish va kuratorlarni tayinlash imkoniyati.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, District


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("id", "region_name", "name", "created_at")
    list_filter = ("region_name",)
    search_fields = ("name", "region_name")
    ordering = ("region_name", "name")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "okj_id",
        "username",
        "phone_number",
        "full_name",
        "district",
        "total_xp",
        "current_streak",
        "role",
        "is_deleted",
    )
    list_filter = ("role", "is_deleted", "district__region_name", "created_at")
    search_fields = ("okj_id", "phone_number", "first_name", "last_name", "username")
    readonly_fields = ("id", "okj_id", "created_at", "updated_at")
    autocomplete_fields = ("district",)
    ordering = ("-total_xp", "-created_at")

    fieldsets = (
        ("Asosiy Pasport Ma'lumotlari", {
            "fields": ("id", "okj_id", "phone_number", "google_id", "password")
        }),
        ("Shaxsiy Profil", {
            "fields": ("first_name", "last_name", "avatar_url", "bio", "district")
        }),
        ("Gamifikasiya va Streaklar", {
            "fields": ("total_xp", "current_streak", "highest_streak")
        }),
        ("Ruxsatlar va Statuslar", {
            "fields": ("role", "is_active", "is_staff", "is_superuser", "is_deleted", "groups", "user_permissions")
        }),
        ("Sana va Vaqtlar", {
            "fields": ("last_login", "date_joined", "created_at", "updated_at")
        }),
    )
