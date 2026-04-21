import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import mi_app_salud.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_clean.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter(
            mi_app_salud.routing.websocket_urlpatterns
        )
    ),
})