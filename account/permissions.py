from rest_framework import permissions


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == "admin"
        return False


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj == request.user
