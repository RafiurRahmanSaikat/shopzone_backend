from rest_framework import serializers

from .models import Cart, CartItem, Order, OrderProduct


def _build_image_url(image_value, request):
    if not image_value:
        return None

    image_url = str(image_value)
    if request and image_url.startswith(("/", "media/")):
        return request.build_absolute_uri(image_url)

    return image_url


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.FloatField(source="product.price", read_only=True)
    product_image = serializers.SerializerMethodField()
    total_price = serializers.FloatField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_price",
            "product_image",
            "quantity",
            "total_price",
        ]
        read_only_fields = ["id", "product_name", "product_price", "total_price"]

    def get_product_image(self, obj):
        request = self.context.get("request") if hasattr(self, "context") else None
        return _build_image_url(obj.product.image, request)


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    item_subtotal = serializers.FloatField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "cart_items", "item_subtotal"]
        read_only_fields = ["id", "user", "cart_items", "item_subtotal"]


class OrderProductSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_price = serializers.ReadOnlyField(source="product.price")
    product_image = serializers.SerializerMethodField()
    total_price = serializers.FloatField(read_only=True)

    class Meta:
        model = OrderProduct
        fields = [
            "id",
            "product",
            "product_name",
            "product_price",
            "product_image",
            "quantity",
            "total_price",
        ]

    def get_product_image(self, obj):
        request = self.context.get("request") if hasattr(self, "context") else None
        return _build_image_url(obj.product.image, request)


class OrderSerializer(serializers.ModelSerializer):

    order_products = OrderProductSerializer(many=True, read_only=True)

    item_subtotal = serializers.FloatField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "order_id",
            "user",
            "status",
            "created_at",
            "order_products",
            "item_subtotal",
        ]


class OrderCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(required=False, min_value=1)
    from_cart = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        user = self.context["request"].user

        if data.get("from_cart"):
            if "product_id" in data or "quantity" in data:
                raise serializers.ValidationError(
                    "Cannot provide product_id or quantity when ordering from cart."
                )
            cart = Cart.objects.filter(user=user).first()
            if not cart or not cart.cart_items.exists():
                raise serializers.ValidationError("Your cart is empty.")
        elif "product_id" not in data or "quantity" not in data:
            raise serializers.ValidationError(
                "Provide both product_id and quantity for single-product orders."
            )

        return data


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.StatusChoices.choices)
