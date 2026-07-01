"""
OKJ PLATFORM - POSTS PERMISSIONS (apps/posts/permissions.py)
Nega bu fayl kerak: Postni faqat uning muallifi tahrirlashi, o'chirish yoki
qoralama holatidan chiqarishi mumkin.
"""

from rest_framework import permissions


class IsPostAuthorOrReadOnly(permissions.BasePermission):
    """Faqat post muallifiga tahrir huquqi, boshqalarga faqat o'qish."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
