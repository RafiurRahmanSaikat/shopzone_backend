import django_filters
from rest_framework import filters

from order.models import Order


class OrderFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name="created_at__date")

    class Meta:
        model = Order
        fields = {"status": ["exact"], "created_at": ["lt", "gt", "exact"]}
