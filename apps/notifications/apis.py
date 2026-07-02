"""
OKJ PLATFORM - NOTIFICATIONS API VIEWS (apps/notifications/apis.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha YENGIL VIEWLAR (Thin Views).
Faqat `selectors.py` va `services.py` dan foydalanadi.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.responses import APIResponse
from core.pagination import StandardResultsSetPagination
from .selectors import NotificationSelector
from .services import NotificationService
from .serializers import NotificationReadSerializer


class NotificationInboxApi(APIView):
    """Kitobxonning bildirishnomalar qutisi (Inbox) API."""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        is_read_param = request.query_params.get("is_read")
        is_read = None
        if is_read_param is not None:
            is_read = is_read_param.lower() in ["true", "1", "yes"]

        notifications = NotificationSelector.get_user_notifications(request.user.id, is_read=is_read)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(notifications, request, view=self)
        serializer = NotificationReadSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class UnreadCountApi(APIView):
    """O'qilmagan bildirishnomalar sonini o'qish API."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = NotificationSelector.get_unread_count(request.user.id)
        return APIResponse(data={"unread_count": count})


class MarkAsReadApi(APIView):
    """Bitta bildirishnomani o'qilgan deb belgilash API."""
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id: str):
        notif = NotificationService.mark_as_read(user=request.user, notification_id=notification_id)
        serializer = NotificationReadSerializer(notif)
        return APIResponse(data=serializer.data, message="O'qilgan deb belgilandi.")


class MarkAllAsReadApi(APIView):
    """Barcha bildirishnomalarni ommaviy o'qilgan deb belgilash API."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        updated_count = NotificationService.mark_all_as_read(user=request.user)
        return APIResponse(
            data={"updated_count": updated_count},
            message=f"{updated_count} ta bildirishnoma o'qildi.",
        )
