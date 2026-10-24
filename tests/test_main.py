import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    client.close()

    app.dependency_overrides.clear()


def test_root_endpoint(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "application": "TaskFlow",
        "message": "TaskFlow API is running",
    }


def test_health_endpoint(client: TestClient):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
    }


def test_info_endpoint(client: TestClient):
    response = client.get("/info")

    assert response.status_code == 200
    assert response.json() == {
        "name": "TaskFlow API",
        "version": "0.1.0",
        "environment": "development",
    }


def test_unknown_endpoint_returns_not_found(client: TestClient):
    response = client.get("/this-endpoint-does-not-exist")

    assert response.status_code == 404


def test_create_task(client: TestClient):
    response = client.post(
        "/tasks",
        json={
            "title": "Learn databases",
            "description": "Add persistent storage to TaskFlow",
        },
    )

    assert response.status_code == 201

    task = response.json()
    assert task["id"] is not None
    assert task["title"] == "Learn databases"
    assert task["completed"] is False
    assert task["created_at"] is not None


def test_list_tasks(client: TestClient):
    client.post("/tasks", json={"title": "First task"})
    client.post("/tasks", json={"title": "Second task"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_and_delete_task(client: TestClient):
    create_response = client.post(
        "/tasks",
        json={"title": "Task to update"},
    )
    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tasks/{task_id}",
        json={"completed": True},
    )

    assert update_response.status_code == 200
    assert update_response.json()["completed"] is True

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_empty_title_is_rejected(client: TestClient):
    response = client.post(
        "/tasks",
        json={"title": ""},
    )

    assert response.status_code == 422