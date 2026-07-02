"""
OKJ PLATFORM - MODERATION SERIALIZERS (apps/moderation/serializers.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha ma'lumotlarni
API ko'rinishida transport qilish va validatsiya qilish uchun toza transport qatlami.
"""

from rest_framework import serializers
from .models import ContentReport


class ReportContentInputSerializer(serializers.Serializer):
    """Kontent ustidan shikoyat qilish kirish ma'lumotlari."""
    content_type = serializers.ChoiceField(choices=ContentReport.ContentType.choices)
    target_id = serializers.UUIDField()
    reason = serializers.ChoiceField(choices=ContentReport.ReportReason.choices)
    description = serializers.CharField(required=False, allow_blank=True, default="")


class ContentReportReadSerializer(serializers.ModelSerializer):
    """Shikoyatlarni moderatorga ko'rsatish uchun serializator."""
    reporter_username = serializers.CharField(source="reporter.username", read_only=True)

    class Meta:
        model = ContentReport
        fields = (
            "id",
            "reporter_username",
            "content_type",
            "target_id",
            "reason",
            "description",
            "status",
            "moderator_notes",
            "created_at",
        )


class ResolveReportInputSerializer(serializers.Serializer):
    """Shikoyat bo'yicha qaror qabul qilish kirish ma'lumotlari."""
    action = serializers.ChoiceField(choices=["APPROVE_AND_BLOCK", "DISMISS"])
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class ShadowBanInputSerializer(serializers.Serializer):
    """Shadow ban holatini o'zgartirish kirish ma'lumotlari."""
    user_id = serializers.UUIDField()
    is_ban = serializers.BooleanField()
