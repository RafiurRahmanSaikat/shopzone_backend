from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()


router.register(r"products", views.ProductViewSet, basename="product")
router.register(r"categories", views.CategoryViewSet, basename="category")
router.register(r"brands", views.BrandViewSet, basename="brand")

# Include router URLs
urlpatterns = router.urls
