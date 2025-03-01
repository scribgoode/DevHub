from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"^ws/text_chat/(?P<profile_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
]