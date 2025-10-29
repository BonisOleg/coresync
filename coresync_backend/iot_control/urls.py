"""
IoT Control URLs для CoreSync API.
REST API endpoints для управління IoT пристроями.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'iot_control'

# DRF Router для ViewSets
router = DefaultRouter()
router.register(r'devices', views.IoTDeviceViewSet, basename='device')
router.register(r'scenes', views.SceneViewSet, basename='scene')
router.register(r'logs', views.ControlLogViewSet, basename='control-log')
router.register(r'sensors', views.SensorReadingViewSet, basename='sensor')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
]
