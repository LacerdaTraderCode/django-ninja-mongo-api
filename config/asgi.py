"""ASGI entrypoint used by Django and, in production, by an ASGI server such as uvicorn."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
