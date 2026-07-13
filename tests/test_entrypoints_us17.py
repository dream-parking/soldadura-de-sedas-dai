import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.adapters.unit_of_work import FakeUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.main import app as real_app
from app.domain.models import Client, Quote

client = TestClient(real_app)


@pytest.fixture
def fake_uow():
    uow = FakeUnitOfWork()
    real_app.dependency_overrides[get_unit_of_work] = lambda: uow
    yield uow
    real_app.dependency_overrides.pop(get_unit_of_work, None)


def _crear_cliente(uow, client_id="C001"):
    uow.clients.add(
        Client(
            client_id=client_id,
            client_company_name="Constructora Acme",
            client_phone="7777-7777",
            registration_date=date(2026, 1, 1),
        )
    )


def _crear_cotizacion(uow, quote_id="Q001", client_id="C001", status="Aprobado"):
    """Helper: inserta una cotización directamente en el repo fake, con el
    estado que necesite el test (evita depender del flujo completo de aprobación)."""
    uow.quotes.add(
        Quote(
            quote_id=quote_id,
            client_id=client_id,
            quote_issue_date=date(2026, 1, 5),
            quote_job_description="Techo de bodega",
            quote_estimated_amount=15000.0,
            quote_status=status,
        )
    )


def _valid_payload(**overrides):
    payload = dict(
        project_id="P001",
        quote_id="Q001",
        project_name="Techo Bodega Norte",
        project_location="Zona 12",
        project_start_date="2026-02-01",
    )
    payload.update(overrides)
    return payload


def test_create_project_from_approved_quote_returns_201(fake_uow):
    _crear_cliente(fake_uow)
    _crear_cotizacion(fake_uow, status="Aprobado")

    response = client.post("/api/projects", json=_valid_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == "P001"
    assert body["client_id"] == "C001"
    assert body["project_total_cost"] == 15000.0
    assert body["project_status"] == "In Progress"


def test_create_project_from_pending_quote_returns_409(fake_uow):
    _crear_cliente(fake_uow)
    _crear_cotizacion(fake_uow, status="Pendiente")

    response = client.post("/api/projects", json=_valid_payload())

    assert response.status_code == 409


def test_create_project_from_rejected_quote_returns_409(fake_uow):
    _crear_cliente(fake_uow)
    _crear_cotizacion(fake_uow, status="Rechazado")

    response = client.post("/api/projects", json=_valid_payload())

    assert response.status_code == 409


def test_create_project_returns_404_when_quote_missing(fake_uow):
    response = client.post("/api/projects", json=_valid_payload())

    assert response.status_code == 404


def test_get_project_returns_existing_project(fake_uow):
    _crear_cliente(fake_uow)
    _crear_cotizacion(fake_uow, status="Aprobado")
    client.post("/api/projects", json=_valid_payload())

    response = client.get("/api/projects/P001")

    assert response.status_code == 200
    assert response.json()["project_name"] == "Techo Bodega Norte"


def test_get_project_returns_404_when_missing(fake_uow):
    response = client.get("/api/projects/P999")

    assert response.status_code == 404


def test_list_projects_by_client_returns_only_that_clients_projects(fake_uow):
    _crear_cliente(fake_uow, "C001")
    _crear_cliente(fake_uow, "C002")
    _crear_cotizacion(fake_uow, "Q001", "C001", "Aprobado")
    _crear_cotizacion(fake_uow, "Q002", "C002", "Aprobado")
    client.post("/api/projects", json=_valid_payload(project_id="P001", quote_id="Q001"))
    client.post("/api/projects", json=_valid_payload(project_id="P002", quote_id="Q002"))

    response = client.get("/api/projects/by-client/C001")

    assert response.status_code == 200
    project_ids = [p["project_id"] for p in response.json()]
    assert project_ids == ["P001"]


def test_update_project_status_changes_status(fake_uow):
    _crear_cliente(fake_uow)
    _crear_cotizacion(fake_uow, status="Aprobado")
    client.post("/api/projects", json=_valid_payload())

    response = client.patch("/api/projects/P001/status", json={"project_status": "Completed"})

    assert response.status_code == 200
    assert response.json()["project_status"] == "Completed"


def test_update_project_status_rejects_invalid_status_with_422(fake_uow):
    _crear_cliente(fake_uow)
    _crear_cotizacion(fake_uow, status="Aprobado")
    client.post("/api/projects", json=_valid_payload())

    response = client.patch("/api/projects/P001/status", json={"project_status": "Cancelado"})

    assert response.status_code == 422


def test_list_assignments_by_project_returns_empty_when_none(fake_uow):
    _crear_cliente(fake_uow)
    _crear_cotizacion(fake_uow, status="Aprobado")
    client.post("/api/projects", json=_valid_payload())

    response = client.get("/api/projects/P001/assignments")

    assert response.status_code == 200
    assert response.json() == []