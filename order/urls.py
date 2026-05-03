# order/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CreatePaymentIntentView, OrderViewSet

router = DefaultRouter()
router.register(r"", OrderViewSet, basename="order")

urlpatterns = [
    path(
        "create-payment-intent/",
        CreatePaymentIntentView.as_view(),
        name="create-payment-intent",
    ),
    path("", include(router.urls)),
]
