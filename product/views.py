from core.pagination import CustomPageNumberPagination
<<<<<<< HEAD
from rest_framework import serializers, status, viewsets
=======
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status, viewsets
>>>>>>> 65956c2 (Filtering Added)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

<<<<<<< HEAD
=======
from .filters import ProductFilter
>>>>>>> 65956c2 (Filtering Added)
from .models import Brand, Category, Product, Review
from .permissions import IsAdminOrStoreOwner
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductSerializer,
    ReviewSerializer,
)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrStoreOwner]
    pagination_class = CustomPageNumberPagination
<<<<<<< HEAD
=======
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
>>>>>>> 65956c2 (Filtering Added)

    def get_queryset(self):
        qs = (
            Product.objects.all()
            .order_by("id")
            .select_related("brand", "store")
            .prefetch_related("categories", "reviews__user")
<<<<<<< HEAD
=======
            .distinct()
>>>>>>> 65956c2 (Filtering Added)
        )

        return qs

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="my_products",
        pagination_class=CustomPageNumberPagination,
    )
    def my_products(self, request):
        user = self.request.user
        if user.is_authenticated and user.role == "store_owner":
            qs = (
                Product.objects.filter(store__owner=user)
                .order_by("id")
                .select_related("brand", "store")
                .prefetch_related("categories", "reviews__user")
            )
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response(
                {"detail": "You must be a store owner to view this endpoint."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def perform_create(self, serializer):
        user = self.request.user
        store = serializer.validated_data.get("store")
        if user.is_authenticated and user.role == "admin":
            serializer.save()
        if user.is_authenticated and user.role == "store_owner":
            if store.owner == user:
                serializer.save()
            else:
                raise serializers.ValidationError(
                    {"store_id": "You can only create products for your own store."}
                )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="add_review",
    )
    def add_review(self, request, pk=None):
        product = self.get_object()
        user = request.user
        data = request.data

        if Review.objects.filter(product=product, user=user).exists():
            return Response(
                {"detail": "You have already reviewed this product."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(product=product, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def reviews(self, request, pk=None):
        product = self.get_object()
        reviews = product.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class BrandViewSet(viewsets.ModelViewSet):

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrStoreOwner]

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrStoreOwner]

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"
