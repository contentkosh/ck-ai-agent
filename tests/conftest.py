import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

TEST_API_KEY = "test-api-key-12345"


@pytest.fixture
def client():
    """
    FastAPI test client fixture.

    Authentication is explicitly enabled for tests so protected
    endpoints exercise the real authentication flow.
    """
    from api.app import app

    with patch(
        "api.dependencies.AUTH_ENABLED",
        True,
    ), patch(
        "api.dependencies.API_KEY",
        TEST_API_KEY,
    ):
        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def auth_headers():
    """
    Standard headers for protected API routes.
    """
    return {
        "X-API-Key": TEST_API_KEY,
    }