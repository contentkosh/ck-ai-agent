import pytest
from fastapi.testclient import TestClient

from api.app import app

@pytest.fixture
def client():
    """
    FastAPI test client fixture.
    """
    return TestClient(app)