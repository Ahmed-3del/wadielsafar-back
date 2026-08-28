"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Deliberately no setdefault here: unlike manage.py (dev convenience), a
# deployment entrypoint must not silently fall back to development settings.
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    raise RuntimeError(
        "DJANGO_SETTINGS_MODULE must be set explicitly (e.g. "
        "config.settings.production) before running asgi.py."
    )

application = get_asgi_application()
