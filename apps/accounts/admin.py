"""
OKJ PLATFORM - ACCOUNTS ADMIN PANEL (apps/accounts/admin.py)
Nega bu fayl kerak: Boshqaruv paneli (Django Admin) orqali kitobxonlar va tumanlarni
qulay saralash, qidirish va kuratorlarni tayinlash imkoniyati.
"""

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from moderation.services import ModerationService
from moderation.models import AdminActionLog
from .models import User, District
from .services import UserService


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
        "get_is_shadow_banned",
        "is_deleted",
    )
    list_filter = ("role", "is_deleted", "district__region_name", "created_at")
    search_fields = ("okj_id", "phone_number", "first_name", "last_name", "username")
    readonly_fields = ("id", "okj_id", "created_at", "updated_at")
    autocomplete_fields = ("district",)
    ordering = ("-total_xp", "-created_at")
    actions = ["ban_users", "unban_users", "grant_xp"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("moderation_flag")

    @admin.display(description="Shadow Ban", boolean=True)
    def get_is_shadow_banned(self, obj):
        if hasattr(obj, "moderation_flag"):
            return obj.moderation_flag.is_shadow_banned
        return False

    @admin.action(description="Tanlangan kitobxonlarga shadow ban berish (ban_users)")
    def ban_users(self, request, queryset):
        for user in queryset:
            ModerationService.admin_toggle_shadow_ban(user_id=user.id, is_ban=True, admin_user=request.user)
            AdminActionLog.objects.create(
                actor=request.user,
                target_user=user,
                action_type="BAN",
                reason="Admin paneli orqali shadow ban berildi",
            )
        self.message_user(request, f"{queryset.count()} ta kitobxon shadow ban qilindi.")

    @admin.action(description="Tanlangan kitobxonlardan shadow banni olib tashlash (unban_users)")
    def unban_users(self, request, queryset):
        for user in queryset:
            ModerationService.admin_toggle_shadow_ban(user_id=user.id, is_ban=False, admin_user=request.user)
            AdminActionLog.objects.create(
                actor=request.user,
                target_user=user,
                action_type="UNBAN",
                reason="Admin paneli orqali shadow ban olib tashlandi",
            )
        self.message_user(request, f"{queryset.count()} ta kitobxondan shadow ban olib tashlandi.")

    @admin.action(description="Tanlangan foydalanuvchilarga XP qo'shish (grant_xp)")
    def grant_xp(self, request, queryset):
        if "apply" in request.POST:
            try:
                amount = int(request.POST.get("xp_amount", 0))
            except ValueError:
                amount = 0
            reason = request.POST.get("reason", "Admin tomonidan qo'lda XP berildi")

            if amount > 0:
                for user in queryset:
                    UserService.add_xp(user=user, amount=amount)
                    AdminActionLog.objects.create(
                        actor=request.user,
                        target_user=user,
                        action_type="GRANT_XP",
                        reason=reason,
                        metadata={"amount": amount},
                    )
                self.message_user(request, f"{queryset.count()} ta foydalanuvchiga {amount} dan XP qo'shildi.")
            else:
                self.message_user(request, "XP miqdori 0 dan katta bo'lishi kerak.", level=messages.ERROR)
            return HttpResponseRedirect(request.get_full_path())

        context = {
            "title": "Tanlangan foydalanuvchilarga XP qo'shish",
            "users": queryset,
            "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
            "opts": self.model._meta,
        }
        return render(request, "admin/accounts/grant_xp_intermediate.html", context)

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
