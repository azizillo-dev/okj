"""
OKJ PLATFORM - PERMISSIONS (core/permissions.py)
Nega bu fayl kerak: Ruxsatlarni markazlashgan holda boshqarish.
m-n: Postni faqat uning muallifi o'chira oladi, kitobni esa faqat kurator tasdiqlay oladi.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """OBYEKT EOGASI RUXSATI: O'qish hamma uchun, o'zgartirish faqat muallif (user) uchun."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(obj, "user") and obj.user == request.user


class IsCurator(permissions.BasePermission):
    """KURATOR RUXSATI: Faqat is_curator=True bo'lgan kitob kuratorlari uchun."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "is_curator", False))


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """SUPERUSER RUXSATI: Oddiy foydalanuvchilar faqat ko'radi, adminlar o'zgartiradi."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
