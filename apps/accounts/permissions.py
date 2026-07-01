"""
OKJ PLATFORM - ACCOUNTS PERMISSIONS (apps/accounts/permissions.py)
Nega bu fayl kerak: Profil ma'lumotlarini faqat foydalanuvchining o'zi
tahrirlashi va xavfsizlik nazorati.
"""

from rest_framework import permissions


class IsSelfOrReadOnly(permissions.BasePermission):
    """Boshqa kitobxonlar profilni faqat ko'radi, o'zgartirish esa faqat o'ziga ruxsat etiladi."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user
