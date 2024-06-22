
import os

from django.core.asgi import get_asgi_application
from django.urls import path, re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'livestream.settings')

application = get_asgi_application()

from streaming import consumers

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'livestream.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
         URLRouter([
            # path('ws/stream/<int:stream_id>/', consumers.StreamConsumer.as_asgi()),
            re_path(r'ws/stream/(?P<stream_id>\w+)/$', consumers.StreamConsumer.as_asgi()),
        ])
    ),
})