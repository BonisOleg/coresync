"""
Authentication URLs for the CoreSync API.
"""
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name = 'authentication'

urlpatterns = [
    # JWT Token endpoints
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # TODO: Add custom authentication views
    # path('register/', views.RegisterView.as_view(), name='register'),
    # path('logout/', views.LogoutView.as_view(), name='logout'),
    # path('password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    # path('biometric/register/', views.BiometricRegisterView.as_view(), name='biometric_register'),
]
