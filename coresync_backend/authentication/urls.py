"""
Authentication URLs для CoreSync API.
"""
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from users import face_auth_views

app_name = 'authentication'

urlpatterns = [
    # JWT Token endpoints
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Face Recognition Authentication
    path('face/login/', face_auth_views.face_login, name='face_login'),
    path('face/verify/', face_auth_views.face_verify_check, name='face_verify'),
]
