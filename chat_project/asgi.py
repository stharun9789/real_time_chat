import os
import django  # Ensure Django is imported
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing  # Ensure this module exists and has `websocket_urlpatterns`

# **Set the environment variable for Django settings**
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_project.settings")

# **Debugging Output**
try:
    print("Starting Django setup...")
    django.setup()  # Ensures Django settings are initialized
    print("Django setup completed successfully!")
except Exception as e:
    print("Django setup failed:", e)
    raise

# **Create the Django ASGI application**
django_asgi_app = get_asgi_application()

# **Define the ASGI application with WebSockets support**
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Handles HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
