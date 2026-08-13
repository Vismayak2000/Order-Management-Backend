from rest_framework.routers import DefaultRouter

from .views import (
    FoodItemViewSet,
    OrderViewSet,
)


router = DefaultRouter()

router.register(
    'menu',
    FoodItemViewSet,
    basename='menu'
)

router.register(
    'orders',
    OrderViewSet,
    basename='orders'
)

urlpatterns = router.urls