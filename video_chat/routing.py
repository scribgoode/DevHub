from django.urls import re_path

#from . import consumers
from text_chat import consumers as text_chat_consumers

websocket_urlpatterns = [
    #re_path(r'ws/(?P<rtc_name>\w+)/$', consumers.RtcConsumer.as_asgi()), #this caputures the rtc_name from the html page at ws-connect=
    #re_path(r"^ws/<endpoint_name>/", text_chat_consumers.ChatConsumer.as_asgi()),
]