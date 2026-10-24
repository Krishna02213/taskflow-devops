from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "application": "TaskFlow",
        "message": "TaskFlow API is running",
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
    }


def test_info_endpoint():
    response = client.get("/info")

    assert response.status_code == 200
    assert response.json() == {
        "name": "TaskFlow API",
        "version": "0.1.0",
        "environment": "development",
    }


def test_unknown_endpoint_returns_not_found():
    response = client.get("/this-endpoint-does-not-exist")

    assert response.status_code == 404