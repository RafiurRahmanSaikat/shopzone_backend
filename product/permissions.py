# product/permissions.py
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrStoreOwner(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.role in ["admin", "store_owner"]
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.role == "admin":
            return True
        if request.method in SAFE_METHODS:
            return True
        # For store owners, ensure the product’s store is theirs.
        return obj.store.owner == request.user


# from rest_framework.permissions import SAFE_METHODS, BasePermission


# class IsAdminOrStoreOwner(BasePermission):

#     def has_permission(self, request, view):

#         if request.method in SAFE_METHODS:
#             return True

#         if request.user.is_authenticated:
#             if request.user.role == "admin":
#                 return True

#             if request.user.role in ["store_owner", "admin"]:
#                 return True

#         return False

#     def has_object_permission(self, request, view, obj):
#         if request.user.is_authenticated and request.user.role == "admin":
#             return True

#         if request.user.is_authenticated and request.user.role in [
#             "store_owner",
#             "admin",
#         ]:
#             return obj.store.owner == request.user

#         if request.method in SAFE_METHODS:
#             return True

#         return False
