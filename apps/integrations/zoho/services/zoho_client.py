import logging

import requests
from django.conf import settings
from django.core.cache import cache

from apps.integrations.zoho.exceptions import ZohoError

logger = logging.getLogger(__name__)

ACCESS_TOKEN_CACHE_KEY = "zoho:access_token"
# Cached slightly shorter than Zoho's stated `expires_in` so a token can't
# lapse between the cache read and Zoho receiving the request.
TOKEN_EXPIRY_MARGIN_SECONDS = 60
DEFAULT_TOKEN_LIFETIME_SECONDS = 3600
REQUEST_TIMEOUT_SECONDS = 10


class ZohoClient:
    """Thin wrapper around the Zoho CRM REST API: OAuth token refresh plus
    lead creation. Every failure surfaces as ZohoError."""

    def __init__(self):
        self.client_id = settings.ZOHO_CLIENT_ID
        self.client_secret = settings.ZOHO_CLIENT_SECRET
        self.refresh_token = settings.ZOHO_REFRESH_TOKEN
        self.dc = settings.ZOHO_DC

    @property
    def is_configured(self) -> bool:
        credentials = (self.client_id, self.client_secret, self.refresh_token, self.dc)
        return all(bool(value) and bool(str(value).strip()) for value in credentials)

    @property
    def token_url(self) -> str:
        return f"https://accounts.zoho.{self.dc}/oauth/v2/token"

    @property
    def leads_url(self) -> str:
        return f"https://www.zohoapis.{self.dc}/crm/v3/Leads"

    def get_access_token(self) -> str:
        token = cache.get(ACCESS_TOKEN_CACHE_KEY)
        if token:
            return token
        return self.refresh_access_token()

    def refresh_access_token(self) -> str:
        response = self._post(
            self.token_url,
            # Sent as a form body rather than a query string so the refresh
            # token never lands in URLs, proxy logs, or error reports.
            data={
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
            },
        )
        if response.status_code >= 400:
            raise ZohoError(
                f"Zoho token refresh failed (HTTP {response.status_code}): {response.text[:500]}"
            )

        payload = self._json(response)
        access_token = payload.get("access_token")
        if not access_token:
            raise ZohoError(f"Zoho token refresh returned no access token: {payload}")

        expires_in = int(payload.get("expires_in", DEFAULT_TOKEN_LIFETIME_SECONDS))
        cache.set(
            ACCESS_TOKEN_CACHE_KEY,
            access_token,
            timeout=max(expires_in - TOKEN_EXPIRY_MARGIN_SECONDS, TOKEN_EXPIRY_MARGIN_SECONDS),
        )
        return access_token

    def push_lead(self, lead_data: dict) -> str:
        response = self._post(
            self.leads_url,
            json={"data": [lead_data]},
            headers={"Authorization": f"Zoho-oauthtoken {self.get_access_token()}"},
        )

        if response.status_code == 401:
            # The cached token was rejected (revoked, or rotated elsewhere):
            # drop it so the next attempt re-authenticates instead of
            # replaying a token Zoho already refuses.
            cache.delete(ACCESS_TOKEN_CACHE_KEY)
            raise ZohoError("Zoho rejected the access token (HTTP 401).")
        if response.status_code >= 400:
            raise ZohoError(
                f"Zoho lead push failed (HTTP {response.status_code}): {response.text[:500]}"
            )

        records = self._json(response).get("data") or []
        if not records:
            raise ZohoError("Zoho lead push returned no record.")

        record = records[0]
        if record.get("code") != "SUCCESS":
            raise ZohoError(
                f"Zoho rejected the lead ({record.get('code')}): {record.get('message')}"
            )

        record_id = (record.get("details") or {}).get("id")
        if not record_id:
            raise ZohoError("Zoho lead push response is missing the record id.")
        return str(record_id)

    @staticmethod
    def _post(url: str, **kwargs):
        try:
            return requests.post(url, timeout=REQUEST_TIMEOUT_SECONDS, **kwargs)
        except requests.RequestException as exc:
            raise ZohoError(f"Zoho request to {url} failed: {exc}") from exc

    @staticmethod
    def _json(response):
        try:
            return response.json()
        except ValueError as exc:
            raise ZohoError(
                f"Zoho returned a non-JSON response (HTTP {response.status_code})."
            ) from exc
