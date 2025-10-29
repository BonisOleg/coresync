"""
ASGI config для CoreSync project.
WebSocket routing для Django Channels.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

# WebSocket routing (activate після channels install)
try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from django.urls import re_path
    from ai_agent.consumers import ChatConsumer
    from iot_control import consumers as iot_consumers
    
    websocket_urlpatterns = [
        # AI Chat WebSocket
        re_path(r'ws/ai-chat/(?P<session_id>[^/]+)/$', ChatConsumer.as_asgi()),
        
        # IoT Control WebSockets
        re_path(r'ws/iot/control/(?P<location>[\w_]+)/$', iot_consumers.IoTControlConsumer.as_asgi()),
        re_path(r'ws/iot/device/(?P<device_id>\d+)/$', iot_consumers.DeviceStatusConsumer.as_asgi()),
        re_path(r'ws/iot/sensors/(?P<device_id>\d+)/$', iot_consumers.SensorDataConsumer.as_asgi()),
    ]
    
    application = ProtocolTypeRouter({
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    })

except ImportError:
    # Channels not installed - HTTP only
    application = django_asgi_app
