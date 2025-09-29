"""
URL patterns for Users API endpoints.
Safe URL patterns without conflicts.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserProfileViewSet,
    UserPreferenceViewSet,
    UserRegistrationViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users/profile', UserProfileViewSet, basename='userprofile')
router.register(r'users/preferences', UserPreferenceViewSet, basename='userpreference')
router.register(r'auth', UserRegistrationViewSet, basename='auth')

# API URL patterns
urlpatterns = [
    path('api/', include(router.urls)),
]

# Named URL patterns for easy access
app_name = 'users_api'