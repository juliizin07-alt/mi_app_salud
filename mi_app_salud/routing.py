from django.urls import re_path

from .consumers import (
    EstadoConsumer,
    PresenciaConsumer,
)

from .monitoreo_consumer import MonitoreoConsumer


websocket_urlpatterns = [

    re_path(
        r"ws/estados/$",
        EstadoConsumer.as_asgi()
    ),

    re_path(
        r"ws/presencia/$",
        PresenciaConsumer.as_asgi()
    ),

    re_path(
        r"ws/monitoreo/$",
        MonitoreoConsumer.as_asgi()
    ),

]
