import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def _clear_cache():
    # DRF throttles (e.g. inquiry_create) persist counters in the cache
    # backend (Redis in dev). Without this, throttle state leaks between
    # test runs and can fail unrelated tests with 429s.
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def _isolate_media_root(settings, tmp_path):
    # Without this, FileField/ImageField tests (apps.media) write into the
    # real media/ directory on every run instead of a throwaway location.
    settings.MEDIA_ROOT = tmp_path
