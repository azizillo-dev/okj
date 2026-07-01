"""
OKJ PLATFORM - NOTIFICATIONS PERMISSIONS (apps/notifications/permissions.py)
"""

from rest_framework import permissions


class IsAuthenticatedForNotification(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
