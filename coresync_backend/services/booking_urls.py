"""
URL patterns for booking API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .booking_views import BookingViewSet, RoomViewSet

# Create router for booking API
router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'rooms', RoomViewSet, basename='room')

urlpatterns = [
    path('api/', include(router.urls)),
]
