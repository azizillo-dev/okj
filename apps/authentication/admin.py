"""
OKJ PLATFORM - AUTHENTICATION ADMIN PANEL (apps/authentication/admin.py)
Nega bu fayl kerak: Boshqaruv paneli orqali SMS kodlar, faol seanslar va
xavfsizlik audit loglarini nazorat qilish.
"""

from django.contrib import admin
from .models import OTPCode, UserDevice, LoginHistory


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "code", "purpose", "is_used", "expires_at", "created_at")
    list_filter = ("purpose", "is_used", "created_at")
    search_fields = ("phone_number",)
    readonly_fields = ("id", "code", "created_at", "updated_at")


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ("user", "device_name", "device_type", "is_trusted", "is_active", "last_active_at")
    list_filter = ("device_type", "is_trusted", "is_active")
    search_fields = ("user__username", "user__phone_number", "device_id")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "user", "ip_address", "status", "failure_reason", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("phone_number", "ip_address")
    readonly_fields = ("id", "created_at", "updated_at")
