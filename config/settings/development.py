from config.settings.base import *  # noqa: F401,F403

DEBUG = True

INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405
INTERNAL_IPS = ["127.0.0.1"]

REST_FRAMEWORK = {  # noqa: F405
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}

# Verbose logging is opt-in per package rather than global. Turning the root
# logger up to DEBUG also turns up every third-party library: the autoreloader
# emits a line per watched file (thousands, including the whole virtualenv),
# celery prints the source of every generated task, and redis repeats
# connection notices — which buries our own output entirely.
for _app_logger in ("apps", "common"):
    LOGGING["loggers"][_app_logger] = {  # noqa: F405
        "handlers": ["console"],
        "level": "DEBUG",
        "propagate": False,
    }
