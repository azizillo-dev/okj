"""
OKJ PLATFORM - MODERATION ADMIN PANEL (apps/moderation/admin.py)
Nega bu fayl kerak: Boshqaruv paneli (Django Admin) orqali markazlashgan
shikoyatlar navbatini (ContentReport) va operatsion audit loglarini boshqarish.
"""

from django.contrib import admin
from .models import ContentReport, UserModerationFlag, AdminActionLog
from .services import ModerationService


@admin.register(ContentReport)
class ModerationQueueAdmin(admin.ModelAdmin):
    list_display = ("reporter", "content_type", "reason", "status", "created_at")
    list_filter = ("content_type", "status", "reason")
    search_fields = ("reporter__username", "target_id", "description", "moderator_notes")
    readonly_fields = ("id", "reporter", "content_type", "target_id", "reason", "description", "created_at", "updated_at")
    actions = ["resolve_and_block", "dismiss_report"]

    @admin.action(description="Shikoyatni tasdiqlash va kontentni bloklash (resolve_and_block)")
    def resolve_and_block(self, request, queryset):
        for report in queryset:
            if report.status == ContentReport.ReportStatus.PENDING:
                ModerationService.resolve_report(
                    moderator=request.user,
                    report_id=report.id,
                    action="APPROVE_AND_BLOCK",
                    notes="Admin paneli orqali bloklandi",
                )
                AdminActionLog.objects.create(
                    actor=request.user,
                    target_user=report.reporter,
                    action_type="RESOLVE_REPORT",
                    reason=f"Shikoyat {report.id} tasdiqlandi va kontent bloklandi",
                    metadata={"report_id": str(report.id), "action": "APPROVE_AND_BLOCK"},
                )
        self.message_user(request, "Tanlangan shikoyatlar ko'rib chiqildi va kontent bloklandi.")

    @admin.action(description="Shikoyatni rad etish (dismiss_report)")
    def dismiss_report(self, request, queryset):
        for report in queryset:
            if report.status == ContentReport.ReportStatus.PENDING:
                ModerationService.resolve_report(
                    moderator=request.user,
                    report_id=report.id,
                    action="DISMISS",
                    notes="Admin paneli orqali rad etildi",
                )
                AdminActionLog.objects.create(
                    actor=request.user,
                    target_user=report.reporter,
                    action_type="RESOLVE_REPORT",
                    reason=f"Shikoyat {report.id} rad etildi",
                    metadata={"report_id": str(report.id), "action": "DISMISS"},
                )
        self.message_user(request, "Tanlangan shikoyatlar rad etildi.")


@admin.register(UserModerationFlag)
class UserModerationFlagAdmin(admin.ModelAdmin):
    list_display = ("user", "is_shadow_banned", "shadow_banned_at", "shadow_banned_by")
    list_filter = ("is_shadow_banned",)
    search_fields = ("user__username", "user__okj_id")
    readonly_fields = ("user", "is_shadow_banned", "shadow_banned_at", "shadow_banned_by", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False


@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action_type", "target_user", "created_at")
    list_filter = ("action_type", "created_at")
    search_fields = ("actor__username", "target_user__username", "reason")
    readonly_fields = ("id", "actor", "target_user", "action_type", "reason", "metadata", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
