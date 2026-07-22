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


def _valid_account_statement_payload(**overrides):
    payload = dict(
        id="AS001",
        project_id="P001",
        date="2026-02-15",
        initial_budget=15000.0,
        amount_paid=5000.0,
    )
    payload.update(overrides)
    return payload


def _valid_biweekly_request_payload(**overrides):
    payload = dict(
        id="BR001",
        project_id="P001",
        date="2026-02-15",
        status="Pendiente",
        amount=3000.0,
        notes="Pago de quincena para mano de obra",
    )
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# Estados de Cuenta (AccountStatement)
# ---------------------------------------------------------------------------

def test_create_account_statement_returns_201_and_computes_remaining_amount(fake_uow):
    _crear_proyecto(fake_uow)

    response = client.post(
        "/api/account-statements", json=_valid_account_statement_payload()
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == "AS001"
    assert body["project_id"] == "P001"
    assert body["remaining_amount"] == 10000.0


def test_create_account_statement_returns_404_when_project_missing(fake_uow):
    response = client.post(
        "/api/account-statements", json=_valid_account_statement_payload()
    )

    assert response.status_code == 404


def test_create_account_statement_rejects_negative_amount_paid_with_422(fake_uow):
    _crear_proyecto(fake_uow)

    response = client.post(
        "/api/account-statements",
        json=_valid_account_statement_payload(amount_paid=-100.0),
    )

    assert response.status_code == 422


def test_get_account_statement_returns_existing_statement(fake_uow):
    _crear_proyecto(fake_uow)
    client.post("/api/account-statements", json=_valid_account_statement_payload())

    response = client.get("/api/account-statements/AS001")

    assert response.status_code == 200
    assert response.json()["initial_budget"] == 15000.0


def test_get_account_statement_returns_404_when_missing(fake_uow):
    response = client.get("/api/account-statements/AS999")

    assert response.status_code == 404


def test_list_account_statements_by_project_returns_created_ones(fake_uow):
    _crear_proyecto(fake_uow)
    client.post("/api/account-statements", json=_valid_account_statement_payload())
    client.post(
        "/api/account-statements",
        json=_valid_account_statement_payload(id="AS002", date="2026-03-01"),
    )

    response = client.get("/api/account-statements/by-project/P001")

    assert response.status_code == 200
    ids = {s["id"] for s in response.json()}
    assert ids == {"AS001", "AS002"}


def test_list_account_statements_by_project_returns_404_when_project_missing(fake_uow):
    response = client.get("/api/account-statements/by-project/P999")

    assert response.status_code == 404


def test_register_payment_updates_amount_paid_and_remaining_amount(fake_uow):
    _crear_proyecto(fake_uow)
    client.post("/api/account-statements", json=_valid_account_statement_payload())

    response = client.patch(
        "/api/account-statements/AS001/payment", json={"amount_paid": 12000.0}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["amount_paid"] == 12000.0
    assert body["remaining_amount"] == 3000.0


def test_register_payment_returns_404_when_statement_missing(fake_uow):
    response = client.patch(
        "/api/account-statements/AS999/payment", json={"amount_paid": 1000.0}
    )

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Solicitudes Quincenales (BiweeklyRequest)
# ---------------------------------------------------------------------------

def test_create_biweekly_request_returns_201_and_persists_it(fake_uow):
    _crear_proyecto(fake_uow)

    response = client.post(
        "/api/biweekly-requests", json=_valid_biweekly_request_payload()
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == "BR001"
    assert body["status"] == "Pendiente"


def test_create_biweekly_request_returns_404_when_project_missing(fake_uow):
    response = client.post(
        "/api/biweekly-requests", json=_valid_biweekly_request_payload()
    )

    assert response.status_code == 404


def test_create_biweekly_request_rejects_negative_amount_with_422(fake_uow):
    _crear_proyecto(fake_uow)

    response = client.post(
        "/api/biweekly-requests",
        json=_valid_biweekly_request_payload(amount=-50.0),
    )

    assert response.status_code == 422


def test_get_biweekly_request_returns_existing_request(fake_uow):
    _crear_proyecto(fake_uow)
    client.post("/api/biweekly-requests", json=_valid_biweekly_request_payload())

    response = client.get("/api/biweekly-requests/BR001")

    assert response.status_code == 200
    assert response.json()["amount"] == 3000.0


def test_get_biweekly_request_returns_404_when_missing(fake_uow):
    response = client.get("/api/biweekly-requests/BR999")

    assert response.status_code == 404


def test_list_biweekly_requests_by_project_returns_created_ones(fake_uow):
    _crear_proyecto(fake_uow)
    client.post("/api/biweekly-requests", json=_valid_biweekly_request_payload())
    client.post(
        "/api/biweekly-requests",
        json=_valid_biweekly_request_payload(id="BR002", date="2026-03-01"),
    )

    response = client.get("/api/biweekly-requests/by-project/P001")

    assert response.status_code == 200
    ids = {r["id"] for r in response.json()}
    assert ids == {"BR001", "BR002"}


def test_list_biweekly_requests_by_project_returns_404_when_project_missing(fake_uow):
    response = client.get("/api/biweekly-requests/by-project/P999")

    assert response.status_code == 404


def test_update_biweekly_request_status_to_aprobada(fake_uow):
    _crear_proyecto(fake_uow)
    client.post("/api/biweekly-requests", json=_valid_biweekly_request_payload())

    response = client.patch(
        "/api/biweekly-requests/BR001/status", json={"status": "Aprobada"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Aprobada"


def test_update_biweekly_request_status_returns_404_when_missing(fake_uow):
    response = client.patch(
        "/api/biweekly-requests/BR999/status", json={"status": "Aprobada"}
    )

    assert response.status_code == 404


def test_update_biweekly_request_status_rejects_invalid_value_with_422(fake_uow):
    _crear_proyecto(fake_uow)
    client.post("/api/biweekly-requests", json=_valid_biweekly_request_payload())

    response = client.patch(
        "/api/biweekly-requests/BR001/status", json={"status": "EnProceso"}
    )

    assert response.status_code == 422
