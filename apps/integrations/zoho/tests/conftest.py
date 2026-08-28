import pytest


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("No JSON body.")
        return self._payload


@pytest.fixture
def zoho_configured(settings):
    settings.ZOHO_CLIENT_ID = "test-client-id"
    settings.ZOHO_CLIENT_SECRET = "test-client-secret"
    settings.ZOHO_REFRESH_TOKEN = "test-refresh-token"
    settings.ZOHO_DC = "com"


@pytest.fixture
def zoho_unconfigured(settings):
    settings.ZOHO_CLIENT_ID = ""
    settings.ZOHO_CLIENT_SECRET = ""
    settings.ZOHO_REFRESH_TOKEN = ""
    settings.ZOHO_DC = "com"


@pytest.fixture
def make_response():
    return FakeResponse


@pytest.fixture
def token_response():
    return FakeResponse(payload={"access_token": "access-token-1", "expires_in": 3600})


@pytest.fixture
def lead_created_response():
    return FakeResponse(
        payload={
            "data": [
                {
                    "code": "SUCCESS",
                    "status": "success",
                    "message": "record added",
                    "details": {"id": "3477061000000419001"},
                }
            ]
        }
    )
