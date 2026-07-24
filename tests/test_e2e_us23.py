"""tests/test_e2e_us23.py  (US-23)

Suite completa de tests End-to-End sobre la API de Soldaduras De Sedas.

A diferencia de los tests de entrypoints previos (que sustituyen el Unit of Work
por un ``FakeUnitOfWork`` en memoria), esta suite ejercita la aplicación completa
usando el ``TestClient`` de FastAPI contra una base de datos **SQLite en memoria**
y el ``SqlAlchemyUnitOfWork`` real. De esta forma se valida el comportamiento
desde el endpoint HTTP -> esquemas Pydantic -> service layer -> repositorios
SQLAlchemy -> base de datos, incluyendo el round-trip real de persistencia entre
requests (Architecture Patterns with Python, Cap. 4 "First End-to-End Test" y
Cap. 5 "TDD in High Gear and Low Gear").

Cada test corre sobre una base de datos limpia y aislada (fixture ``client``).
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import clear_mappers, sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.adapters import orm
from app.adapters.unit_of_work import SqlAlchemyUnitOfWork
from app.entrypoints.dependencies import get_unit_of_work
from app.entrypoints.main import app as real_app


# ---------------------------------------------------------------------------
# Infraestructura de test: SQLite en memoria + UoW real
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """TestClient conectado a una BD SQLite en memoria con el UoW real.

    Se usa ``StaticPool`` para que todas las sesiones creadas por el UoW
    compartan la misma conexión (y por lo tanto la misma BD en memoria);
    de lo contrario cada nueva conexión SQLite ``:memory:`` obtendría una
    base vacía y no habría persistencia entre requests.
    """
    # Estado limpio de mappers, por si un test previo los dejó registrados.
    clear_mappers()

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    orm.start_mappers()
    orm.mapper_registry.metadata.create_all(engine)

    session_factory = sessionmaker(bind=engine)

    real_app.dependency_overrides[get_unit_of_work] = (
        lambda: SqlAlchemyUnitOfWork(session_factory)
    )

    with TestClient(real_app) as test_client:
        yield test_client

    real_app.dependency_overrides.pop(get_unit_of_work, None)
    clear_mappers()
    engine.dispose()


# ---------------------------------------------------------------------------
# Payloads de ejemplo (helpers)
# ---------------------------------------------------------------------------

def _client_payload(**overrides):
    payload = dict(
        client_id="C001",
        client_company_name="Constructora Sedas",
        client_phone="555-1000",
        registration_date="2026-01-10",
        client_email="contacto@sedas.com",
    )
    payload.update(overrides)
    return payload


def _quote_payload(**overrides):
    payload = dict(
        quote_id="Q001",
        client_id="C001",
        quote_issue_date="2026-01-15",
        quote_job_description="Estructura metálica para bodega",
        quote_estimated_amount=15000.0,
        notes="Incluye materiales",
    )
    payload.update(overrides)
    return payload


def _project_payload(**overrides):
    payload = dict(
        project_id="P001",
        quote_id="Q001",
        project_name="Techo Bodega Norte",
        project_location="Zona 12",
        project_start_date="2026-02-01",
        project_estimated_end_date="2026-04-01",
    )
    payload.update(overrides)
    return payload


def _worker_payload(**overrides):
    payload = dict(
        worker_id="W001",
        worker_name="Juan Pérez",
        worker_role="Soldador",
        worker_base_rate=12.5,
    )
    payload.update(overrides)
    return payload


def _account_statement_payload(**overrides):
    payload = dict(
        id="AS001",
        project_id="P001",
        date="2026-02-15",
        initial_budget=15000.0,
        amount_paid=5000.0,
    )
    payload.update(overrides)
    return payload


def _biweekly_request_payload(**overrides):
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
# Seeders reutilizables (a través de la API real -> BD real)
# ---------------------------------------------------------------------------

def _seed_client(client, **overrides):
    resp = client.post("/api/clients", json=_client_payload(**overrides))
    assert resp.status_code == 201, resp.text
    return resp.json()


def _seed_approved_quote(client, **overrides):
    resp = client.post("/api/quotes", json=_quote_payload(**overrides))
    assert resp.status_code == 201, resp.text
    quote_id = resp.json()["quote_id"]
    approved = client.post(f"/api/quotes/{quote_id}/approve")
    assert approved.status_code == 200, approved.text
    return approved.json()


def _seed_project(client, **overrides):
    resp = client.post("/api/projects", json=_project_payload(**overrides))
    assert resp.status_code == 201, resp.text
    return resp.json()


def _seed_project_chain(client):
    """Crea cliente -> cotización aprobada -> proyecto y devuelve el proyecto."""
    _seed_client(client)
    _seed_approved_quote(client)
    return _seed_project(client)


def _seed_worker(client, **overrides):
    resp = client.post("/api/workers", json=_worker_payload(**overrides))
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Health / root
# ---------------------------------------------------------------------------

def test_root_returns_ok_message(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Soldadura de Sedas API OK"}


def test_health_check_returns_ok(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Clientes (US-15)
# ---------------------------------------------------------------------------

def test_create_client_returns_201_and_persists_to_db(client):
    response = client.post("/api/clients", json=_client_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["client_id"] == "C001"
    assert body["client_company_name"] == "Constructora Sedas"


def test_created_client_is_retrievable_in_a_later_request(client):
    _seed_client(client)

    response = client.get("/api/clients/C001")

    assert response.status_code == 200
    assert response.json()["client_email"] == "contacto@sedas.com"


def test_get_client_returns_404_when_missing(client):
    response = client.get("/api/clients/C999")

    assert response.status_code == 404


def test_list_clients_returns_all_created(client):
    _seed_client(client, client_id="C001")
    _seed_client(client, client_id="C002", client_company_name="Otra Empresa")

    response = client.get("/api/clients")

    assert response.status_code == 200
    ids = {c["client_id"] for c in response.json()}
    assert ids == {"C001", "C002"}


def test_update_client_persists_new_values(client):
    _seed_client(client)

    response = client.put(
        "/api/clients/C001",
        json={
            "client_company_name": "Constructora Sedas S.A.",
            "client_phone": "555-2000",
            "registration_date": "2026-01-10",
            "client_email": "nuevo@sedas.com",
        },
    )

    assert response.status_code == 200
    assert response.json()["client_company_name"] == "Constructora Sedas S.A."

    # El cambio quedó persistido en la BD.
    refetched = client.get("/api/clients/C001")
    assert refetched.json()["client_phone"] == "555-2000"


def test_update_client_returns_404_when_missing(client):
    response = client.put(
        "/api/clients/C999",
        json={
            "client_company_name": "Fantasma",
            "client_phone": "555-0000",
            "registration_date": "2026-01-10",
            "client_email": None,
        },
    )

    assert response.status_code == 404


def test_create_client_rejects_invalid_email_with_422(client):
    response = client.post(
        "/api/clients", json=_client_payload(client_email="no-es-un-email")
    )

    assert response.status_code == 422


def test_create_client_rejects_empty_company_name_with_422(client):
    response = client.post(
        "/api/clients", json=_client_payload(client_company_name="")
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Cotizaciones (US-16)
# ---------------------------------------------------------------------------

def test_create_quote_returns_201_with_initial_status_pendiente(client):
    _seed_client(client)

    response = client.post("/api/quotes", json=_quote_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["quote_id"] == "Q001"
    assert body["quote_status"] == "Pendiente"


def test_create_quote_returns_404_when_client_missing(client):
    response = client.post("/api/quotes", json=_quote_payload())

    assert response.status_code == 404


def test_create_quote_rejects_negative_amount_with_422(client):
    _seed_client(client)

    response = client.post(
        "/api/quotes", json=_quote_payload(quote_estimated_amount=-1.0)
    )

    assert response.status_code == 422


def test_get_quote_returns_existing_quote(client):
    _seed_client(client)
    client.post("/api/quotes", json=_quote_payload())

    response = client.get("/api/quotes/Q001")

    assert response.status_code == 200
    assert response.json()["quote_estimated_amount"] == 15000.0


def test_get_quote_returns_404_when_missing(client):
    response = client.get("/api/quotes/Q999")

    assert response.status_code == 404


def test_list_quotes_by_client_returns_created_ones(client):
    _seed_client(client)
    client.post("/api/quotes", json=_quote_payload(quote_id="Q001"))
    client.post("/api/quotes", json=_quote_payload(quote_id="Q002"))

    response = client.get("/api/quotes/by-client/C001")

    assert response.status_code == 200
    ids = {q["quote_id"] for q in response.json()}
    assert ids == {"Q001", "Q002"}


def test_approve_quote_sets_status_aprobado(client):
    _seed_client(client)
    client.post("/api/quotes", json=_quote_payload())

    response = client.post("/api/quotes/Q001/approve")

    assert response.status_code == 200
    assert response.json()["quote_status"] == "Aprobado"


def test_reject_quote_sets_status_rechazado(client):
    _seed_client(client)
    client.post("/api/quotes", json=_quote_payload())

    response = client.post("/api/quotes/Q001/reject")

    assert response.status_code == 200
    assert response.json()["quote_status"] == "Rechazado"


def test_update_quote_status_rejects_invalid_value_with_422(client):
    _seed_client(client)
    client.post("/api/quotes", json=_quote_payload())

    response = client.patch(
        "/api/quotes/Q001/status", json={"quote_status": "EnRevision"}
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Proyectos (US-17)
# ---------------------------------------------------------------------------

def test_create_project_from_approved_quote_returns_201(client):
    _seed_client(client)
    _seed_approved_quote(client)

    response = client.post("/api/projects", json=_project_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == "P001"
    # client_id y costo se derivan de la cotización.
    assert body["client_id"] == "C001"
    assert body["project_total_cost"] == 15000.0
    assert body["project_status"] == "In Progress"


def test_create_project_returns_409_when_quote_not_approved(client):
    _seed_client(client)
    client.post("/api/quotes", json=_quote_payload())  # queda "Pendiente"

    response = client.post("/api/projects", json=_project_payload())

    assert response.status_code == 409


def test_create_project_returns_404_when_quote_missing(client):
    response = client.post("/api/projects", json=_project_payload())

    assert response.status_code == 404


def test_get_project_returns_existing_project(client):
    _seed_project_chain(client)

    response = client.get("/api/projects/P001")

    assert response.status_code == 200
    assert response.json()["project_name"] == "Techo Bodega Norte"


def test_get_project_returns_404_when_missing(client):
    response = client.get("/api/projects/P999")

    assert response.status_code == 404


def test_list_projects_by_client_returns_created_ones(client):
    _seed_project_chain(client)

    response = client.get("/api/projects/by-client/C001")

    assert response.status_code == 200
    ids = {p["project_id"] for p in response.json()}
    assert ids == {"P001"}


def test_update_project_status_to_completed(client):
    _seed_project_chain(client)

    response = client.patch(
        "/api/projects/P001/status", json={"project_status": "Completed"}
    )

    assert response.status_code == 200
    assert response.json()["project_status"] == "Completed"

    refetched = client.get("/api/projects/P001")
    assert refetched.json()["project_status"] == "Completed"


# ---------------------------------------------------------------------------
# Trabajadores y asignaciones (US-18)
# ---------------------------------------------------------------------------

def test_create_worker_returns_201_and_persists(client):
    response = client.post("/api/workers", json=_worker_payload())

    assert response.status_code == 201
    assert response.json()["worker_id"] == "W001"


def test_get_worker_returns_existing_worker(client):
    _seed_worker(client)

    response = client.get("/api/workers/W001")

    assert response.status_code == 200
    assert response.json()["worker_role"] == "Soldador"


def test_get_worker_returns_404_when_missing(client):
    response = client.get("/api/workers/W999")

    assert response.status_code == 404


def test_list_workers_returns_all_created(client):
    _seed_worker(client, worker_id="W001")
    _seed_worker(client, worker_id="W002", worker_name="Ana Gómez")

    response = client.get("/api/workers")

    assert response.status_code == 200
    ids = {w["worker_id"] for w in response.json()}
    assert ids == {"W001", "W002"}


def test_assign_worker_to_project_returns_201(client):
    _seed_project_chain(client)
    _seed_worker(client)

    response = client.post(
        "/api/workers/W001/assignments",
        json={
            "assignment_id": "A001",
            "project_id": "P001",
            "assignment_date": "2026-02-05",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["assignment_id"] == "A001"
    assert body["worker_id"] == "W001"
    assert body["project_id"] == "P001"


def test_assign_worker_returns_404_when_worker_missing(client):
    _seed_project_chain(client)

    response = client.post(
        "/api/workers/W999/assignments",
        json={
            "assignment_id": "A001",
            "project_id": "P001",
            "assignment_date": "2026-02-05",
        },
    )

    assert response.status_code == 404


def test_assign_worker_returns_404_when_project_missing(client):
    _seed_worker(client)

    response = client.post(
        "/api/workers/W001/assignments",
        json={
            "assignment_id": "A001",
            "project_id": "P999",
            "assignment_date": "2026-02-05",
        },
    )

    assert response.status_code == 404


def test_list_assignments_by_worker_and_by_project(client):
    _seed_project_chain(client)
    _seed_worker(client)
    client.post(
        "/api/workers/W001/assignments",
        json={
            "assignment_id": "A001",
            "project_id": "P001",
            "assignment_date": "2026-02-05",
        },
    )

    by_worker = client.get("/api/workers/W001/assignments")
    by_project = client.get("/api/projects/P001/assignments")

    assert by_worker.status_code == 200
    assert by_project.status_code == 200
    assert {a["assignment_id"] for a in by_worker.json()} == {"A001"}
    assert {a["assignment_id"] for a in by_project.json()} == {"A001"}


# ---------------------------------------------------------------------------
# Estados de Cuenta (US-22)
# ---------------------------------------------------------------------------

def test_create_account_statement_computes_remaining_amount(client):
    _seed_project_chain(client)

    response = client.post(
        "/api/account-statements", json=_account_statement_payload()
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == "AS001"
    assert body["remaining_amount"] == 10000.0


def test_create_account_statement_returns_404_when_project_missing(client):
    response = client.post(
        "/api/account-statements", json=_account_statement_payload()
    )

    assert response.status_code == 404


def test_create_account_statement_rejects_negative_amount_paid_with_422(client):
    _seed_project_chain(client)

    response = client.post(
        "/api/account-statements",
        json=_account_statement_payload(amount_paid=-100.0),
    )

    assert response.status_code == 422


def test_get_account_statement_returns_persisted_statement(client):
    _seed_project_chain(client)
    client.post("/api/account-statements", json=_account_statement_payload())

    response = client.get("/api/account-statements/AS001")

    assert response.status_code == 200
    assert response.json()["initial_budget"] == 15000.0


def test_get_account_statement_returns_404_when_missing(client):
    response = client.get("/api/account-statements/AS999")

    assert response.status_code == 404


def test_list_account_statements_by_project(client):
    _seed_project_chain(client)
    client.post("/api/account-statements", json=_account_statement_payload())
    client.post(
        "/api/account-statements",
        json=_account_statement_payload(id="AS002", date="2026-03-01"),
    )

    response = client.get("/api/account-statements/by-project/P001")

    assert response.status_code == 200
    ids = {s["id"] for s in response.json()}
    assert ids == {"AS001", "AS002"}


def test_list_account_statements_by_project_returns_404_when_project_missing(client):
    response = client.get("/api/account-statements/by-project/P999")

    assert response.status_code == 404


def test_register_payment_updates_remaining_amount_and_persists(client):
    _seed_project_chain(client)
    client.post("/api/account-statements", json=_account_statement_payload())

    response = client.patch(
        "/api/account-statements/AS001/payment", json={"amount_paid": 12000.0}
    )

    assert response.status_code == 200
    assert response.json()["remaining_amount"] == 3000.0

    refetched = client.get("/api/account-statements/AS001")
    assert refetched.json()["amount_paid"] == 12000.0


def test_register_payment_returns_404_when_statement_missing(client):
    response = client.patch(
        "/api/account-statements/AS999/payment", json={"amount_paid": 1000.0}
    )

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Solicitudes Quincenales (US-22)
# ---------------------------------------------------------------------------

def test_create_biweekly_request_returns_201_and_persists(client):
    _seed_project_chain(client)

    response = client.post(
        "/api/biweekly-requests", json=_biweekly_request_payload()
    )

    assert response.status_code == 201
    assert response.json()["status"] == "Pendiente"


def test_create_biweekly_request_returns_404_when_project_missing(client):
    response = client.post(
        "/api/biweekly-requests", json=_biweekly_request_payload()
    )

    assert response.status_code == 404


def test_create_biweekly_request_rejects_negative_amount_with_422(client):
    _seed_project_chain(client)

    response = client.post(
        "/api/biweekly-requests",
        json=_biweekly_request_payload(amount=-50.0),
    )

    assert response.status_code == 422


def test_get_biweekly_request_returns_persisted_request(client):
    _seed_project_chain(client)
    client.post("/api/biweekly-requests", json=_biweekly_request_payload())

    response = client.get("/api/biweekly-requests/BR001")

    assert response.status_code == 200
    assert response.json()["amount"] == 3000.0


def test_get_biweekly_request_returns_404_when_missing(client):
    response = client.get("/api/biweekly-requests/BR999")

    assert response.status_code == 404


def test_list_biweekly_requests_by_project(client):
    _seed_project_chain(client)
    client.post("/api/biweekly-requests", json=_biweekly_request_payload())
    client.post(
        "/api/biweekly-requests",
        json=_biweekly_request_payload(id="BR002", date="2026-03-01"),
    )

    response = client.get("/api/biweekly-requests/by-project/P001")

    assert response.status_code == 200
    ids = {r["id"] for r in response.json()}
    assert ids == {"BR001", "BR002"}


def test_update_biweekly_request_status_to_aprobada_and_persists(client):
    _seed_project_chain(client)
    client.post("/api/biweekly-requests", json=_biweekly_request_payload())

    response = client.patch(
        "/api/biweekly-requests/BR001/status", json={"status": "Aprobada"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Aprobada"

    refetched = client.get("/api/biweekly-requests/BR001")
    assert refetched.json()["status"] == "Aprobada"


def test_update_biweekly_request_status_returns_404_when_missing(client):
    response = client.patch(
        "/api/biweekly-requests/BR999/status", json={"status": "Aprobada"}
    )

    assert response.status_code == 404


def test_update_biweekly_request_status_rejects_invalid_value_with_422(client):
    _seed_project_chain(client)
    client.post("/api/biweekly-requests", json=_biweekly_request_payload())

    response = client.patch(
        "/api/biweekly-requests/BR001/status", json={"status": "EnProceso"}
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Flujo de negocio completo End-to-End
# ---------------------------------------------------------------------------

def test_full_business_flow_from_client_to_payment(client):
    """Recorre el flujo crítico completo del negocio validando la persistencia
    real en la BD SQLite entre cada paso:

    cliente -> cotización -> aprobación -> proyecto -> trabajador ->
    asignación -> estado de cuenta -> pago -> solicitud quincenal.
    """
    # 1. Cliente
    assert client.post("/api/clients", json=_client_payload()).status_code == 201

    # 2. Cotización (Pendiente) y aprobación
    assert client.post("/api/quotes", json=_quote_payload()).status_code == 201
    approve = client.post("/api/quotes/Q001/approve")
    assert approve.status_code == 200
    assert approve.json()["quote_status"] == "Aprobado"

    # 3. Proyecto derivado de la cotización aprobada
    project = client.post("/api/projects", json=_project_payload())
    assert project.status_code == 201
    assert project.json()["project_total_cost"] == 15000.0

    # 4. Trabajador y asignación al proyecto
    assert client.post("/api/workers", json=_worker_payload()).status_code == 201
    assignment = client.post(
        "/api/workers/W001/assignments",
        json={
            "assignment_id": "A001",
            "project_id": "P001",
            "assignment_date": "2026-02-05",
        },
    )
    assert assignment.status_code == 201

    # 5. Estado de cuenta del proyecto y registro de un pago
    assert (
        client.post(
            "/api/account-statements", json=_account_statement_payload()
        ).status_code
        == 201
    )
    payment = client.patch(
        "/api/account-statements/AS001/payment", json={"amount_paid": 15000.0}
    )
    assert payment.status_code == 200
    assert payment.json()["remaining_amount"] == 0.0

    # 6. Solicitud quincenal aprobada
    assert (
        client.post(
            "/api/biweekly-requests", json=_biweekly_request_payload()
        ).status_code
        == 201
    )
    status_update = client.patch(
        "/api/biweekly-requests/BR001/status", json={"status": "Aprobada"}
    )
    assert status_update.status_code == 200

    # 7. Verificación final: todo quedó persistido y es consultable.
    assert client.get("/api/clients/C001").status_code == 200
    assert client.get("/api/projects/P001").json()["project_id"] == "P001"
    assert {a["assignment_id"] for a in client.get(
        "/api/projects/P001/assignments"
    ).json()} == {"A001"}
    assert client.get("/api/account-statements/AS001").json()["amount_paid"] == 15000.0
    assert client.get("/api/biweekly-requests/BR001").json()["status"] == "Aprobada"
