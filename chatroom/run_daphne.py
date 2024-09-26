import os
import sys
from django.core.management.base import BaseCommand
from channels.management.commands
from chatroom_project import routing
class Command(BaseCommand):
    help = 'Run the Daphne ASGI server'
    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            default=8000,
            type=int,
            help='Port to run the server on',
        )
        parser.add_argument(
            '--address',
            default='127.0.0.1',
            help='Address to bind the server to',
        )
    def handle(self, *args, **options):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatroom_project.settings')
        address = options['address']
        port = options['port']
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from channels.asgi import get_asgi_application
        from channels.routing import ProtocolTypeRouter, URLRouter
        from channels.auth import AuthMiddlewareStack
        application = ProtocolTypeRouter({
            "http": get_asgi_application(),
            "websocket": AuthMiddlewareStack(
                URLRouter(
                    routing.websocket_urlpatterns
                )
            ),
        })
        from daphne.server import Server
        server = Server(application=application, interfaces=[address], ports=[port])
        server.run()