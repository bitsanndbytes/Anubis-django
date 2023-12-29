from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import AnubisConsumer

websocket_urlpatterns = [
    re_path(r"ws/stream/1", AnubisConsumer.as_asgi()),
    re_path(r"ws/stream/2", AnubisConsumer.as_asgi()),
    
]

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
