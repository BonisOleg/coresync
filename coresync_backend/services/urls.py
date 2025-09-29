"""
URL patterns for Services API endpoints.
Safe URL patterns without conflicts.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ServiceViewSet,
    ServiceCategoryViewSet,
    ServiceAddonViewSet,
    ServiceHistoryViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'services/categories', ServiceCategoryViewSet, basename='servicecategory')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'services/addons', ServiceAddonViewSet, basename='serviceaddon')
router.register(r'services/history', ServiceHistoryViewSet, basename='servicehistory')

# API URL patterns
urlpatterns = [
    path('api/', include(router.urls)),
]

# Named URL patterns for easy access
app_name = 'services_api'