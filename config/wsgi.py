"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Deliberately no setdefault here: unlike manage.py (dev convenience), a
# deployment entrypoint must not silently fall back to development settings.
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    raise RuntimeError(
        "DJANGO_SETTINGS_MODULE must be set explicitly (e.g. "
        "config.settings.production) before running wsgi.py."
    )

application = get_wsgi_application()
