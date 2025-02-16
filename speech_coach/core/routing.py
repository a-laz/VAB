from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/speeches/(?P<speech_id>\d+)/live/$', 
        consumers.LiveTranscriptionConsumer.as_asgi()
    ),
    re_path(
        r'ws/openai/realtime/$',
        consumers.OpenAIRealtimeConsumer.as_asgi()
    ),
    re_path(
        r'ws/interview/(?P<session_id>\d+)/$',
        consumers.InterviewConsumer.as_asgi()
    ),
] 