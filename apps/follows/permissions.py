"""
OKJ PLATFORM - FOLLOWS PERMISSIONS (apps/follows/permissions.py)
Nega bu fayl kerak: Faqat autentifikatsiyadan o'tgan kitobxonlar obuna bo'la oladi.
"""

from rest_framework import permissions


class IsAuthenticatedForFollow(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
