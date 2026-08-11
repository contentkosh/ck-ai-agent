import pytest
from types import SimpleNamespace
from unittest.mock import patch
from fastapi.testclient import TestClient
from api.dependencies import verify_bearer_token
from configuration.constants import ADMIN_ROLE

@pytest.fixture
def client():
    """
    FastAPI test client for functional API tests.

    Authentication is overridden with a test ADMIN user so
    functional tests can reach the actual route/service logic.
    """
    with patch("api.app.create_collection_if_missing"):
        from api.app import app

        test_user = SimpleNamespace(
            username="test_user",
            role=ADMIN_ROLE,
            is_active=True,
            expires_at=None,
        )

        app.dependency_overrides[verify_bearer_token] = (
            lambda: test_user
        )

        with TestClient(app) as test_client:
            yield test_client

        app.dependency_overrides.clear()


@pytest.fixture
def auth_client():
    """
    FastAPI test client with real authentication enabled.

    Used specifically for authentication tests such as
    missing or invalid Bearer tokens.
    """
    with patch("api.app.create_collection_if_missing"):
        from api.app import app

        with TestClient(app) as test_client:
            yield test_client