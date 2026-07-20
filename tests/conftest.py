import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

TEST_API_KEY = "test-api-key-12345"

@pytest.fixture
def client():
    """
    FastAPI test client fixture. Qdrant collection creation
    is mocked on startup. Auth is enabled with a fixed test
    key so protected-route tests exercise real auth behavior
    instead of relying on auth being globally disabled.
    """
    with patch("api.app.create_collection_if_missing"), \
         patch("api.dependencies.AUTH_ENABLED", True), \
         patch("api.dependencies.API_KEY", TEST_API_KEY):
        from api.app import app
        with TestClient(app) as test_client:
            yield test_client

@pytest.fixture
def auth_headers():
    """
    Standard headers for calling protected routes in tests.
    """
    return {"X-API-Key": TEST_API_KEY}