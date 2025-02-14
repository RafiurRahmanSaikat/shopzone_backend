import django_filters
<<<<<<< HEAD
from django.db.models import Q
from rest_framework import filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            "name": ["iexact", "icontains"],
            "price": ["exact", "lt", "gt", "range"],
        }


class ProductPermissionFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        user = request.user

        if user.is_authenticated:
            if user.is_staff:
                return queryset
            if user.role in ["store_owner", "admin"]:
                return queryset.filter(Q(store__owner=user) | Q(store__manager=user))

        # Regular users only see approved products
        return queryset
=======

from .models import Category, Product


class ProductFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    categories = django_filters.ModelMultipleChoiceFilter(
        field_name="categories",
        to_field_name="id",
        queryset=Category.objects.all(),
        conjoined=False,
    )

    class Meta:
        model = Product
        fields = {
            "name": ["icontains"],
            "description": ["icontains"],
        }
>>>>>>> 65956c2 (Filtering Added)
