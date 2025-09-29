"""
URL patterns for Memberships API endpoints.
Safe URL patterns without conflicts.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    MembershipPlanViewSet,
    MembershipViewSet,
    MembershipBenefitViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'memberships/plans', MembershipPlanViewSet, basename='membershipplan')
router.register(r'memberships', MembershipViewSet, basename='membership')
router.register(r'memberships/benefits', MembershipBenefitViewSet, basename='membershipbenefit')

# API URL patterns
urlpatterns = [
    path('api/', include(router.urls)),
]

# Named URL patterns for easy access
app_name = 'memberships_api'