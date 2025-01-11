"""
ASGI config for devhub project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devhub.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

import django
django.setup()


from channels.auth import AuthMiddlewareStack
import text_chat.routing

django_asgi_app = get_asgi_application()
from text_chat.routing import websocket_urlpatterns
from channels.security.websocket import AllowedHostsOriginValidator


# application = ProtocolTypeRouter(
#     {
#         "http": get_asgi_application(),
#         # Just HTTP for now. (We can add other protocols later.)
#         'websocket': AuthMiddlewareStack(
#             URLRouter(
#                 text_chat.routing.websocket_urlpatterns
#             )
#         ),
#     }
# )

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
