"""
OKJ PLATFORM - LIBRARY PERMISSIONS (apps/library/permissions.py)
Nega bu fayl kerak: Kutubxona yozuvlarini faqat uning egasi (yoki admin)
tahrirlashi va o'chirishini nazorat qilish.
"""

from rest_framework import permissions


class IsShelfOwner(permissions.BasePermission):
    """Shaxsiy kutubxona egasi ekanligini nazorat qilish."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
