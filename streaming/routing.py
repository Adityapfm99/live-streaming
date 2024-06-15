# streaming/routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/stream/<str:stream_id>/', consumers.StreamConsumer.as_asgi()),
]
