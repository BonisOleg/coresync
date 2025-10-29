"""
WebSocket routing для IoT control real-time communication.
Real-time updates для управління пристроями.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/iot/control/(?P<location>[\w_]+)/$', consumers.IoTControlConsumer.as_asgi()),
    re_path(r'ws/iot/device/(?P<device_id>\d+)/$', consumers.DeviceStatusConsumer.as_asgi()),
    re_path(r'ws/iot/sensors/(?P<device_id>\d+)/$', consumers.SensorDataConsumer.as_asgi()),
]
