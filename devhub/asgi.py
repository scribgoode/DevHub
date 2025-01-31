import os
import django
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# Ensure correct settings module is set once
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devhub.settings")  # Update if rtc_demo is correct
django.setup()

# Initialize Django ASGI application first
django_asgi_app = get_asgi_application()

# Import WebSocket routes after Django setup
from text_chat.routing import websocket_urlpatterns as text_chat_websocket_urlpatterns
from video_chat.routing import websocket_urlpatterns as video_chat_websocket_urlpatterns

# Combine WebSocket routes
websocket_urlpatterns = text_chat_websocket_urlpatterns + video_chat_websocket_urlpatterns

# Define ASGI application
application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
