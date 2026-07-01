"""
OKJ PLATFORM - API RESPONSE HELPER (core/responses.py)
Nega bu fayl kerak: APIView va ViewSet javoblarida `Response({"success": True, "data": ...})`
standartini buzmasdan yozishni ta'minlovchi yordamchi sinflar.
"""

from rest_framework.response import Response
from rest_framework import status


class APIResponse(Response):
    """Standartlashtirilgan muvaffaqiyatli API javobi."""
    def __init__(self, data=None, message="Muvaffaqiyatli", status_code=status.HTTP_200_OK, **kwargs):
        payload = {
            "success": True,
            "message": message,
            "data": data,
        }
        super().__init__(data=payload, status=status_code, **kwargs)
