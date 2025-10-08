"""URL configuration for Concierge app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConciergeRequestViewSet

router = DefaultRouter()
router.register(r'concierge/requests', ConciergeRequestViewSet, basename='concierge-request')

urlpatterns = [
    path('api/', include(router.urls)),
]

app_name = 'concierge'

