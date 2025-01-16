from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/(?P<rtc_name>\w+)/$', consumers.RtcConsumer.as_asgi()), #this caputures the rtc_name from the url, if i want it to change i need to change this or the url
]
