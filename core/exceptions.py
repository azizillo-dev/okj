"""
OKJ PLATFORM - EXCEPTION HANDLER (core/exceptions.py)
Nega bu fayl kerak: Barcha xatoliklar (500, 400, 401, 403, 404) mobil ilova (Flutter) va
Next.js uchun bir xil standart JSON formatida (`success: false, code: "...", message: "..."`) qaytishi shart.
"""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404

logger = logging.getLogger(__name__)


class ApplicationError(Exception):
    """Biznes logikada yuz beradigan kutilgan xatoliklar uchun umumiy klass."""
    def __init__(self, message: str, code: str = "APPLICATION_ERROR", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


def sentry_before_send(event, hint):
    """
    ApplicationError (400 biznes xatoliklari) Sentry'ga yuborilmasligini
    ta'minlovchi before_send hook. Faqat 500 va kutilmagan xatolar yuboriladi.
    """
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        if isinstance(exc_value, ApplicationError):
            return None
    return event


def custom_exception_handler(exc, context):
    """DRF standart xatolarni ushlaydi va standart javob obyekti shakllantiradi."""
    # Agar bu bizning ApplicationError bo'lsa
    if isinstance(exc, ApplicationError):
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": None,
                },
            },
            status=exc.status_code,
        )

    # Django core ValidationError larni DRF formatga o'tkazish
    if isinstance(exc, DjangoValidationError):
        return Response(
            {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Kiritilgan ma'lumotlarda xatolik mavjud.",
                    "details": exc.message_dict if hasattr(exc, "message_dict") else {"detail": exc.messages},
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # DRF ning standart exception handlerini chaqiramiz
    response = exception_handler(exc, context)

    if response is not None:
        error_code = response.data.get("code") or response.data.get("detail", "API_ERROR")
        if isinstance(error_code, str) and len(error_code) > 50:
            error_code = "INVALID_REQUEST"

        response.data = {
            "success": False,
            "error": {
                "code": str(response.status_code),
                "message": str(response.data.get("detail", "So'rovni bajarishda xatolik yuz berdi.")),
                "details": response.data if "detail" not in response.data else None,
            },
        }
    else:
        # 500 Internal Server Error (Kutilmagan tizim xatoligi)
        logger.exception("Kutilmagan xatolik yuz berdi", exc_info=exc)
        try:
            import sentry_sdk
            sentry_sdk.capture_exception(exc)
        except Exception:
            pass
        return Response(
            {
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Tizimda kutilmagan xatolik yuz berdi. Iltimos keyinroq urinib ko'ring.",
                    "details": None,
                },
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
