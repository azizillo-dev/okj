"""
OKJ PLATFORM - COMMENTS PERMISSIONS (apps/comments/permissions.py)
Nega bu fayl kerak: Faqat autentifikatsiyadan o'tgan kitobxonlar izoh yoza oladi.
"""

from rest_framework import permissions


class IsCommentAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
