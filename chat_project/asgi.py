import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns  # Import WebSocket routes
import chat.routing  # Make sure 'chat.routing' exists and is correct

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_project.settings")

# Create Django ASGI application early to ensure Apps are loaded
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Handles HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
