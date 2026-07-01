"""
OKJ PLATFORM - AUTHENTICATION PERMISSIONS (apps/authentication/permissions.py)
Nega bu fayl kerak: Qurilmani yoki kirish auditini faqat seans egasi boshqarishini nazorat qilish.
"""

from rest_framework import permissions


class IsDeviceOwner(permissions.BasePermission):
    """Qurilma yoki sessiya egasi ekanligini tekshirish."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
