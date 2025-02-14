# store/permissions.py
from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow if the user is authenticated and is either staff/admin or the owner of the store.
        return request.user.is_authenticated and (
            request.user.is_staff or obj.owner == request.user
        )
