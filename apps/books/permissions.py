"""
OKJ PLATFORM - BOOKS PERMISSIONS (apps/books/permissions.py)
Nega bu fayl kerak: Barcha kitobxonlar kitoblarni qo'sha oladi (qoralama sifatida),
lekin ularni rasman tasdiqlash va o'chirish faqat Kurator/Adminlar ruxsatiga bog'liq.
"""

from rest_framework import permissions


class IsCuratorOrReadOnly(permissions.BasePermission):
    """O'qish barchaga ochiq, tahrirlash va tasdiqlash faqat kuratorlar uchun."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "is_curator", False))
