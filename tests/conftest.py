import pytest
from starlette.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client():
    """Provides a TestClient instance for testing FastAPI endpoints."""
    with TestClient(app) as test_client:
        yield test_client
