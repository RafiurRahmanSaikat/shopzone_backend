from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StoreCategoryViewSet, StoreViewSet

router = DefaultRouter()
router.register(r"", StoreViewSet, basename="store")


urlpatterns = [
    path(
        "storeCategory",
        StoreCategoryViewSet.as_view({"get": "list", "post": "create"}),
        name="storeCategory-list",
    ),
    path(
        "storeCategory/<int:pk>/",
        StoreCategoryViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="storeCategory-detail",
    ),
    path("", include(router.urls)),
]
