import os

import stripe
from core.pagination import CustomPageNumberPagination
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from order.models import Cart, OrderProduct
from order.permissions import CanManageOrderStatus
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


from .models import Cart, CartItem, Order, OrderProduct, Product
from .permissions import CanManageOrderStatus
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    OrderCreateSerializer,
    OrderSerializer,
)


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        cart, _ = (
            Cart.objects.select_related("user")
            .prefetch_related("cart_items__product")
            .get_or_create(user=request.user)
        )

        # cart, _ = Cart.objects.prefetch_related("cart_items__product").get_or_create(
        #     user=request.user
        # )
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    # def list(self, request, *args, **kwargs):
    #     cart, _ = Cart.objects.get_or_create(user=request.user)
    #     serializer = CartSerializer(cart)
    #     return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response(
                {"detail": "Product ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        cart_item_id = kwargs.get("pk")
        cart_item = get_object_or_404(CartItem, cart=cart, id=cart_item_id)
        cart_item.delete()
        return Response(
            {"detail": "Product removed from cart."}, status=status.HTTP_204_NO_CONTENT
        )

    def update(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        cart_item_id = kwargs.get("pk")
        cart_item = get_object_or_404(CartItem, cart=cart, id=cart_item_id)

        quantity = request.data.get("quantity")
        if not quantity:
            return Response(
                {"detail": "Quantity is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            cart_item.delete()
            return Response(
                {"detail": "Product removed from cart."},
                status=status.HTTP_204_NO_CONTENT,
            )

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related("user").prefetch_related(
            "order_products",
            "order_products__product",
        )
        if user.role == "admin":
            return qs
        elif user.role == "store_owner":
            return qs.filter(order_products__product__store__owner=user).distinct()
        return qs.filter(user=user)

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.role == "admin":
    #         return Order.objects.all()
    #     elif user.role == "store_owner":
    #         # Only show orders that contain products from stores the user owns.
    #         return Order.objects.filter(
    #             order_products__product__store__owner=user
    #         ).distinct()
    #     # Regular users see only their own orders.
    #     return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user

        # If ordering from cart, create an order from the user’s cart.
        if serializer.validated_data.get("from_cart"):
            # cart = get_object_or_404(Cart, user=user)
            cart, created = Cart.objects.get_or_create(user=user)
            cart_items = cart.cart_items.all()
            order = Order.objects.create(user=user)
            for item in cart_items:
                OrderProduct.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                )
            cart.cart_items.all().delete()
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

        # Otherwise, process a single-product order.
        product = get_object_or_404(Product, id=serializer.validated_data["product_id"])
        quantity = serializer.validated_data["quantity"]

        if quantity > product.stock:
            return Response(
                {"detail": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST
            )

        order = Order.objects.create(user=user)

        OrderProduct.objects.create(order=order, product=product, quantity=quantity)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["PATCH"],
        permission_classes=[IsAuthenticated, CanManageOrderStatus],
    )
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")

        if new_status not in Order.StatusChoices.values:
            return Response(
                {"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.role == "store_owner":
            allowed_statuses = [
                Order.StatusChoices.PENDING,
                Order.StatusChoices.CONFIRMED,
                Order.StatusChoices.CANCELLED,
                Order.StatusChoices.SHIPPED,
                Order.StatusChoices.DELIVERED,
            ]
            if new_status not in allowed_statuses:
                return Response(
                    {
                        "detail": "Store owners can only set Pending, Confirmed, or Shipped status"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        order.status = new_status
        order.save()

        return Response(OrderSerializer(order).data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def create_payment_intent(self, request):
        try:
            amount = int(request.data.get("amount", 0))
            if amount <= 0:
                return Response(
                    {"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST
                )
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency="usd",  # Change currency as needed.
            )
            return Response({"clientSecret": intent.client_secret})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            # Amount (in cents) should be passed from the front end
            amount = int(request.data.get("amount", 0))
            if amount <= 0:
                return Response(
                    {"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Create a PaymentIntent on Stripe
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency="usd",  # Change as needed
                # Optionally, you can add metadata or receipt_email here.
            )
            return Response({"clientSecret": intent.client_secret})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ! AI Code

# import os

# import stripe
# from core.pagination import CustomPageNumberPagination
# from django.conf import settings
# from django.contrib.auth import get_user_model
# from django.shortcuts import get_object_or_404
# from rest_framework import status, viewsets
# from rest_framework.decorators import action
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from .models import Cart, CartItem, Order, OrderProduct, Product
# from .permissions import CanManageOrderStatus
# from .serializers import (
#     CartItemSerializer,
#     CartSerializer,
#     OrderCreateSerializer,
#     OrderSerializer,
# )

# User = get_user_model()
# stripe.api_key = settings.STRIPE_SECRET_KEY


# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = CustomPageNumberPagination

#     def get_queryset(self):
#         return Cart.objects.filter(user=self.request.user)

#     def list(self, request, *args, **kwargs):
#         cart, _ = (
#             Cart.objects.select_related("user")
#             .prefetch_related("cart_items__product")
#             .get_or_create(user=request.user)
#         )
#         serializer = CartSerializer(cart)
#         return Response(serializer.data)

#     def create(self, request, *args, **kwargs):
#         cart, _ = Cart.objects.get_or_create(user=request.user)
#         product_id = request.data.get("product")
#         quantity = request.data.get("quantity", 1)

#         if not product_id:
#             return Response(
#                 {"detail": "Product ID is required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         product = get_object_or_404(Product, id=product_id)

#         cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
#         if not created:
#             cart_item.quantity += quantity
#         else:
#             cart_item.quantity = quantity
#         cart_item.save()

#         serializer = CartItemSerializer(cart_item)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

#     def destroy(self, request, *args, **kwargs):
#         cart = get_object_or_404(Cart, user=request.user)
#         cart_item_id = kwargs.get("pk")
#         cart_item = get_object_or_404(CartItem, cart=cart, id=cart_item_id)
#         cart_item.delete()
#         return Response(
#             {"detail": "Product removed from cart."}, status=status.HTTP_204_NO_CONTENT
#         )

#     def update(self, request, *args, **kwargs):
#         cart = get_object_or_404(Cart, user=request.user)
#         cart_item_id = kwargs.get("pk")
#         cart_item = get_object_or_404(CartItem, cart=cart, id=cart_item_id)

#         quantity = request.data.get("quantity")
#         if not quantity:
#             return Response(
#                 {"detail": "Quantity is required."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         if quantity <= 0:
#             cart_item.delete()
#             return Response(
#                 {"detail": "Product removed from cart."},
#                 status=status.HTTP_204_NO_CONTENT,
#             )

#         cart_item.quantity = quantity
#         cart_item.save()

#         serializer = CartItemSerializer(cart_item)
#         return Response(serializer.data)


# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = CustomPageNumberPagination

#     def get_queryset(self):
#         user = self.request.user
#         qs = Order.objects.select_related("user").prefetch_related(
#             "order_products",
#             "order_products__product",
#         )
#         if user.role == "admin":
#             return qs
#         elif user.role == "store_owner":
#             return qs.filter(order_products__product__store__owner=user).distinct()
#         return qs.filter(user=user)

#     def create(self, request, *args, **kwargs):
#         serializer = OrderCreateSerializer(
#             data=request.data, context={"request": request}
#         )
#         serializer.is_valid(raise_exception=True)
#         user = request.user

#         if serializer.validated_data.get("from_cart"):
#             cart, _ = Cart.objects.get_or_create(user=user)
#             cart_items = cart.cart_items.all()
#             order = Order.objects.create(user=user)
#             for item in cart_items:
#                 OrderProduct.objects.create(
#                     order=order,
#                     product=item.product,
#                     quantity=item.quantity,
#                 )
#             cart.cart_items.all().delete()
#             return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

#         product = get_object_or_404(Product, id=serializer.validated_data["product_id"])
#         quantity = serializer.validated_data["quantity"]

#         if quantity > product.stock:
#             return Response(
#                 {"detail": "Insufficient stock."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         order = Order.objects.create(user=user)
#         OrderProduct.objects.create(order=order, product=product, quantity=quantity)
#         return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

#     @action(
#         detail=True,
#         methods=["PATCH"],
#         permission_classes=[IsAuthenticated, CanManageOrderStatus],
#     )
#     def update_status(self, request, pk=None):
#         order = self.get_object()
#         new_status = request.data.get("status")

#         if new_status not in Order.StatusChoices.values:
#             return Response(
#                 {"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST
#             )

#         if request.user.role == "store_owner":
#             allowed_statuses = [
#                 Order.StatusChoices.PENDING,
#                 Order.StatusChoices.CONFIRMED,
#                 Order.StatusChoices.CANCELLED,
#                 Order.StatusChoices.SHIPPED,
#                 Order.StatusChoices.DELIVERED,
#             ]
#             if new_status not in allowed_statuses:
#                 return Response(
#                     {
#                         "detail": "Store owners can only set Pending, Confirmed, or Shipped status"
#                     },
#                     status=status.HTTP_403_FORBIDDEN,
#                 )

#         order.status = new_status
#         order.save()
#         return Response(OrderSerializer(order).data)

#     # ------------------------------------------------------------------ #
#     #  POST /api/orders/checkout/                                          #
#     #  Called by frontend CartPage → returns { "url": stripe_hosted_url } #
#     # ------------------------------------------------------------------ #
#     @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
#     def checkout(self, request):
#         user = request.user

#         # ── 1. Load cart ──────────────────────────────────────────────── #
#         cart, _ = Cart.objects.prefetch_related("cart_items__product").get_or_create(
#             user=user
#         )
#         cart_items = cart.cart_items.select_related("product").all()

#         if not cart_items.exists():
#             return Response(
#                 {"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         # ── 2. Build Stripe line items ────────────────────────────────── #
#         line_items = []
#         for item in cart_items:
#             product = item.product
#             product_data = {"name": product.name}

#             # Attach image only if the product has one
#             if hasattr(product, "image") and product.image:
#                 try:
#                     image_url = request.build_absolute_uri(product.image.url)
#                     product_data["images"] = [image_url]
#                 except Exception:
#                     pass

#             line_items.append(
#                 {
#                     "price_data": {
#                         "currency": "usd",
#                         "unit_amount": int(float(product.price) * 100),  # cents
#                         "product_data": product_data,
#                     },
#                     "quantity": item.quantity,
#                 }
#             )

#         # ── 3. Create a pending Order (so we have an ID for metadata) ─── #
#         order = Order.objects.create(user=user)
#         for item in cart_items:
#             OrderProduct.objects.create(
#                 order=order,
#                 product=item.product,
#                 quantity=item.quantity,
#             )

#         # ── 4. Create Stripe Checkout Session ────────────────────────── #
#         frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
#         try:
#             session = stripe.checkout.Session.create(
#                 payment_method_types=["card"],
#                 line_items=line_items,
#                 mode="payment",
#                 success_url=f"{frontend_url}/success?order_id={order.id}&session_id={{CHECKOUT_SESSION_ID}}",
#                 cancel_url=f"{frontend_url}/cart",
#                 customer_email=user.email,
#                 metadata={
#                     "order_id": order.id,
#                     "user_id": user.id,
#                 },
#             )
#         except stripe.error.StripeError as exc:
#             order.delete()  # rollback orphan order on Stripe failure
#             return Response(
#                 {"detail": exc.user_message or str(exc)},
#                 status=status.HTTP_502_BAD_GATEWAY,
#             )

#         # Save session id on the order for webhook lookup
#         order.stripe_payment_intent_id = session.id
#         order.save(update_fields=["stripe_payment_intent_id"])

#         # Return the Stripe-hosted checkout URL — frontend does window.location.href = url
#         return Response({"url": session.url}, status=status.HTTP_201_CREATED)

#     # ------------------------------------------------------------------ #
#     #  POST /api/orders/webhook/  — Stripe calls this after payment       #
#     #  No JWT auth — verified by Stripe signature instead                 #
#     # ------------------------------------------------------------------ #
#     @action(
#         detail=False,
#         methods=["post"],
#         url_path="webhook",
#         permission_classes=[],
#         authentication_classes=[],
#     )
#     def webhook(self, request):
#         payload = request.body
#         sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

#         try:
#             event = stripe.Webhook.construct_event(
#                 payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#             )
#         except ValueError:
#             return Response(
#                 {"detail": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST
#             )
#         except stripe.error.SignatureVerificationError:
#             return Response(
#                 {"detail": "Invalid signature."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         if event["type"] == "checkout.session.completed":
#             session = event["data"]["object"]
#             order_id = session.get("metadata", {}).get("order_id")
#             user_id = session.get("metadata", {}).get("user_id")
#             if order_id:
#                 Order.objects.filter(id=order_id).update(
#                     status=Order.StatusChoices.CONFIRMED
#                 )
#             # Clear the cart after successful payment
#             if user_id:
#                 Cart.objects.filter(user_id=user_id).update()
#                 CartItem.objects.filter(cart__user_id=user_id).delete()

#         elif event["type"] == "checkout.session.expired":
#             order_id = event["data"]["object"].get("metadata", {}).get("order_id")
#             if order_id:
#                 Order.objects.filter(id=order_id).update(
#                     status=Order.StatusChoices.CANCELLED
#                 )

#         return Response({"status": "ok"})

#     # ── keep your existing create_payment_intent action untouched ──────── #
#     @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
#     def create_payment_intent(self, request):
#         try:
#             amount = int(request.data.get("amount", 0))
#             if amount <= 0:
#                 return Response(
#                     {"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST
#                 )
#             intent = stripe.PaymentIntent.create(amount=amount, currency="usd")
#             return Response({"clientSecret": intent.client_secret})
#         except Exception as e:
#             return Response(
#                 {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


# class CreatePaymentIntentView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, format=None):
#         try:
#             amount = int(request.data.get("amount", 0))
#             if amount <= 0:
#                 return Response(
#                     {"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST
#                 )
#             intent = stripe.PaymentIntent.create(amount=amount, currency="usd")
#             return Response({"clientSecret": intent.client_secret})
#         except Exception as e:
#             return Response(
#                 {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
