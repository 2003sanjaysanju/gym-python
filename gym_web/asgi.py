"""
ASGI config for gym_web project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym_web.settings')

application = get_asgi_application()

