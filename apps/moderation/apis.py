"""
OKJ PLATFORM - MODERATION APIS (apps/moderation/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha API ko'rinishlari (Views)
maksimal darajada yupqa (Thin Views) bo'lib, biznes qoidalar va validatsiyani
selektorlar/servislarga topshiriqi shart.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from core.pagination import StandardResultsSetPagination
from .selectors import ModerationSelector
from .services import ModerationService
from .serializers import (
    ReportContentInputSerializer,
    ContentReportReadSerializer,
    ResolveReportInputSerializer,
)


class IsStaffModerator(permissions.BasePermission):
    """Faqat is_staff=True (yoki is_superuser=True) bo'lgan moderatorlar uchun ruxsat."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        )


class ReportContentApi(APIView):
    """
    Kontent ustidan shikoyat qilish:
    POST /api/v1/moderation/report/ (Hamma kitobxonlar uchun, Authenticated)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReportContentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report = ModerationService.report_content(
            reporter=request.user,
            **serializer.validated_data
        )
        read_serializer = ContentReportReadSerializer(report)
        return Response(
            {"success": True, "message": "Shikoyat yuborildi.", "data": read_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class ModerationQueueApi(APIView):
    """
    Kelib tushgan PENDING shikoyatlar ro'yxati:
    GET /api/v1/moderation/queue/ (Faqat is_staff=True, Paginatsiya bilan)
    """
    permission_classes = [IsStaffModerator]

    def get(self, request):
        queryset = ModerationSelector.get_pending_queue()
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = ContentReportReadSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class ResolveReportApi(APIView):
    """
    Shikoyatni ko'rib chiqish va kontentni bloklash:
    POST /api/v1/moderation/reports/{id}/resolve/ (Faqat is_staff=True)
    """
    permission_classes = [IsStaffModerator]

    def post(self, request, id):
        serializer = ResolveReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report = ModerationService.resolve_report(
            moderator=request.user,
            report_id=id,
            **serializer.validated_data
        )
        read_serializer = ContentReportReadSerializer(report)
        return Response(
            {"success": True, "message": "Shikoyat ko'rib chiqildi.", "data": read_serializer.data},
            status=status.HTTP_200_OK,
        )
