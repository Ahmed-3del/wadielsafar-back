from rest_framework.response import Response


def api_response(data=None, status=200, **kwargs):
    """Wrap successful payloads consistently. Paginated list responses keep DRF's
    own {count, next, previous, results} shape untouched — this helper is for
    non-paginated single-object / action endpoints."""
    return Response(data, status=status, **kwargs)
