from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    #re_path(r'ws/socket-server/', consumers.ChatConsumer.as_asgi()),
    #re_path('ws/text_chat/adamscribner1@gmail.com/', consumers.ChatConsumer.as_asgi()),
    re_path(r"^ws/text_chat/(?P<profile_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
]