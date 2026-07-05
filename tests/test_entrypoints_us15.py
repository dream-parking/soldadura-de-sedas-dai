import pytest
from fastapi.testclient import TestClient

from app.adapters.unit_of_work import FakeUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.main import app as real_app

client = TestClient(real_app)


@pytest.fixture
def fake_uow():
    """Sustituye el Unit of Work real por uno en memoria durante el test."""
    uow = FakeUnitOfWork()
    real_app.dependency_overrides[get_unit_of_work] = lambda: uow
    yield uow
    real_app.dependency_overrides.pop(get_unit_of_work, None)


def _valid_payload(**overrides):
    payload = dict(
        client_id="C001",
        client_company_name="Soldaduras de Sedas",
        client_phone="555-1234",
        registration_date="2026-01-01",
        client_email="contacto@sedas.com",
    )
    payload.update(overrides)
    return payload


def test_create_client_returns_201_and_persists_it(fake_uow):
    response = client.post("/api/clients", json=_valid_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["client_id"] == "C001"
    assert body["client_company_name"] == "Soldaduras de Sedas"
    assert fake_uow.clients.get("C001") is not None
    assert fake_uow.committed is True


def test_create_client_rejects_invalid_email_with_422(fake_uow):
    response = client.post("/api/clients", json=_valid_payload(client_email="no-es-un-email"))

    assert response.status_code == 422
    assert fake_uow.clients.get("C001") is None


def test_create_client_rejects_missing_required_field_with_422(fake_uow):
    payload = _valid_payload()
    del payload["client_phone"]

    response = client.post("/api/clients", json=payload)

    assert response.status_code == 422


def test_get_client_returns_existing_client(fake_uow):
    client.post("/api/clients", json=_valid_payload())

    response = client.get("/api/clients/C001")

    assert response.status_code == 200
    assert response.json()["client_company_name"] == "Soldaduras de Sedas"


def test_get_client_returns_404_when_missing(fake_uow):
    response = client.get("/api/clients/C999")

    assert response.status_code == 404
    assert "detail" in response.json()


def test_list_clients_returns_all_created(fake_uow):
    client.post("/api/clients", json=_valid_payload())
    client.post("/api/clients", json=_valid_payload(client_id="C002", client_email=None))

    response = client.get("/api/clients")

    assert response.status_code == 200
    ids = {c["client_id"] for c in response.json()}
    assert ids == {"C001", "C002"}


def test_list_clients_returns_empty_list_when_none_exist(fake_uow):
    response = client.get("/api/clients")

    assert response.status_code == 200
    assert response.json() == []


def test_update_client_returns_200_with_updated_fields(fake_uow):
    client.post("/api/clients", json=_valid_payload())

    response = client.put(
        "/api/clients/C001",
        json={
            "client_company_name": "Soldaduras de Sedas S.A.",
            "client_phone": "555-0000",
            "registration_date": "2026-01-01",
            "client_email": "nuevo@sedas.com",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["client_company_name"] == "Soldaduras de Sedas S.A."
    assert body["client_phone"] == "555-0000"
    assert body["client_email"] == "nuevo@sedas.com"


def test_update_client_returns_404_when_missing(fake_uow):
    response = client.put(
        "/api/clients/C999",
        json={
            "client_company_name": "No existe",
            "client_phone": "555-0000",
            "registration_date": "2026-01-01",
        },
    )

    assert response.status_code == 404


def test_update_client_rejects_invalid_payload_with_422(fake_uow):
    client.post("/api/clients", json=_valid_payload())

    response = client.put(
        "/api/clients/C001",
        json={
            "client_company_name": "Soldaduras de Sedas",
            "client_phone": "555-0000",
            "registration_date": "no-es-una-fecha",
        },
    )

    assert response.status_code == 422
