from django.urls import re_path
from .consumers import EstadoConsumer

websocket_urlpatterns = [
    re_path(r"ws/estados/$", EstadoConsumer.as_asgi()),
]