from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/speeches/(?P<speech_id>\d+)/live/$', 
        consumers.LiveTranscriptionConsumer.as_asgi()
    ),
] 