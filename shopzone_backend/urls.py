from account.views import LogoutView
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from order.views import CartViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r"api/cart", CartViewSet, basename="cart")

urlpatterns = [
    # Admin panel
    path("admin/", admin.site.urls),
    # App-specific URLs under `/api/`
    path("api/", include("product.urls")),
    path("api/accounts/", include("account.urls")),
    path("api/stores/", include("store.urls")),
    path("api/orders/", include("order.urls")),
    # Performance monitoring (silk)
    path("silk/", include("silk.urls", namespace="silk")),
    # API schema and documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    # JWT authentication
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

urlpatterns += router.urls
