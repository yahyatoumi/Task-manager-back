"""
ASGI config for sideproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sideproject.settings')
django_asgi_app = get_asgi_application()
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from django_channels_jwt.middleware import JwtAuthMiddlewareStack

def get_websocket_urlpatterns():
    from taskmanager.consumers import TextRoomConsumer
    return [
        re_path(r'^ws/board/(?P<board_id>\d+)/$', TextRoomConsumer.as_asgi()),
    ]



application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket':JwtAuthMiddlewareStack(
        URLRouter(
            get_websocket_urlpatterns(),
        )
    )
    ,
    # Just HTTP for now. (We can add other protocols later.)
})