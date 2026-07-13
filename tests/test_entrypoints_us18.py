import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.adapters.unit_of_work import FakeUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.main import app as real_app
from app.domain.models import Project

client = TestClient(real_app)


@pytest.fixture
def fake_uow():
    uow = FakeUnitOfWork()
    real_app.dependency_overrides[get_unit_of_work] = lambda: uow
    yield uow
    real_app.dependency_overrides.pop(get_unit_of_work, None)


def _crear_proyecto(uow, project_id="P001"):
    """Helper: inserta un proyecto directamente en el repo fake."""
    uow.projects.add(
        Project(
            project_id=project_id,
            client_id="C001",
            quote_id="Q001",
            project_name="Techo Bodega Norte",
            project_location="Zona 12",
            project_start_date=date(2026, 2, 1),
            project_total_cost=15000.0,
            project_status="In Progress",
        )
    )


def _valid_worker_payload(**overrides):
    payload = dict(
        worker_id="W001",
        worker_name="Juan Pérez",
        worker_role="Soldador",
        worker_base_rate=150.0,
    )
    payload.update(overrides)
    return payload


def test_create_worker_returns_201_and_persists_it(fake_uow):
    response = client.post("/api/workers", json=_valid_worker_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["worker_id"] == "W001"
    assert fake_uow.workers.get("W001") is not None


def test_create_worker_rejects_negative_base_rate_with_422(fake_uow):
    response = client.post("/api/workers", json=_valid_worker_payload(worker_base_rate=-10.0))

    assert response.status_code == 422


def test_get_worker_returns_existing_worker(fake_uow):
    client.post("/api/workers", json=_valid_worker_payload())

    response = client.get("/api/workers/W001")

    assert response.status_code == 200
    assert response.json()["worker_name"] == "Juan Pérez"


def test_get_worker_returns_404_when_missing(fake_uow):
    response = client.get("/api/workers/W999")

    assert response.status_code == 404


def test_list_workers_returns_all_created(fake_uow):
    client.post("/api/workers", json=_valid_worker_payload())
    client.post("/api/workers", json=_valid_worker_payload(worker_id="W002", worker_name="María"))

    response = client.get("/api/workers")

    assert response.status_code == 200
    ids = {w["worker_id"] for w in response.json()}
    assert ids == {"W001", "W002"}


def test_assign_worker_to_project_returns_201(fake_uow):
    client.post("/api/workers", json=_valid_worker_payload())
    _crear_proyecto(fake_uow)

    response = client.post(
        "/api/workers/W001/assignments",
        json={"assignment_id": "A001", "project_id": "P001", "assignment_date": "2026-02-05"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["worker_id"] == "W001"
    assert body["project_id"] == "P001"


def test_assign_worker_to_project_returns_404_when_worker_missing(fake_uow):
    _crear_proyecto(fake_uow)

    response = client.post(
        "/api/workers/W999/assignments",
        json={"assignment_id": "A001", "project_id": "P001", "assignment_date": "2026-02-05"},
    )

    assert response.status_code == 404


def test_assign_worker_to_project_returns_404_when_project_missing(fake_uow):
    client.post("/api/workers", json=_valid_worker_payload())

    response = client.post(
        "/api/workers/W001/assignments",
        json={"assignment_id": "A001", "project_id": "P999", "assignment_date": "2026-02-05"},
    )

    assert response.status_code == 404


def test_list_assignments_by_worker_returns_created_assignment(fake_uow):
    client.post("/api/workers", json=_valid_worker_payload())
    _crear_proyecto(fake_uow)
    client.post(
        "/api/workers/W001/assignments",
        json={"assignment_id": "A001", "project_id": "P001", "assignment_date": "2026-02-05"},
    )

    response = client.get("/api/workers/W001/assignments")

    assert response.status_code == 200
    assignments = response.json()
    assert len(assignments) == 1
    assert assignments[0]["project_id"] == "P001"


def test_list_assignments_by_worker_returns_empty_when_none(fake_uow):
    client.post("/api/workers", json=_valid_worker_payload())

    response = client.get("/api/workers/W001/assignments")

    assert response.status_code == 200
    assert response.json() == []


def test_list_assignments_by_worker_returns_404_when_worker_missing(fake_uow):
    response = client.get("/api/workers/W999/assignments")

    assert response.status_code == 404