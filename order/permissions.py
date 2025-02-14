from rest_framework import permissions


class CanManageOrderStatus(permissions.BasePermission):
    def has_permission(self, request, view):
        # Only admin and store owners can manage orders
        return request.user.is_authenticated and request.user.role in [
            "admin",
            "store_owner",
        ]

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin can do anything
        if user.role == "admin":
            return True

        # Store owner can only manage orders that contain their products
        if user.role == "store_owner":
            # Get all stores related to this order's products
            store_owners = [op.product.store.owner for op in obj.order_products.all()]
            # Check if user owns any of these stores
            return user in store_owners

        return False
