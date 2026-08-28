import logging

from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def _error_code_from_exc(exc):
    return exc.__class__.__name__.replace("Error", "").replace("Exception", "") or "Error"


def custom_exception_handler(exc, context):
    """Normalizes every DRF-raised error into
    {"success": false, "error": {"code", "message", "details"}} so both
    frontends can rely on one shape regardless of endpoint."""
    response = drf_exception_handler(exc, context)

    if response is None:
        logger.exception("Unhandled exception in %s", context.get("view"))
        return None

    detail = response.data

    if isinstance(detail, dict) and "detail" in detail and len(detail) == 1:
        message = str(detail["detail"])
        details = None
    elif isinstance(detail, (list, dict)):
        message = "Validation failed."
        details = detail
    else:
        message = str(detail)
        details = None

    response.data = {
        "success": False,
        "error": {
            "code": _error_code_from_exc(exc),
            "message": message,
            "details": details,
        },
    }
    return response
