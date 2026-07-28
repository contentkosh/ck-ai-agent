from fastapi import Header
from configuration.config import (API_KEY,AUTH_ENABLED,)
from configuration.context import RequestContext
from common.custom_exceptions import AuthenticationException

def get_request_context() -> RequestContext:
    return RequestContext()

def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """
    Verify the caller supplied a valid API key.

    Disabled entirely when AUTH_ENABLED=False (useful for local
    dev). If AUTH_ENABLED=True but no API_KEY is configured on
    the server, requests are rejected rather than silently
    allowed through, since that almost certainly indicates a
    misconfiguration rather than intent to run unauthenticated.
    """
    if not AUTH_ENABLED:
        return

    if not API_KEY:
        raise AuthenticationException(
            "Server is misconfigured: AUTH_ENABLED is True but no API_KEY is set."
        )

    if not x_api_key or x_api_key != API_KEY:
        raise AuthenticationException("Missing or invalid API key.")