import django_filters

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
