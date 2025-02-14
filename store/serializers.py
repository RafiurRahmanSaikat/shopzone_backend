# store/serializers.py
from rest_framework import serializers

from .models import Store, StoreCategory


class StoreCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreCategory
        fields = ("id", "name")


class StoreSerializer(serializers.ModelSerializer):
    store_categories = StoreCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=StoreCategory.objects.all(),
        many=True,
        write_only=True,
        source="store_categories",
    )
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Store
        fields = (
            "id",
            "name",
            "address",
            "location",
            "owner",
            "store_categories",
            "category_ids",
        )
        read_only_fields = ("owner",)
