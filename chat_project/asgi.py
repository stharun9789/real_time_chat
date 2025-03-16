import os
import django  # Import Django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing  # Ensure this module exists

# Ensure Django settings are set before importing anything
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_project.settings")

# Initialize Django (fixes 'Apps aren't loaded yet' issue)
django.setup()

# Create Django ASGI application early to ensure Apps are loaded
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Handles HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
