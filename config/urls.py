from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("config.api")),
]

if settings.DEBUG:
    # django.conf.urls.static.static() would do, except that every response
    # then carries the global X-Frame-Options: DENY — and the website shows a
    # certificate PDF in a frame, from a different origin than the API. The
    # header is right for the API and the admin; for a public document it just
    # stops the viewer working.
    #
    # In production nginx serves /media/ and must be configured not to send
    # X-Frame-Options: DENY for that location, or the certificate viewer goes
    # blank there too.
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            xframe_options_exempt(serve),
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
    try:
        import debug_toolbar

        urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
    except ImportError:
        pass
