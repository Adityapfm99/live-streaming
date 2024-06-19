# streaming/routing.py

from django.urls import path,re_path
from . import consumers
from livestream.views import stream_video

websocket_urlpatterns = [
    # path('ws/stream/<int:stream_id>/', consumers.StreamConsumer.as_asgi()),
    re_path(r'ws/stream/(?P<stream_id>\w+)/$', consumers.StreamConsumer.as_asgi()),
]
