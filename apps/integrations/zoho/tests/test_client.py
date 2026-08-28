from unittest.mock import patch

import pytest
import requests
from django.core.cache import cache

from apps.integrations.zoho.exceptions import ZohoError
from apps.integrations.zoho.services.zoho_client import (
    ACCESS_TOKEN_CACHE_KEY,
    REQUEST_TIMEOUT_SECONDS,
    ZohoClient,
)
from apps.integrations.zoho.tests.conftest import FakeResponse

POST_TARGET = "apps.integrations.zoho.services.zoho_client.requests.post"


def test_is_configured_is_true_when_every_credential_is_present(zoho_configured):
    assert ZohoClient().is_configured is True


@pytest.mark.parametrize(
    "blank_setting",
    ["ZOHO_CLIENT_ID", "ZOHO_CLIENT_SECRET", "ZOHO_REFRESH_TOKEN", "ZOHO_DC"],
)
def test_is_configured_is_false_when_any_credential_is_blank(
    settings, zoho_configured, blank_setting
):
    setattr(settings, blank_setting, "")
    assert ZohoClient().is_configured is False


def test_urls_are_built_from_the_data_centre(settings, zoho_configured):
    settings.ZOHO_DC = "eu"
    client = ZohoClient()
    assert client.token_url == "https://accounts.zoho.eu/oauth/v2/token"
    assert client.leads_url == "https://www.zohoapis.eu/crm/v3/Leads"


def test_refresh_access_token_returns_and_caches_the_token(zoho_configured, token_response):
    with patch(POST_TARGET, return_value=token_response) as post:
        token = ZohoClient().refresh_access_token()

    assert token == "access-token-1"
    assert cache.get(ACCESS_TOKEN_CACHE_KEY) == "access-token-1"
    assert post.call_args.kwargs["timeout"] == REQUEST_TIMEOUT_SECONDS


def test_cached_token_ttl_is_shorter_than_zohos_expiry(zoho_configured):
    response = FakeResponse(payload={"access_token": "abc", "expires_in": 3600})
    with (
        patch(POST_TARGET, return_value=response),
        patch("apps.integrations.zoho.services.zoho_client.cache.set") as cache_set,
    ):
        ZohoClient().refresh_access_token()

    assert cache_set.call_args.kwargs["timeout"] == 3540


def test_second_call_reuses_the_cached_token(zoho_configured, token_response):
    client = ZohoClient()
    with patch(POST_TARGET, return_value=token_response) as post:
        first = client.get_access_token()
        second = client.get_access_token()

    assert first == second == "access-token-1"
    assert post.call_count == 1


def test_refresh_access_token_raises_when_zoho_returns_no_token(zoho_configured):
    with patch(POST_TARGET, return_value=FakeResponse(payload={"error": "invalid_client"})):
        with pytest.raises(ZohoError, match="no access token"):
            ZohoClient().refresh_access_token()


def test_refresh_access_token_raises_on_http_error(zoho_configured):
    with patch(POST_TARGET, return_value=FakeResponse(status_code=500, text="boom")):
        with pytest.raises(ZohoError, match="token refresh failed"):
            ZohoClient().refresh_access_token()


def test_push_lead_returns_the_zoho_record_id(
    zoho_configured, token_response, lead_created_response
):
    with patch(POST_TARGET, side_effect=[token_response, lead_created_response]) as post:
        record_id = ZohoClient().push_lead({"Last_Name": "Sara"})

    assert record_id == "3477061000000419001"
    leads_call = post.call_args_list[1]
    assert leads_call.args[0] == "https://www.zohoapis.com/crm/v3/Leads"
    assert leads_call.kwargs["json"] == {"data": [{"Last_Name": "Sara"}]}
    assert leads_call.kwargs["headers"]["Authorization"] == "Zoho-oauthtoken access-token-1"
    assert leads_call.kwargs["timeout"] == REQUEST_TIMEOUT_SECONDS


def test_push_lead_raises_on_http_error(zoho_configured, token_response):
    failure = FakeResponse(status_code=500, text="server error")
    with patch(POST_TARGET, side_effect=[token_response, failure]):
        with pytest.raises(ZohoError, match="lead push failed"):
            ZohoClient().push_lead({"Last_Name": "Sara"})


def test_push_lead_raises_when_zoho_rejects_the_record(zoho_configured, token_response):
    rejected = FakeResponse(
        payload={"data": [{"code": "INVALID_DATA", "message": "missing Last_Name"}]}
    )
    with patch(POST_TARGET, side_effect=[token_response, rejected]):
        with pytest.raises(ZohoError, match="INVALID_DATA"):
            ZohoClient().push_lead({})


def test_push_lead_drops_the_cached_token_on_401(zoho_configured, token_response):
    unauthorized = FakeResponse(status_code=401, text="invalid token")
    with patch(POST_TARGET, side_effect=[token_response, unauthorized]):
        with pytest.raises(ZohoError, match="401"):
            ZohoClient().push_lead({"Last_Name": "Sara"})

    assert cache.get(ACCESS_TOKEN_CACHE_KEY) is None


def test_transport_failures_surface_as_zoho_error(zoho_configured):
    with patch(POST_TARGET, side_effect=requests.Timeout("timed out")):
        with pytest.raises(ZohoError, match="failed"):
            ZohoClient().refresh_access_token()


def test_non_json_response_surfaces_as_zoho_error(zoho_configured):
    with patch(POST_TARGET, return_value=FakeResponse(payload=None, text="<html>")):
        with pytest.raises(ZohoError, match="non-JSON"):
            ZohoClient().refresh_access_token()
