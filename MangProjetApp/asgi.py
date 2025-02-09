import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MangProjetApp.settings')
django.setup()

import student_app.routing 
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            student_app.routing.websocket_urlpatterns
        )
    ),
})