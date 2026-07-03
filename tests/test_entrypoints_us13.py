import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.entrypoints.errors import register_exception_handlers
from app.entrypoints.main import app as real_app
from app.service_layer.exceptions import (
    WorkerNotFound,
    ProjectNotFound,
    MaterialNotFound,
    WorkerNotAssignedToProject,
)

client = TestClient(real_app)


def test_root_endpoint_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Soldadura de Sedas API OK"}


def test_health_endpoint_under_api_router():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_headers_present_for_allowed_origin():
    response = client.get("/api/health", headers={"Origin": "http://localhost:3000"})
    assert response.headers.get("access-control-allow-origin") == "*"


@pytest.fixture
def error_app():
    """App aislada para probar el mapeo de excepciones sin depender de endpoints reales."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom/worker-not-found")
    def worker_not_found():
        raise WorkerNotFound("no existe")

    @app.get("/boom/project-not-found")
    def project_not_found():
        raise ProjectNotFound("no existe")

    @app.get("/boom/material-not-found")
    def material_not_found():
        raise MaterialNotFound("no existe")

    @app.get("/boom/worker-not-assigned")
    def worker_not_assigned():
        raise WorkerNotAssignedToProject("no asignado")

    @app.get("/boom/value-error")
    def value_error():
        raise ValueError("regla de negocio violada")

    @app.get("/boom/unexpected")
    def unexpected():
        raise RuntimeError("algo inesperado")

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.parametrize(
    "path, expected_status",
    [
        ("/boom/worker-not-found", 404),
        ("/boom/project-not-found", 404),
        ("/boom/material-not-found", 404),
        ("/boom/worker-not-assigned", 409),
        ("/boom/value-error", 400),
        ("/boom/unexpected", 500),
    ],
)
def test_domain_exceptions_map_to_http_status(error_app, path, expected_status):
    response = error_app.get(path)
    assert response.status_code == expected_status
    assert "detail" in response.json()
