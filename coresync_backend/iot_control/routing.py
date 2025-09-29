"""
WebSocket routing for IoT control real-time communication.
"""
from django.urls import path

# TODO: Add WebSocket consumers for real-time IoT control
websocket_urlpatterns = [
    # path('ws/iot/<str:location>/', consumers.IoTControlConsumer.as_asgi()),
    # path('ws/sensors/<str:device_id>/', consumers.SensorDataConsumer.as_asgi()),
]
