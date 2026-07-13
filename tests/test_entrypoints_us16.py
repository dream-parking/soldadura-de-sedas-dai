import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.adapters.unit_of_work import FakeUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.main import app as real_app
from app.domain.models import Client

client = TestClient(real_app)


@pytest.fixture
def fake_uow():
    """Sustituye el Unit of Work real por uno en memoria durante el test."""
    uow = FakeUnitOfWork()
    real_app.dependency_overrides[get_unit_of_work] = lambda: uow
    yield uow
    real_app.dependency_overrides.pop(get_unit_of_work, None)


def _crear_cliente(uow, client_id="C001"):
    """Helper: inserta un cliente directamente en el repo fake, sin pasar por la API."""
    uow.clients.add(
        Client(
            client_id=client_id,
            client_company_name="Constructora Acme",
            client_phone="7777-7777",
            registration_date=date(2026, 1, 1),
        )
    )


def _valid_payload(**overrides):
    payload = dict(
        quote_id="Q001",
        client_id="C001",
        quote_issue_date="2026-01-05",
        quote_job_description="Techo de bodega",
        quote_estimated_amount=15000.0,
        notes="Primera visita realizada",
    )
    payload.update(overrides)
    return payload


def test_create_quote_returns_201_with_status_pendiente(fake_uow):
    _crear_cliente(fake_uow)

    response = client.post("/api/quotes", json=_valid_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["quote_id"] == "Q001"
    assert body["quote_status"] == "Pendiente"
    assert fake_uow.committed is True


def test_create_quote_returns_404_when_client_missing(fake_uow):
    response = client.post("/api/quotes", json=_valid_payload())

    assert response.status_code == 404


def test_create_quote_ignores_status_field_in_payload(fake_uow):
    """quote_status no es un campo aceptado en QuoteCreate; el estado inicial
    siempre lo asigna el servidor como 'Pendiente'."""
    _crear_cliente(fake_uow)

    response = client.post(
        "/api/quotes", json=_valid_payload(quote_status="Aprobado")
    )

    assert response.status_code == 201
    assert response.json()["quote_status"] == "Pendiente"


def test_get_quote_returns_existing_quote(fake_uow):
    _crear_cliente(fake_uow)
    client.post("/api/quotes", json=_valid_payload())

    response = client.get("/api/quotes/Q001")

    assert response.status_code == 200
    assert response.json()["quote_job_description"] == "Techo de bodega"


def test_get_quote_returns_404_when_missing(fake_uow):
    response = client.get("/api/quotes/Q999")

    assert response.status_code == 404


def test_list_quotes_by_client_returns_only_that_clients_quotes(fake_uow):
    _crear_cliente(fake_uow, "C001")
    _crear_cliente(fake_uow, "C002")
    client.post("/api/quotes", json=_valid_payload(quote_id="Q001", client_id="C001"))
    client.post("/api/quotes", json=_valid_payload(quote_id="Q002", client_id="C002"))

    response = client.get("/api/quotes/by-client/C001")

    assert response.status_code == 200
    quote_ids = [q["quote_id"] for q in response.json()]
    assert quote_ids == ["Q001"]


def test_list_quotes_by_client_returns_404_when_client_missing(fake_uow):
    response = client.get("/api/quotes/by-client/C999")

    assert response.status_code == 404


def test_update_quote_status_changes_status(fake_uow):
    _crear_cliente(fake_uow)
    client.post("/api/quotes", json=_valid_payload())

    response = client.patch("/api/quotes/Q001/status", json={"quote_status": "Rechazado"})

    assert response.status_code == 200
    assert response.json()["quote_status"] == "Rechazado"


def test_update_quote_status_rejects_invalid_status_with_422(fake_uow):
    _crear_cliente(fake_uow)
    client.post("/api/quotes", json=_valid_payload())

    response = client.patch("/api/quotes/Q001/status", json={"quote_status": "Cancelada"})

    assert response.status_code == 422


def test_approve_quote_sets_status_aprobado(fake_uow):
    _crear_cliente(fake_uow)
    client.post("/api/quotes", json=_valid_payload())

    response = client.post("/api/quotes/Q001/approve")

    assert response.status_code == 200
    assert response.json()["quote_status"] == "Aprobado"


def test_reject_quote_sets_status_rechazado(fake_uow):
    _crear_cliente(fake_uow)
    client.post("/api/quotes", json=_valid_payload())

    response = client.post("/api/quotes/Q001/reject")

    assert response.status_code == 200
    assert response.json()["quote_status"] == "Rechazado"


def test_approve_quote_returns_404_when_missing(fake_uow):
    response = client.post("/api/quotes/Q999/approve")

    assert response.status_code == 404