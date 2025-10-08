"""URL configuration for Shop app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, PickupOrderViewSet

router = DefaultRouter()
router.register(r'shop/products', ProductViewSet, basename='product')
router.register(r'shop/orders', PickupOrderViewSet, basename='pickup-order')

urlpatterns = [
    path('api/', include(router.urls)),
]

app_name = 'shop'

