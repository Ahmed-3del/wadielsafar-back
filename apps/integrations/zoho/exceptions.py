class ZohoError(Exception):
    """Raised for any Zoho CRM failure — transport, auth, or a rejected
    record — so callers never have to catch `requests` exceptions."""
