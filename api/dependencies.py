from fastapi import Depends, Header
from sqlalchemy.orm import Session
from configuration.config import (API_KEY,AUTH_ENABLED,)
from configuration.context import RequestContext
from common.custom_exceptions import AuthenticationException
from configuration.constants import (
    AUTHORIZATION_HEADER_PREFIX,
    AUTHORIZATION_HEADER_SEPARATOR,
)
from configuration.error_constants import (
    AUTHORIZATION_HEADER_REQUIRED_MESSAGE,
    INVALID_AUTHORIZATION_FORMAT_MESSAGE,
    AUTHENTICATION_TOKEN_REQUIRED_MESSAGE,
    INVALID_AUTHENTICATION_TOKEN_MESSAGE,
)
from database.postgres_dependency import get_db
from services.api_user_service import validate_api_user_token
from exceptions.authorization_exception import AuthorizationException
from configuration.constants import ROLE_PERMISSIONS


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
    print("AUTH_ENABLED =", AUTH_ENABLED)
    print("API_KEY =", API_KEY)
    print("RECEIVED_API_KEY =", x_api_key)
    
    if not AUTH_ENABLED:
        return

    if not API_KEY:
        raise AuthenticationException(
            "Server is misconfigured: AUTH_ENABLED is True but no API_KEY is set."
        )

    if not x_api_key or x_api_key != API_KEY:
        raise AuthenticationException("Missing or invalid API key.")


def verify_bearer_token(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """
    Validate the Bearer token supplied by the API client.
    """

    if not authorization:
        raise AuthenticationException(AUTHORIZATION_HEADER_REQUIRED_MESSAGE)
    authorization_parts = authorization.split(
        AUTHORIZATION_HEADER_SEPARATOR,
        maxsplit=1,
    )

    if (
        len(authorization_parts) != 2
        or authorization_parts[0] != AUTHORIZATION_HEADER_PREFIX
    ):
        raise AuthenticationException(INVALID_AUTHORIZATION_FORMAT_MESSAGE)
    token = authorization_parts[1].strip()

    if not token:
        raise AuthenticationException(AUTHENTICATION_TOKEN_REQUIRED_MESSAGE)
    api_user = validate_api_user_token(
        db=db,
        token=token,
    )

    if api_user is None:
        raise AuthenticationException(INVALID_AUTHENTICATION_TOKEN_MESSAGE)
    return api_user


def require_permission(permission: str):
    """
    Verify that the authenticated API user has the required permission.
    """

    def authorization_dependency(
        api_user=Depends(verify_bearer_token),
    ):
        user_permissions = ROLE_PERMISSIONS.get(
            api_user.role,
            set(),
        )

        if permission not in user_permissions:
            raise AuthorizationException()
        return api_user
    return authorization_dependency