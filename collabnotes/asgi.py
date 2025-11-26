import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "collabnotes.settings")

# Instantiate the default ASGI application provided by Django
django_asgi_app = get_asgi_application()

import note.routing

# Define the main ASGI application
application = ProtocolTypeRouter(
    {
        # Route traditional HTTP requests to Django's ASGI application
        "http": django_asgi_app,
        # Route WebSocket connections using Django Channels, including authentication middleware
        "websocket": AuthMiddlewareStack(
            URLRouter(note.routing.websocket_urlpatterns)  # Use URLRouter for websocket URLs defined in 'note.routing'
        ),
    }
)