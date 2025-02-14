from core.pagination import CustomPageNumberPagination
from order.models import Order
from order.serializers import OrderSerializer
from product.models import Product
from product.serializers import ProductSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Store, StoreCategory
from .permissions import IsOwnerOrAdmin
from .serializers import StoreCategorySerializer, StoreSerializer


class StoreCategoryViewSet(viewsets.ModelViewSet):
    queryset = StoreCategory.objects.all()
    serializer_class = StoreCategorySerializer
    permission_classes = [IsAuthenticated]

    def has_permission(self, request, view):
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return request.user.is_staff
        return True


class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        if self.request.user.role == "admin":
            return Store.objects.all()
        return Store.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"])
    def products_all(self, request):
        stores = self.get_queryset()
        products = Product.objects.filter(store__in=stores)

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
